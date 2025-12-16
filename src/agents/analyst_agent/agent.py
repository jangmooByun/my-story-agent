"""Analyst Agent - 관계 분석 및 카테고리 분류"""

from typing import Optional

from core.base_agent import BaseAgent
from agents.analyst_agent.tools import AnalystTools
from agents.analyst_agent.prompts import PROMPTS


class AnalystAgent(BaseAgent):
    """Analyst Agent

    역할 (ARCHITECTURE.md 스펙):
    - 카테고리 분류
    - 개념 간 관계 분석 (RELATED_TO, MENTIONS 등)
    - 기존 그래프 상태와 비교

    사용법:
        agent = AnalystAgent()
        result = agent.run({
            "output_file": "data/output/graph.cypher",
            "parsed_docs": [...],
            "new_concepts": [...]
        })
    """

    name = "analyst_agent"
    description = "개념 간 관계를 분석하고 카테고리를 분류합니다"

    def __init__(self, model_name: Optional[str] = None):
        super().__init__(model_name=model_name)
        self.prompts = PROMPTS
        self.tools = AnalystTools()

    def run(self, state: dict) -> dict:
        """에이전트 실행

        Args:
            state: {output_file, parsed_docs, new_concepts, ...}

        Returns:
            {existing_graph, categorized_docs, relationships}
        """
        self.logger.info("=== Analyst Agent 시작 ===")

        # 1. 기존 그래프 상태 로드
        output_file = state.get("output_file", "data/output/graph.cypher")
        existing_graph = self.tools.load_existing_graph(output_file)

        self.logger.info(f"기존 그래프: {existing_graph['stats']}")

        # 2. 문서 카테고리 분류
        parsed_docs = state.get("parsed_docs", [])
        categorized_docs = self._categorize_documents(
            parsed_docs,
            existing_graph
        )

        # 3. 개념 간 관계 분석
        new_concepts = state.get("new_concepts", [])
        relationships = self._analyze_relationships(
            new_concepts,
            existing_graph
        )

        self.logger.info(
            f"분석 완료: {len(categorized_docs)}개 문서 분류, "
            f"{len(relationships)}개 관계 발견"
        )

        return {
            "existing_graph": existing_graph,
            "categorized_docs": categorized_docs,
            "relationships": relationships
        }

    def _categorize_documents(
        self,
        docs: list[dict],
        existing_graph: dict
    ) -> list[dict]:
        """문서별 카테고리 분류"""
        categorized = []

        # 기존 카테고리 추출
        existing_categories = [
            node["properties"].get("name", "")
            for node in existing_graph["nodes"].values()
            if node["label"] == "Category"
        ]

        for doc in docs:
            analysis = doc.get("analysis", {})
            suggested_category = analysis.get("category", "")

            # LLM으로 카테고리 확정
            if suggested_category:
                category = self._confirm_category(
                    doc, suggested_category, existing_categories
                )
            else:
                category = self._assign_category(doc, existing_categories)

            doc_with_category = {**doc, "final_category": category}
            categorized.append(doc_with_category)

            # 새 카테고리면 목록에 추가
            if category and category not in existing_categories:
                existing_categories.append(category)

        return categorized

    def _confirm_category(
        self,
        doc: dict,
        suggested: str,
        existing: list[str]
    ) -> str:
        """제안된 카테고리 확정"""
        # 기존 카테고리에 있으면 그대로 사용
        for cat in existing:
            if cat.lower() == suggested.lower():
                return cat

        # LLM으로 검증
        try:
            prompt = self.get_prompt(
                "categorization",
                title=doc.get("title", ""),
                summary=doc.get("analysis", {}).get("summary", ""),
                concepts=doc.get("analysis", {}).get("concepts", [])[:10],
                existing_categories=existing[:20]
            )

            result = self.invoke_llm_json(prompt)
            return result.get("category", suggested)

        except Exception as e:
            self.logger.warning(f"카테고리 확정 실패: {e}")
            return suggested

    def _assign_category(
        self,
        doc: dict,
        existing: list[str]
    ) -> str:
        """카테고리 할당"""
        try:
            prompt = self.get_prompt(
                "categorization",
                title=doc.get("title", ""),
                summary=doc.get("analysis", {}).get("summary", "")[:500],
                concepts=doc.get("analysis", {}).get("concepts", [])[:10],
                existing_categories=existing[:20]
            )

            result = self.invoke_llm_json(prompt)
            return result.get("category", "미분류")

        except Exception as e:
            self.logger.warning(f"카테고리 할당 실패: {e}")
            return "미분류"

    def _analyze_relationships(
        self,
        new_concepts: list[dict],
        existing_graph: dict
    ) -> list[dict]:
        """개념 간 관계 분석"""
        relationships = []
        existing_concepts = existing_graph.get("concepts", [])

        if not new_concepts:
            return relationships

        # 1. 새 개념 ↔ 기존 개념 관계
        if existing_concepts:
            cross_rels = self._find_cross_relationships(
                new_concepts, existing_concepts
            )
            relationships.extend(cross_rels)

        # 2. 새 개념 ↔ 새 개념 관계 (같은 배치 내)
        if len(new_concepts) > 1:
            internal_rels = self._find_internal_relationships(new_concepts)
            relationships.extend(internal_rels)

        return relationships

    def _find_cross_relationships(
        self,
        new_concepts: list[dict],
        existing_concepts: list[str]
    ) -> list[dict]:
        """새 개념과 기존 개념 간 관계 찾기"""
        new_names = list(set(c.get("name", "") for c in new_concepts if c.get("name")))

        if not new_names or not existing_concepts:
            return []

        try:
            prompt = self.get_prompt(
                "relationship_analysis",
                new_concepts=new_names[:20],
                existing_concepts=existing_concepts[:30]
            )

            result = self.invoke_llm_json(prompt)
            relationships = result.get("relationships", [])

            self.logger.info(f"교차 관계 발견: {len(relationships)}개")
            return relationships

        except Exception as e:
            self.logger.warning(f"교차 관계 분석 실패: {e}")
            return []

    def _find_internal_relationships(
        self,
        concepts: list[dict]
    ) -> list[dict]:
        """새 개념들 간 내부 관계 찾기"""
        concept_names = list(set(c.get("name", "") for c in concepts if c.get("name")))

        if len(concept_names) < 2:
            return []

        try:
            prompt = self.get_prompt(
                "inter_concept_relations",
                concepts=concept_names[:20]
            )

            result = self.invoke_llm_json(prompt)
            relationships = result.get("relationships", [])

            self.logger.info(f"내부 관계 발견: {len(relationships)}개")
            return relationships

        except Exception as e:
            self.logger.warning(f"내부 관계 분석 실패: {e}")
            return []
