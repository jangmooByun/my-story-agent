# Markdown to Neo4j Graph Agent System

마구잡이로 작성된 마크다운 파일들을 분석하여 Neo4j 그래프 데이터베이스용 구조화된 문서로 변환하는 멀티 에이전트 시스템

## 핵심 기능

- **생각의 카테고리화**: 흩어진 메모와 아이디어를 주제별로 자동 분류
- **연관성 발견**: 개념 간 숨겨진 관계를 그래프로 시각화
- **시간순 추적**: 생각의 발전과 변화 흐름 파악
- **로컬 LLM**: Ollama를 사용한 프라이버시 보장 (API 불필요)

## 시스템 개요

```
입력 (md 파일들)
      ↓
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Research   │ → │   Analyst   │ → │   Writer    │
│   Agent     │    │    Agent    │    │    Agent    │
│  (파싱/추출) │    │ (분류/분석)  │    │ (스키마생성) │
└─────────────┘    └─────────────┘    └─────────────┘
      ↓
출력 (Neo4j용 md/csv)
```

## 기술 스택

| 구성요소 | 기술 |
|---------|------|
| 워크플로우 | LangGraph |
| 로컬 LLM | Ollama (llama3.2, mistral 등) |
| 그래프 DB | Neo4j |
| 언어 | Python 3.11+ |

## 빠른 시작

```bash
# 1. Ollama 설치 및 모델 다운로드
ollama pull llama3.2:3b

# 2. 의존성 설치
pip install -e .

# 3. 입력 파일 준비
cp your-notes/*.md data/input/

# 4. 실행
python main.py
```

## 프로젝트 구조

```
my-agent-system/
├── src/
│   ├── agents/          # 에이전트 구현
│   │   ├── research/    # 파싱 & 추출
│   │   ├── analyst/     # 분류 & 관계 분석
│   │   └── writer/      # Neo4j 출력 생성
│   ├── graph/           # LangGraph 워크플로우
│   ├── tools/           # 에이전트 도구
│   └── core/            # 설정, LLM 연결
├── configs/             # 설정 파일
├── data/
│   ├── input/           # 입력 md 파일
│   └── output/          # Neo4j용 출력
└── docs/                # 상세 문서
```

## 문서

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - 시스템 아키텍처 상세
- [SETUP.md](docs/SETUP.md) - Ollama 설정 가이드
- [GRAPH_SCHEMA.md](docs/GRAPH_SCHEMA.md) - Neo4j 스키마 정의
- [USAGE.md](docs/USAGE.md) - 상세 사용법

## 출력 예시

입력 md 파일들이 다음과 같은 Neo4j 그래프로 변환됩니다:

```
(:Thought {title: "AI 학습 메모"})
    -[:BELONGS_TO]-> (:Category {name: "기술"})
    -[:MENTIONS]-> (:Concept {name: "머신러닝"})
    -[:CREATED_ON]-> (:Date {date: "2024-01-15"})

(:Concept {name: "머신러닝"})
    -[:RELATED_TO]-> (:Concept {name: "딥러닝"})
```

## 라이선스

MIT
