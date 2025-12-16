"""Cypher 쿼리 관리"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class GraphNode:
    """그래프 노드

    지원 노드 타입: Thought, Category, Concept, Date, Tag
    """
    id: str
    label: str
    properties: dict = field(default_factory=dict)

    def to_cypher(self) -> str:
        """Cypher MERGE 쿼리 생성"""
        props = ", ".join(
            f'{k}: "{v}"' if isinstance(v, str) else f'{k}: {v}'
            for k, v in self.properties.items()
        )
        return f'MERGE (n:{self.label} {{id: "{self.id}", {props}}})'


@dataclass
class GraphRelationship:
    """그래프 관계

    지원 관계 타입:
    - BELONGS_TO: Thought → Category
    - MENTIONS: Thought → Concept
    - RELATED_TO: Concept ↔ Concept
    - CREATED_ON: Thought → Date
    - EVOLVED_TO: Concept → Concept
    - HAS_TAG: Thought → Tag
    """
    source_id: str
    target_id: str
    rel_type: str
    properties: dict = field(default_factory=dict)

    def to_cypher(self) -> str:
        """Cypher MERGE 쿼리 생성"""
        props = ""
        if self.properties:
            props_str = ", ".join(
                f'{k}: "{v}"' if isinstance(v, str) else f'{k}: {v}'
                for k, v in self.properties.items()
            )
            props = f" {{{props_str}}}"

        return (f'MATCH (a {{id: "{self.source_id}"}}), (b {{id: "{self.target_id}"}}) '
                f'MERGE (a)-[:{self.rel_type}{props}]->(b)')


@dataclass
class GraphState:
    """현재 그래프 상태"""
    nodes: dict[str, GraphNode] = field(default_factory=dict)
    relationships: list[GraphRelationship] = field(default_factory=list)

    def has_node(self, node_id: str) -> bool:
        """노드 존재 여부"""
        return node_id in self.nodes

    def has_concept(self, concept_name: str) -> bool:
        """개념 존재 여부 (이름으로 검색)"""
        for node in self.nodes.values():
            if node.label == "Concept" and node.properties.get("name") == concept_name:
                return True
        return False

    def get_concept_id(self, concept_name: str) -> Optional[str]:
        """개념 ID 찾기"""
        for node_id, node in self.nodes.items():
            if node.label == "Concept" and node.properties.get("name") == concept_name:
                return node_id
        return None

    def get_all_concepts(self) -> list[str]:
        """모든 개념 이름 목록"""
        return [
            node.properties.get("name", "")
            for node in self.nodes.values()
            if node.label == "Concept"
        ]

    def get_all_tags(self) -> list[str]:
        """모든 태그 이름 목록"""
        return [
            node.properties.get("name", "")
            for node in self.nodes.values()
            if node.label == "Tag"
        ]

    def add_node(self, node: GraphNode):
        """노드 추가"""
        self.nodes[node.id] = node

    def add_relationship(self, rel: GraphRelationship):
        """관계 추가"""
        self.relationships.append(rel)


class CypherManager:
    """Cypher 파일 관리"""

    def __init__(self, output_path: str = "data/output/graph.cypher"):
        self.output_path = Path(output_path)
        self.state = GraphState()

    def load_existing(self) -> GraphState:
        """기존 Cypher 파일에서 상태 로드"""
        if not self.output_path.exists():
            return self.state

        content = self.output_path.read_text(encoding='utf-8')
        self._parse_cypher(content)

        return self.state

    def _parse_cypher(self, content: str):
        """Cypher 쿼리 파싱하여 노드/관계 추출"""
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # MERGE (n:Label {id: "...", ...}) 패턴
            node_match = re.search(
                r'MERGE\s+\((\w+):(\w+)\s+\{([^}]+)\}\)',
                line, re.IGNORECASE
            )
            if node_match:
                var_name, label, props_str = node_match.groups()
                props = self._parse_properties(props_str)

                if 'id' in props:
                    node = GraphNode(
                        id=props['id'],
                        label=label,
                        properties={k: v for k, v in props.items() if k != 'id'}
                    )
                    self.state.add_node(node)
                continue

            # MATCH ... MERGE (a)-[:REL]->(b) 패턴
            rel_match = re.search(
                r'MATCH.*\{id:\s*"([^"]+)"\}.*\{id:\s*"([^"]+)"\}.*'
                r'MERGE.*\[:(\w+)(?:\s*\{([^}]*)\})?\]',
                line, re.IGNORECASE
            )
            if rel_match:
                source_id, target_id, rel_type = rel_match.groups()[:3]
                props_str = rel_match.groups()[3] if len(rel_match.groups()) > 3 else None

                rel = GraphRelationship(
                    source_id=source_id,
                    target_id=target_id,
                    rel_type=rel_type,
                    properties=self._parse_properties(props_str) if props_str else {}
                )
                self.state.add_relationship(rel)

    def _parse_properties(self, props_str: str) -> dict:
        """프로퍼티 문자열 파싱"""
        props = {}
        if not props_str:
            return props

        pattern = r'(\w+):\s*(?:"([^"]*)"|(\d+(?:\.\d+)?)|(\w+))'
        for match in re.finditer(pattern, props_str):
            key = match.group(1)
            value = match.group(2) or match.group(3) or match.group(4)

            if match.group(3):
                value = float(value) if '.' in value else int(value)

            props[key] = value

        return props

    def generate_node_id(self, label: str, name: str) -> str:
        """노드 ID 생성"""
        clean_name = re.sub(r'[^a-zA-Z0-9가-힣]', '_', name)[:30]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{label.lower()}_{clean_name}_{timestamp}"

    def append_queries(self, queries: list[str]):
        """쿼리들을 파일에 추가"""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"\n// === Added: {timestamp} ===\n"

        with open(self.output_path, 'a', encoding='utf-8') as f:
            f.write(header)
            for query in queries:
                f.write(query + '\n')

    def create_thought_node(
        self,
        title: str,
        content: str,
        source_file: str
    ) -> tuple[GraphNode, str]:
        """Thought 노드 생성"""
        node_id = self.generate_node_id("Thought", title)

        node = GraphNode(
            id=node_id,
            label="Thought",
            properties={
                "title": title,
                "content": content[:500],
                "source": source_file,
                "created_at": datetime.now().isoformat()
            }
        )

        return node, node.to_cypher()

    def create_concept_node(
        self,
        name: str,
        concept_type: str = "keyword"
    ) -> tuple[GraphNode, str]:
        """Concept 노드 생성 (중복 체크)"""
        existing_id = self.state.get_concept_id(name)
        if existing_id:
            return self.state.nodes[existing_id], ""

        node_id = self.generate_node_id("Concept", name)

        node = GraphNode(
            id=node_id,
            label="Concept",
            properties={
                "name": name,
                "type": concept_type
            }
        )

        return node, node.to_cypher()

    def create_category_node(self, name: str) -> tuple[GraphNode, str]:
        """Category 노드 생성"""
        node_id = f"category_{re.sub(r'[^a-zA-Z0-9가-힣]', '_', name)}"

        if self.state.has_node(node_id):
            return self.state.nodes[node_id], ""

        node = GraphNode(
            id=node_id,
            label="Category",
            properties={"name": name}
        )

        return node, node.to_cypher()

    def create_date_node(self, date_str: str) -> tuple[GraphNode, str]:
        """Date 노드 생성 (GRAPH_SCHEMA.md 스펙)"""
        node_id = f"date_{date_str.replace('-', '')}"

        if self.state.has_node(node_id):
            return self.state.nodes[node_id], ""

        node = GraphNode(
            id=node_id,
            label="Date",
            properties={"date": date_str}
        )

        return node, node.to_cypher()

    def create_tag_node(self, name: str) -> tuple[GraphNode, str]:
        """Tag 노드 생성 (GRAPH_SCHEMA.md 스펙)"""
        node_id = f"tag_{re.sub(r'[^a-zA-Z0-9가-힣]', '_', name.lower())}"

        if self.state.has_node(node_id):
            return self.state.nodes[node_id], ""

        node = GraphNode(
            id=node_id,
            label="Tag",
            properties={"name": name}
        )

        return node, node.to_cypher()

    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        properties: dict = None
    ) -> tuple[GraphRelationship, str]:
        """관계 생성"""
        rel = GraphRelationship(
            source_id=source_id,
            target_id=target_id,
            rel_type=rel_type,
            properties=properties or {}
        )

        return rel, rel.to_cypher()
