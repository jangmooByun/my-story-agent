# 시스템 아키텍처

## 전체 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│                        입력 레이어                               │
│  data/input/*.md → DataLoader → 원본 텍스트 + 메타데이터          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph 워크플로우                          │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │   Research   │   │   Analyst    │   │    Writer    │        │
│  │    Agent     │ → │    Agent     │ → │    Agent     │        │
│  └──────────────┘   └──────────────┘   └──────────────┘        │
│         │                  │                  │                 │
│    파싱/추출           분류/분석          스키마 생성             │
│                                                                 │
│  [State: 공유 상태가 에이전트 간 전달됨]                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        출력 레이어                               │
│  Neo4jExporter → data/output/ (md, csv, cypher)                 │
└─────────────────────────────────────────────────────────────────┘
```

## 에이전트 상세

### 1. Research Agent (연구 에이전트)

**역할**: 원본 md 파일에서 정보 추출

**입력**:
- 원본 마크다운 텍스트
- 파일 메타데이터 (파일명, 수정일 등)

**출력**:
- 추출된 키워드/개념 목록
- 문서 구조 (헤딩, 리스트 등)
- 날짜 정보 (있는 경우)
- 태그 (있는 경우)

**사용 도구**:
- `md_parser`: 마크다운 구조 파싱
- `concept_extractor`: LLM 기반 개념 추출

```python
# 예시 출력
{
    "source_file": "2024-01-15-ai-thoughts.md",
    "concepts": ["머신러닝", "딥러닝", "신경망"],
    "headings": ["개요", "학습 내용", "궁금한 점"],
    "date": "2024-01-15",
    "tags": ["AI", "학습"]
}
```

### 2. Analyst Agent (분석 에이전트)

**역할**: 추출된 정보 분석 및 관계 도출

**입력**:
- Research Agent의 출력 (모든 문서)

**출력**:
- 카테고리 분류
- 개념 간 관계 매핑
- 시간순 연결
- 클러스터 정보

**사용 도구**:
- `relationship_finder`: LLM 기반 관계 분석
- `categorizer`: 주제 분류
- `temporal_linker`: 시간순 연결

```python
# 예시 출력
{
    "categories": {
        "기술": ["ai-thoughts.md", "coding-notes.md"],
        "일상": ["daily-memo.md"]
    },
    "relationships": [
        {"from": "머신러닝", "to": "딥러닝", "type": "RELATED_TO"},
        {"from": "ai-thoughts", "to": "coding-notes", "type": "EVOLVED_TO"}
    ],
    "clusters": [
        {"name": "AI 학습", "members": ["머신러닝", "딥러닝", "신경망"]}
    ]
}
```

### 3. Writer Agent (작성 에이전트)

**역할**: Neo4j 임포트용 출력 생성

**입력**:
- Analyst Agent의 분석 결과

**출력**:
- 노드 정의 파일
- 관계 정의 파일
- Cypher 쿼리 (선택)

**사용 도구**:
- `neo4j_exporter`: Neo4j 형식 변환
- `file_writer`: 파일 저장

## 상태 관리 (State)

LangGraph의 공유 상태 구조:

```python
class GraphState(TypedDict):
    # 입력
    input_files: list[str]
    raw_documents: list[Document]

    # Research Agent 출력
    extracted_concepts: list[ConceptInfo]
    document_metadata: list[DocumentMeta]

    # Analyst Agent 출력
    categories: dict[str, list[str]]
    relationships: list[Relationship]
    temporal_links: list[TemporalLink]

    # Writer Agent 출력
    output_files: list[str]

    # 공통
    errors: list[str]
    current_step: str
```

## 도구 (Tools) 구조

```
src/tools/
├── registry.py          # 도구 등록 및 관리
├── search/
│   ├── web_search.py    # (미사용 - 로컬 전용)
│   └── vector_search.py # 유사 문서 검색
├── data/
│   ├── md_parser.py     # 마크다운 파싱
│   ├── csv_reader.py    # CSV 처리
│   └── json_parser.py   # JSON 처리
├── analysis/
│   ├── concept_extractor.py    # 개념 추출
│   ├── relationship_finder.py  # 관계 분석
│   └── calculator.py           # (미사용)
└── io/
    ├── neo4j_exporter.py  # Neo4j 출력
    ├── file_writer.py     # 파일 저장
    └── api_caller.py      # (미사용 - 로컬 전용)
```

## LLM 연동 (Ollama)

```python
# src/core/llm.py 구조

class OllamaClient:
    def __init__(self, model: str = "llama3.2:3b"):
        self.model = model

    def extract_concepts(self, text: str) -> list[str]:
        """텍스트에서 핵심 개념 추출"""

    def find_relationships(self, concepts: list[str]) -> list[dict]:
        """개념 간 관계 분석"""

    def categorize(self, document: str) -> str:
        """문서 카테고리 분류"""
```

## 데이터 흐름 예시

```
1. 입력: data/input/2024-01-15-ai-memo.md
   "오늘 머신러닝 공부함. 딥러닝이랑 연관있는듯"

2. Research Agent:
   - concepts: ["머신러닝", "딥러닝"]
   - date: "2024-01-15"

3. Analyst Agent:
   - category: "기술/AI"
   - relationship: 머신러닝 -[RELATED_TO]-> 딥러닝

4. Writer Agent:
   - nodes.md: Thought, Concept 노드 정의
   - relationships.md: BELONGS_TO, RELATED_TO 정의

5. 출력: data/output/neo4j_import.md
```

## 확장 포인트

| 확장 | 설명 |
|------|------|
| 새 에이전트 추가 | `src/agents/` 아래 디렉토리 생성 |
| 새 도구 추가 | `src/tools/` 아래 구현 후 registry에 등록 |
| 출력 형식 추가 | `neo4j_exporter.py`에 포매터 추가 |
| 다른 LLM | `src/core/llm.py` 수정 |
