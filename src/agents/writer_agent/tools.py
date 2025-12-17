"""Writer Agent 전용 도구"""

from typing import Optional
from datetime import datetime

from src.tools.cypher import CypherManager, GraphNode, GraphRelationship


class WriterTools:
    """Writer Agent가 사용하는 도구 모음"""

    def __init__(self):
        self._cypher_manager: Optional[CypherManager] = None

    def set_cypher_manager(self, manager: CypherManager):
        """CypherManager 설정 (Analyst Agent에서 전달받음)"""
        self._cypher_manager = manager

    def get_cypher_manager(self, output_file: str) -> CypherManager:
        """CypherManager 가져오기"""
        if self._cypher_manager is None:
            self._cypher_manager = CypherManager(output_file)
        return self._cypher_manager

    def create_thought_node(
        self,
        title: str,
        content: str,
        source_file: str,
        manager: CypherManager
    ) -> tuple[GraphNode, str]:
        """Thought 노드 생성"""
        return manager.create_thought_node(title, content, source_file)

    def create_concept_node(
        self,
        name: str,
        concept_type: str,
        manager: CypherManager
    ) -> tuple[GraphNode, str]:
        """Concept 노드 생성 (중복 체크)"""
        return manager.create_concept_node(name, concept_type)

    def create_category_node(
        self,
        name: str,
        manager: CypherManager
    ) -> tuple[GraphNode, str]:
        """Category 노드 생성"""
        return manager.create_category_node(name)

    def create_date_node(
        self,
        date_str: str,
        manager: CypherManager
    ) -> tuple[GraphNode, str]:
        """Date 노드 생성 (GRAPH_SCHEMA.md 스펙)"""
        return manager.create_date_node(date_str)

    def create_tag_node(
        self,
        name: str,
        manager: CypherManager
    ) -> tuple[GraphNode, str]:
        """Tag 노드 생성 (GRAPH_SCHEMA.md 스펙)"""
        return manager.create_tag_node(name)

    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        properties: dict,
        manager: CypherManager
    ) -> tuple[GraphRelationship, str]:
        """관계 생성"""
        return manager.create_relationship(
            source_id, target_id, rel_type, properties
        )

    def append_queries(
        self,
        queries: list[str],
        manager: CypherManager
    ):
        """쿼리 저장"""
        manager.append_queries(queries)

    def is_concept_exists(
        self,
        concept_name: str,
        existing_concepts: list[str]
    ) -> bool:
        """개념 존재 여부 확인"""
        concept_lower = concept_name.lower().strip()
        for existing in existing_concepts:
            if existing.lower().strip() == concept_lower:
                return True
        return False

    def get_today_date(self) -> str:
        """오늘 날짜 반환"""
        return datetime.now().strftime("%Y-%m-%d")
