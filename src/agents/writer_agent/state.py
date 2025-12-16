"""Writer Agent 전용 상태 정의"""

from typing import TypedDict
from dataclasses import dataclass, field


@dataclass
class GeneratedQuery:
    """생성된 Cypher 쿼리"""
    query: str
    query_type: str  # node, relationship
    node_label: str = ""
    node_id: str = ""


@dataclass
class WriteResult:
    """쓰기 결과"""
    success: bool
    output_file: str
    queries_written: int
    new_nodes: int
    new_relationships: int
    errors: list[str] = field(default_factory=list)


class WriterState(TypedDict, total=False):
    """Writer Agent 내부 상태"""
    # 입력
    categorized_docs: list[dict]
    relationships: list[dict]
    existing_graph: dict

    # 처리 중
    current_doc: dict
    generated_queries: list[str]

    # 출력
    queries: list[str]
    result: dict

    # 에러
    errors: list[str]
