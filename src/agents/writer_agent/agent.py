"""Writer Agent - Cypher 쿼리 생성 및 저장"""

from typing import Optional

from src.core.base_agent import BaseAgent
from src.tools.cypher import CypherManager
from src.agents.writer_agent.tools import WriterTools
from src.agents.writer_agent.prompts import PROMPTS


class WriterAgent(BaseAgent):
    """Writer Agent

    역할 (ARCHITECTURE.md 스펙):
    - Cypher 쿼리 생성
    - 중복 체크
    - 파일 저장

    그래프 스키마 (GRAPH_SCHEMA.md):
    - 노드: Thought, Category, Concept, Date, Tag
    - 관계: BELONGS_TO, MENTIONS, RELATED_TO, CREATED_ON, EVOLVED_TO, HAS_TAG

    사용법:
        agent = WriterAgent()
        result = agent.run({
            "output_file": "data/output/graph.cypher",
            "categorized_docs": [...],
            "relationships": [...],
            "existing_graph": {...},
            "metadata": {...}
        })
    """

    name = "writer_agent"
    description = "Cypher 쿼리를 생성하고 파일에 저장합니다"

    def __init__(self, model_name: Optional[str] = None):
        super().__init__(model_name=model_name)
        self.prompts = PROMPTS
        self.tools = WriterTools()

    def run(self, state: dict) -> dict:
        """에이전트 실행

        Args:
            state: {output_file, categorized_docs, relationships, existing_graph, metadata}

        Returns:
            {queries, result}
        """
        self.logger.info("=== Writer Agent 시작 ===")

        output_file = state.get("output_file", "data/output/graph.cypher")
        categorized_docs = state.get("categorized_docs", [])
        relationships = state.get("relationships", [])
        existing_graph = state.get("existing_graph", {})
        metadata = state.get("metadata", {})

        # CypherManager 가져오기
        cypher_manager = existing_graph.get("cypher_manager")
        if not cypher_manager:
            cypher_manager = self.tools.get_cypher_manager(output_file)

        existing_concepts = existing_graph.get("concepts", [])

        queries = []
        new_node_count = 0
        new_rel_count = 0

        # 1. 문서별 노드/관계 생성
        for doc in categorized_docs:
            doc_queries, nodes, rels = self._process_document(
                doc, existing_concepts, metadata, cypher_manager
            )
            queries.extend(doc_queries)
            new_node_count += nodes
            new_rel_count += rels

            # 기존 개념 목록 업데이트
            for concept in doc.get("analysis", {}).get("concepts", []):
                name = concept.get("name", "")
                if name and name not in existing_concepts:
                    existing_concepts.append(name)

        # 2. 분석된 관계 쿼리 생성
        rel_queries = self._process_relationships(
            relationships, cypher_manager
        )
        queries.extend(rel_queries)
        new_rel_count += len(rel_queries)

        # 3. 쿼리 저장
        if queries:
            self.tools.append_queries(queries, cypher_manager)
            self.logger.info(f"쿼리 저장 완료: {len(queries)}개")

        result = {
            "success": True,
            "output_file": str(cypher_manager.output_path),
            "processed_docs": len(categorized_docs),
            "new_nodes": new_node_count,
            "new_relationships": new_rel_count,
            "total_queries": len(queries)
        }

        self.logger.info(f"완료: {result}")

        return {
            "queries": queries,
            "result": result
        }

    def _process_document(
        self,
        doc: dict,
        existing_concepts: list[str],
        metadata: dict,
        manager: CypherManager
    ) -> tuple[list[str], int, int]:
        """단일 문서 처리"""
        queries = []
        node_count = 0
        rel_count = 0

        analysis = doc.get("analysis", {})

        # 1. Thought 노드
        thought_node, thought_query = self.tools.create_thought_node(
            title=doc.get("title", "Untitled"),
            content=doc.get("content", "")[:500],
            source_file=doc.get("file_name", ""),
            manager=manager
        )
        queries.append(thought_query)
        manager.state.add_node(thought_node)
        node_count += 1

        # 2. Category 노드 및 BELONGS_TO 관계
        category = doc.get("final_category", "")
        if category:
            cat_node, cat_query = self.tools.create_category_node(
                category, manager
            )
            if cat_query:
                queries.append(cat_query)
                manager.state.add_node(cat_node)
                node_count += 1

            _, rel_query = self.tools.create_relationship(
                thought_node.id, cat_node.id, "BELONGS_TO", {}, manager
            )
            queries.append(rel_query)
            rel_count += 1

        # 3. Date 노드 및 CREATED_ON 관계
        dates = metadata.get("dates", []) or doc.get("metadata", {}).get("dates", [])
        if dates:
            date_str = dates[0]  # 첫 번째 날짜 사용
            date_node, date_query = self.tools.create_date_node(date_str, manager)
            if date_query:
                queries.append(date_query)
                manager.state.add_node(date_node)
                node_count += 1

            _, rel_query = self.tools.create_relationship(
                thought_node.id, date_node.id, "CREATED_ON", {}, manager
            )
            queries.append(rel_query)
            rel_count += 1

        # 4. Tag 노드 및 HAS_TAG 관계
        tags = metadata.get("tags", []) or doc.get("metadata", {}).get("tags", [])
        for tag in tags[:5]:  # 최대 5개 태그
            tag_node, tag_query = self.tools.create_tag_node(tag, manager)
            if tag_query:
                queries.append(tag_query)
                manager.state.add_node(tag_node)
                node_count += 1

            _, rel_query = self.tools.create_relationship(
                thought_node.id, tag_node.id, "HAS_TAG", {}, manager
            )
            queries.append(rel_query)
            rel_count += 1

        # 5. Concept 노드 및 MENTIONS 관계
        for concept in analysis.get("concepts", []):
            concept_name = concept.get("name", "")
            if not concept_name:
                continue

            concept_type = concept.get("type", "keyword")
            is_new = not self.tools.is_concept_exists(
                concept_name, existing_concepts
            )

            concept_node, concept_query = self.tools.create_concept_node(
                concept_name, concept_type, manager
            )

            if concept_query and is_new:
                queries.append(concept_query)
                manager.state.add_node(concept_node)
                node_count += 1

            # MENTIONS 관계 (GRAPH_SCHEMA.md 스펙)
            _, rel_query = self.tools.create_relationship(
                thought_node.id, concept_node.id, "MENTIONS",
                {"confidence": concept.get("confidence", 0.8)},
                manager
            )
            queries.append(rel_query)
            rel_count += 1

        return queries, node_count, rel_count

    def _process_relationships(
        self,
        relationships: list[dict],
        manager: CypherManager
    ) -> list[str]:
        """분석된 관계 처리"""
        queries = []

        for rel in relationships:
            source = rel.get("source", "")
            target = rel.get("target", "")
            rel_type = rel.get("type", "RELATED_TO")

            if not source or not target:
                continue

            # 개념 ID 찾기
            source_id = manager.state.get_concept_id(source)
            target_id = manager.state.get_concept_id(target)

            if source_id and target_id:
                _, query = self.tools.create_relationship(
                    source_id, target_id, rel_type,
                    {"reason": rel.get("reason", "")},
                    manager
                )
                queries.append(query)

        return queries
