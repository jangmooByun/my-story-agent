"""전역 워크플로우 상태 정의"""

from typing import TypedDict, Any, Optional


class WorkflowState(TypedDict, total=False):
    """LangGraph 워크플로우 전역 상태

    각 에이전트는 이 상태의 일부를 읽고 업데이트함.
    에이전트 내부 상태는 각 에이전트의 state.py에 정의됨.
    """

    # === 입력 ===
    input_dir: str          # 입력 파일 디렉토리
    output_file: str        # 출력 Cypher 파일 경로

    # === Research Agent 출력 ===
    parsed_docs: list[dict]      # 파싱된 문서들
    new_concepts: list[dict]     # 추출된 개념들
    metadata: dict               # 추출된 메타데이터 (날짜, 태그 등)

    # === Analyst Agent 출력 ===
    existing_graph: dict         # 기존 그래프 상태
    categorized_docs: list[dict] # 카테고리가 할당된 문서들
    relationships: list[dict]    # 분석된 관계들

    # === Writer Agent 출력 ===
    queries: list[str]      # 생성된 Cypher 쿼리들
    result: dict            # 최종 결과 정보

    # === 공통 ===
    errors: list[str]       # 에러 메시지들
    current_step: str       # 현재 실행 중인 단계


def create_initial_state(
    input_dir: str = "data/input",
    output_file: str = "data/output/graph.cypher"
) -> WorkflowState:
    """초기 상태 생성

    Args:
        input_dir: 입력 디렉토리
        output_file: 출력 파일

    Returns:
        초기 WorkflowState
    """
    return WorkflowState(
        input_dir=input_dir,
        output_file=output_file,
        parsed_docs=[],
        new_concepts=[],
        metadata={},
        existing_graph={},
        categorized_docs=[],
        relationships=[],
        queries=[],
        result={},
        errors=[],
        current_step="initialized"
    )
