# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LangGraph 기반 멀티 에이전트 시스템으로, 마크다운 등 문서를 분석하여 Neo4j 그래프 DB용 Cypher 쿼리로 변환. 로컬 LLM(Ollama)을 사용하여 프라이버시 보장.

## Commands

```bash
# 실행
python main.py                              # 기본 실행
python main.py --input ./notes              # 입력 디렉토리 지정
python main.py --output ./out/graph.cypher  # 출력 파일 지정
python main.py --model qwen2.5:7b           # LLM 모델 지정
python main.py --verbose                    # 디버그 로깅

# 의존성 설치
pip install -r requirements.txt

# Ollama 모델 준비
ollama pull qwen2.5:7b
```

## Architecture

```
입력 (md/txt/csv/docx/json)
       ↓
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Research   │ → │   Analyst   │ → │   Writer    │
│   Agent     │    │    Agent    │    │    Agent    │
│ (파싱/추출)  │    │ (분류/분석)  │    │(Cypher 생성)│
└─────────────┘    └─────────────┘    └─────────────┘
       ↓
출력 (Neo4j용 .cypher)
```

### 주요 컴포넌트

**Workflow** (`src/graphs/knowledge_graph.py`)
- `create_workflow()`: LangGraph StateGraph 생성 및 컴파일
- `KnowledgeGraphBuilder`: 워크플로우 실행 클래스

**State** (`src/graphs/state.py`)
- `WorkflowState`: 에이전트 간 공유 상태 (TypedDict)
- 각 에이전트는 state의 일부를 읽고 partial state만 반환 (순수 함수)

**Agents** (`src/agents/*/`)
- 각 에이전트는 독립 패키지: `agent.py`, `state.py`, `tools.py`, `prompts.py`
- `BaseAgent` 상속, `run(state) -> dict` 구현

**Tools** (`src/tools/`)
- `parsers/`: 문서 파싱 (md, txt, csv, docx, json)
- `cypher/`: Neo4j Cypher 쿼리 생성/관리

### 데이터 흐름

1. **Research Agent**: 파일 수집 → 파싱 → LLM 개념 추출 → `{parsed_docs, new_concepts, metadata}`
2. **Analyst Agent**: 기존 그래프 로드 → 카테고리 분류 → 관계 분석 → `{existing_graph, categorized_docs, relationships}`
3. **Writer Agent**: Cypher 쿼리 생성 → 중복 체크 → 파일 저장 → `{queries, result}`

## Key Abstractions

**LLM** (`src/core/llm.py`)
```python
from src.core.llm import get_llm, invoke_llm, invoke_llm_json
llm = get_llm("qwen2.5:7b")
result = invoke_llm_json(prompt, system_prompt)
```

**Config** (`src/core/config.py`)
```python
from src.core.config import get_config
config = get_config()  # LLMConfig, Neo4jConfig, PathsConfig 등
```

**Document Parsing** (`src/tools/parsers/document_parser.py`)
```python
from src.tools import DocumentParserTool, ParsedDocument
parser = DocumentParserTool()
doc: ParsedDocument = parser.parse("file.md")
```

**Cypher Generation** (`src/tools/cypher/manager.py`)
```python
from src.tools import CypherManager, GraphNode, GraphRelationship
manager = CypherManager("output.cypher")
node, query = manager.create_thought_node(title, content, source)
```

## Neo4j Graph Schema

노드: `Thought`, `Category`, `Concept`, `Date`, `Tag`
관계: `BELONGS_TO`, `MENTIONS`, `RELATED_TO`, `CREATED_ON`, `EVOLVED_TO`, `HAS_TAG`

## Tech Stack

- LangGraph 1.0.5 (워크플로우 오케스트레이션)
- langchain-ollama (Ollama 연동)
- python-docx, PyYAML (파일 파싱)
- Python 3.10+
