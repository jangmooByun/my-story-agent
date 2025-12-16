# 사용법

## 기본 사용

### 1. 입력 파일 준비

`data/input/` 폴더에 마크다운 파일들을 넣습니다:

```bash
data/input/
├── 2024-01-15-ai-memo.md
├── 2024-01-20-project-idea.md
├── daily-thoughts.md
└── ...
```

**지원하는 입력 형식**:
- 일반 마크다운 파일
- 날짜가 파일명에 포함된 파일 (예: `2024-01-15-*.md`)
- 태그가 포함된 파일 (예: `#태그` 형식)
- YAML frontmatter가 있는 파일

**입력 예시**:
```markdown
---
title: AI 학습 메모
date: 2024-01-15
tags: [AI, 학습]
---

# 오늘 배운 것

## 머신러닝 기초
오늘 머신러닝에 대해 공부했다.
딥러닝과 연관이 있는 것 같다.

## 느낀 점
데이터가 중요하다는 걸 깨달았다.
```

### 2. 실행

```bash
# 기본 실행
python main.py

# 특정 입력 폴더 지정
python main.py --input ./my-notes/

# 출력 형식 지정
python main.py --format csv    # Neo4j LOAD CSV용
python main.py --format cypher # Cypher 쿼리
python main.py --format md     # 마크다운 (기본)

# 모델 지정
python main.py --model mistral:7b

# 상세 로그
python main.py --verbose
```

### 3. 출력 확인

`data/output/` 폴더에 결과가 생성됩니다:

```bash
data/output/
├── graph_export.md      # 메인 출력
├── nodes/
│   ├── thoughts.csv
│   ├── concepts.csv
│   └── categories.csv
├── relationships/
│   ├── mentions.csv
│   ├── related_to.csv
│   └── belongs_to.csv
└── import.cypher        # Neo4j 임포트 쿼리
```

## 출력 형식 상세

### Markdown 출력 (기본)

`graph_export.md` 구조:

```markdown
# 그래프 분석 결과

## 요약
- 총 문서 수: 15
- 추출된 개념: 45
- 카테고리: 8
- 발견된 관계: 120

## 노드

### Thoughts (생각)
| ID | 제목 | 날짜 | 카테고리 |
|----|------|------|----------|
| t001 | AI 학습 메모 | 2024-01-15 | 기술/AI |

### Concepts (개념)
| 개념 | 빈도 | 관련 개념 |
|------|------|----------|
| 머신러닝 | 15 | 딥러닝, 데이터 |

### Categories (카테고리)
- 기술
  - AI
    - 머신러닝
    - 딥러닝
  - 프로그래밍

## 관계

### 개념 연관도
머신러닝 ←→ 딥러닝 (강도: 0.9)
데이터 ←→ 머신러닝 (강도: 0.7)

### 시간순 발전
[2024-01-15] AI 기초 → [2024-01-20] 딥러닝 심화
```

### CSV 출력

Neo4j의 `LOAD CSV` 명령어와 호환됩니다.

**Neo4j에서 가져오기**:
```cypher
// 노드 로드
LOAD CSV WITH HEADERS FROM 'file:///thoughts.csv' AS row
CREATE (:Thought {
    id: row.id,
    title: row.title,
    created_at: date(row.created_at)
});

// 관계 로드
LOAD CSV WITH HEADERS FROM 'file:///mentions.csv' AS row
MATCH (t:Thought {id: row.thought_id})
MATCH (c:Concept {name: row.concept_name})
CREATE (t)-[:MENTIONS {count: toInteger(row.count)}]->(c);
```

### Cypher 출력

직접 실행 가능한 Cypher 쿼리:

```cypher
// import.cypher

// === 노드 생성 ===
CREATE (:Thought {id: "t001", title: "AI 학습 메모", ...});
CREATE (:Concept {name: "머신러닝", frequency: 15});

// === 관계 생성 ===
MATCH (t:Thought {id: "t001"}), (c:Concept {name: "머신러닝"})
CREATE (t)-[:MENTIONS {count: 3, importance: 0.8}]->(c);
```

## 고급 사용

### 설정 커스터마이징

`configs/settings.yaml`:

```yaml
llm:
  model: mistral:7b
  temperature: 0.3      # 낮을수록 일관된 결과

agents:
  research:
    max_concepts_per_doc: 15    # 문서당 최대 개념 수
    include_headings: true      # 헤딩도 개념으로 추출

  analyst:
    similarity_threshold: 0.6   # 관계 판단 임계값
    max_categories: 10          # 최대 카테고리 수
    enable_temporal: true       # 시간순 분석 활성화

  writer:
    output_format: all          # md, csv, cypher 모두 생성
    include_statistics: true    # 통계 포함
```

### 특정 파일만 처리

```bash
# 패턴으로 필터링
python main.py --pattern "2024-01-*.md"

# 특정 파일 목록
python main.py --files file1.md file2.md file3.md
```

### 증분 처리

이미 처리된 파일은 건너뛰기:

```bash
python main.py --incremental
```

### 대화형 모드

결과 확인 후 수동 조정:

```bash
python main.py --interactive

# 출력:
# [1/3] Research Agent 완료
# 추출된 개념: 머신러닝, 딥러닝, 데이터
#
# 개념을 수정하시겠습니까? (y/n): y
# 추가할 개념: 신경망
# 제거할 개념:
#
# [2/3] Analyst Agent 실행 중...
```

## 결과 활용

### Neo4j Desktop에서 시각화

1. Neo4j Desktop 실행
2. 새 프로젝트/데이터베이스 생성
3. `import.cypher` 실행 또는 CSV 파일 임포트
4. Neo4j Browser에서 시각화:

```cypher
// 전체 그래프 보기 (주의: 노드가 많으면 느림)
MATCH (n) RETURN n LIMIT 100

// 특정 개념 중심으로 보기
MATCH path = (c:Concept {name: "머신러닝"})-[*1..2]-()
RETURN path
```

### Neo4j Bloom에서 탐색

더 인터랙티브한 시각화를 원하면 Neo4j Bloom 사용

### 분석 쿼리 예시

**가장 많이 언급된 개념**:
```cypher
MATCH (c:Concept)<-[r:MENTIONS]-()
RETURN c.name, count(r) as mentions
ORDER BY mentions DESC
LIMIT 10
```

**연결이 많은 생각 (허브 노드)**:
```cypher
MATCH (t:Thought)-[r]-()
RETURN t.title, count(r) as connections
ORDER BY connections DESC
LIMIT 10
```

**고립된 생각 (연결 없음)**:
```cypher
MATCH (t:Thought)
WHERE NOT (t)-[:MENTIONS]->()
RETURN t.title
```

## 문제 해결

### 개념 추출이 부정확함
- `temperature` 값을 낮춤 (0.1~0.3)
- 더 큰 모델 사용 (`mistral:7b` 또는 `llama3.1:8b`)

### 처리 속도가 느림
- 더 작은 모델 사용 (`llama3.2:1b`)
- 배치 크기 조정: `--batch-size 5`

### 메모리 부족
- 파일을 나눠서 처리: `--max-files 10`
- quantized 모델 사용: `llama3.2:3b-q4_0`

### 관계가 너무 많이/적게 추출됨
- `similarity_threshold` 조정 (0.5~0.8)
