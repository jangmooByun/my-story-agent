"""Analyst Agent 전용 도구"""

from typing import Optional
from tools.cypher import CypherManager, GraphState


class AnalystTools:
    """Analyst Agent가 사용하는 도구 모음"""

    def __init__(self):
        self._cypher_manager: Optional[CypherManager] = None

    def load_existing_graph(self, output_file: str) -> dict:
        """기존 그래프 상태 로드

        Args:
            output_file: Cypher 파일 경로

        Returns:
            그래프 상태 정보
        """
        self._cypher_manager = CypherManager(output_file)
        graph_state = self._cypher_manager.load_existing()

        existing_concepts = graph_state.get_all_concepts()
        existing_tags = graph_state.get_all_tags()

        existing_nodes = {
            node_id: {
                "label": node.label,
                "properties": node.properties
            }
            for node_id, node in graph_state.nodes.items()
        }

        existing_relationships = [
            {
                "source": rel.source_id,
                "target": rel.target_id,
                "type": rel.rel_type,
                "properties": rel.properties
            }
            for rel in graph_state.relationships
        ]

        stats = {
            "total_nodes": len(graph_state.nodes),
            "total_relationships": len(graph_state.relationships),
            "concept_count": len(existing_concepts),
            "tag_count": len(existing_tags),
            "thought_count": sum(
                1 for n in graph_state.nodes.values()
                if n.label == "Thought"
            ),
            "category_count": sum(
                1 for n in graph_state.nodes.values()
                if n.label == "Category"
            ),
        }

        return {
            "concepts": existing_concepts,
            "tags": existing_tags,
            "nodes": existing_nodes,
            "relationships": existing_relationships,
            "stats": stats,
            "cypher_manager": self._cypher_manager
        }

    def find_similar_concepts(
        self,
        concept: str,
        existing_concepts: list[str],
        threshold: float = 0.7
    ) -> list[str]:
        """유사한 개념 찾기 (간단한 문자열 매칭)

        Args:
            concept: 찾을 개념
            existing_concepts: 기존 개념 목록
            threshold: 유사도 임계값

        Returns:
            유사한 개념 목록
        """
        similar = []
        concept_lower = concept.lower()

        for existing in existing_concepts:
            existing_lower = existing.lower()

            # 완전 일치
            if concept_lower == existing_lower:
                similar.append(existing)
                continue

            # 부분 일치
            if concept_lower in existing_lower or existing_lower in concept_lower:
                similar.append(existing)

        return similar

    def is_duplicate_concept(
        self,
        concept: str,
        existing_concepts: list[str]
    ) -> bool:
        """중복 개념인지 확인

        Args:
            concept: 확인할 개념
            existing_concepts: 기존 개념 목록

        Returns:
            중복 여부
        """
        concept_lower = concept.lower().strip()
        for existing in existing_concepts:
            if existing.lower().strip() == concept_lower:
                return True
        return False

    def suggest_category(
        self,
        concept: str,
        existing_categories: list[str]
    ) -> Optional[str]:
        """카테고리 제안 (키워드 기반)

        Args:
            concept: 개념
            existing_categories: 기존 카테고리 목록

        Returns:
            제안된 카테고리 또는 None
        """
        concept_lower = concept.lower()

        # 간단한 키워드 매핑
        category_keywords = {
            "프로그래밍": ["python", "java", "code", "함수", "클래스", "api"],
            "AI": ["llm", "gpt", "ai", "머신러닝", "딥러닝", "모델"],
            "데이터": ["데이터", "database", "sql", "분석", "통계"],
            "비즈니스": ["마케팅", "전략", "비즈니스", "매출", "고객"],
        }

        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in concept_lower:
                    return category

        return None
