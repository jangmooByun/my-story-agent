# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

마크다운 파일을 분석하여 Neo4j 그래프 DB용 문서로 변환하는 LangGraph 기반 멀티 에이전트 시스템.
로컬 LLM(Ollama)을 사용하여 프라이버시 보장.

## Architecture

```
입력 (md 파일) → Research Agent → Analyst Agent → Writer Agent → 출력 (Neo4j용)
```

## 구현 상태

### 구현 완료
- `src/tools/` - 모든 도구 구현됨
- `docs/` - 문서 작성됨
- `README.md` - 프로젝트 소개

### 미구현 (빈 파일)
- `src/agents/` - 에이전트 클래스
- `src/graph/` - LangGraph 워크플로우
- `src/core/` - 설정, LLM 연결
- `main.py` - 진입점

## Tools (구현됨)

### 도구 이름 상수
```python
from src.tools.tools import FILE_READ_TOOL_NAME, CONCEPT_EXTRACTOR_TOOL_NAME
```

### 구현된 도구들

| 경로 | 클래스 | 용도 |
|------|--------|------|
| `tools/data/md_parser.py` | `MarkdownParserTool` | md 파일 파싱 |
| `tools/analysis/concept_extractor.py` | `ConceptExtractorTool` | 개념/키워드 추출 (LLM) |
| `tools/analysis/relationship_finder.py` | `RelationshipFinderTool` | 관계 분석 (LLM) |
| `tools/analysis/categorizer.py` | `CategorizerTool` | 카테고리 분류 (LLM) |
| `tools/io/file_manager.py` | `FileManager` | 파일 CRUD |
| `tools/io/folder_manager.py` | `FolderManager` | 폴더 CRUD |
| `tools/io/neo4j_exporter.py` | `Neo4jExporterTool` | Neo4j 출력 (md/csv/cypher) |
| `tools/search/file_search.py` | `FileSearchTool` | 파일 검색 (glob) |
| `tools/search/text_search.py` | `TextSearchTool` | 텍스트 검색 (grep) |

### 도구 레지스트리
```python
from src.tools.registry import initialize_tools, get_tools_for

registry = initialize_tools(llm=my_llm)
research_tools = get_tools_for("research")
```

## 다음 구현 단계

1. `src/core/config.py` - Ollama 설정
2. `src/core/llm.py` - Ollama 클라이언트 래퍼
3. `src/graph/state.py` - LangGraph 상태 스키마
4. `src/agents/base.py` - 기본 에이전트 클래스
5. 개별 에이전트 구현
6. `src/graph/workflow.py` - 워크플로우 연결
7. `main.py` - 진입점

## Commands

```bash
# 의존성 설치 (pyproject.toml 구현 후)
pip install -e .

# 실행 (main.py 구현 후)
python main.py --input data/input/ --output data/output/
```

## Tech Stack

- LangGraph: 워크플로우 오케스트레이션
- Ollama: 로컬 LLM (llama3.2, mistral)
- Neo4j: 그래프 DB (출력 대상)
- Python 3.11+
