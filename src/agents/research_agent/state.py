"""Research Agent 전용 상태 정의"""

from typing import TypedDict, Optional
from dataclasses import dataclass, field


@dataclass
class ExtractedConcept:
    """추출된 개념"""
    name: str
    type: str  # keyword, idea, entity
    confidence: float = 0.8
    source_file: str = ""


@dataclass
class ExtractedMetadata:
    """추출된 메타데이터"""
    dates: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    authors: list[str] = field(default_factory=list)


@dataclass
class ParsedDocument:
    """파싱된 문서"""
    file_name: str
    file_path: str
    file_type: str
    title: str
    content: str
    summary: str = ""
    concepts: list[ExtractedConcept] = field(default_factory=list)
    metadata: ExtractedMetadata = field(default_factory=ExtractedMetadata)
    category_suggestion: str = ""


class ResearchState(TypedDict, total=False):
    """Research Agent 내부 상태

    이 상태는 Research Agent 내부에서만 사용됨.
    워크플로우 전역 상태와는 별개.
    """
    # 입력
    input_dir: str
    file_extensions: list[str]

    # 처리 중
    current_file: str
    processing_status: str

    # 출력
    parsed_docs: list[dict]
    extracted_concepts: list[dict]
    extracted_metadata: dict

    # 에러
    errors: list[str]
