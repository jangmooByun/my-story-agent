"""Analyst Agent 전용 상태 정의"""

from typing import TypedDict
from dataclasses import dataclass, field


@dataclass
class AnalyzedRelationship:
    """분석된 관계"""
    source: str
    target: str
    rel_type: str  # RELATED_TO, MENTIONS, EVOLVED_TO, etc.
    confidence: float = 0.8
    reason: str = ""


@dataclass
class CategoryAssignment:
    """카테고리 할당"""
    concept: str
    category: str
    confidence: float = 0.8


class AnalystState(TypedDict, total=False):
    """Analyst Agent 내부 상태"""
    # 입력
    parsed_docs: list[dict]
    new_concepts: list[dict]
    existing_concepts: list[str]
    existing_graph: dict

    # 처리 중
    current_concept: str
    analysis_progress: int

    # 출력
    categorized_docs: list[dict]
    relationships: list[dict]
    category_assignments: list[dict]

    # 에러
    errors: list[str]
