# Neo4j 그래프 스키마

## 개요

이 문서는 마크다운 파일에서 추출된 정보를 Neo4j 그래프 데이터베이스에 저장하기 위한 스키마를 정의합니다.

## 노드 타입

### 1. Thought (생각)

개별 마크다운 파일 또는 문서 섹션을 나타냅니다.

```cypher
(:Thought {
    id: String,           // 고유 ID (UUID)
    title: String,        // 제목 또는 파일명
    content: String,      // 원본 내용 (요약)
    source_file: String,  // 원본 파일 경로
    created_at: DateTime, // 생성일
    updated_at: DateTime  // 수정일
})
```

**예시**:
```cypher
CREATE (:Thought {
    id: "thought-001",
    title: "AI 학습 메모",
    content: "오늘 머신러닝에 대해 공부했다...",
    source_file: "2024-01-15-ai-memo.md",
    created_at: datetime("2024-01-15")
})
```

### 2. Category (카테고리)

생각들을 분류하는 주제 카테고리입니다.

```cypher
(:Category {
    id: String,          // 고유 ID
    name: String,        // 카테고리명
    description: String, // 설명 (선택)
    level: Integer       // 계층 레벨 (0: 최상위)
})
```

**예시 카테고리 구조**:
```
기술 (level: 0)
├── AI (level: 1)
│   ├── 머신러닝 (level: 2)
│   └── 딥러닝 (level: 2)
├── 프로그래밍 (level: 1)
일상 (level: 0)
├── 일기 (level: 1)
└── 독서 (level: 1)
```

### 3. Concept (개념)

추출된 핵심 키워드나 개념입니다.

```cypher
(:Concept {
    id: String,          // 고유 ID
    name: String,        // 개념명
    description: String, // 설명 (LLM 생성)
    frequency: Integer   // 등장 빈도
})
```

**예시**:
```cypher
CREATE (:Concept {
    id: "concept-ml",
    name: "머신러닝",
    description: "데이터에서 패턴을 학습하는 AI 기술",
    frequency: 15
})
```

### 4. Date (날짜)

시간순 분석을 위한 날짜 노드입니다.

```cypher
(:Date {
    date: Date,          // 날짜
    year: Integer,
    month: Integer,
    day: Integer,
    week: Integer        // 주차
})
```

### 5. Tag (태그)

사용자가 직접 지정한 태그입니다 (md 파일에 #태그 형식으로 존재하는 경우).

```cypher
(:Tag {
    id: String,
    name: String
})
```

## 관계 타입

### 1. BELONGS_TO

Thought가 Category에 속함을 나타냅니다.

```cypher
(:Thought)-[:BELONGS_TO {
    confidence: Float,   // 분류 신뢰도 (0-1)
    assigned_by: String  // "llm" 또는 "user"
}]->(:Category)
```

### 2. MENTIONS

Thought가 특정 Concept을 언급함을 나타냅니다.

```cypher
(:Thought)-[:MENTIONS {
    count: Integer,      // 언급 횟수
    importance: Float    // 중요도 (0-1)
}]->(:Concept)
```

### 3. RELATED_TO

Concept 간의 연관 관계입니다.

```cypher
(:Concept)-[:RELATED_TO {
    strength: Float,     // 관계 강도 (0-1)
    type: String         // "similar", "opposite", "part_of" 등
}]->(:Concept)
```

**관계 유형**:
| type | 설명 | 예시 |
|------|------|------|
| similar | 유사 개념 | 머신러닝 ↔ 딥러닝 |
| opposite | 반대 개념 | 입력 ↔ 출력 |
| part_of | 부분 관계 | 신경망 → 딥러닝 |
| requires | 선행 필요 | 딥러닝 → 선형대수 |
| causes | 인과 관계 | 학습 → 성장 |

### 4. CREATED_ON

Thought의 생성 날짜를 연결합니다.

```cypher
(:Thought)-[:CREATED_ON]->(:Date)
```

### 5. EVOLVED_TO

시간에 따른 생각의 발전을 나타냅니다.

```cypher
(:Thought)-[:EVOLVED_TO {
    days_apart: Integer,  // 날짜 차이
    evolution_type: String // "expanded", "revised", "concluded"
}]->(:Thought)
```

### 6. HAS_TAG

Thought에 붙은 태그입니다.

```cypher
(:Thought)-[:HAS_TAG]->(:Tag)
```

### 7. SUBCATEGORY_OF

카테고리 계층 구조입니다.

```cypher
(:Category)-[:SUBCATEGORY_OF]->(:Category)
```

## 전체 스키마 다이어그램

```
                    ┌──────────┐
                    │   Date   │
                    └────┬─────┘
                         │ CREATED_ON
                         ↓
┌──────────┐    ┌──────────────┐    ┌──────────────┐
│   Tag    │←───│   Thought    │───→│   Category   │
└──────────┘    └──────┬───────┘    └──────┬───────┘
   HAS_TAG             │                    │
                       │ MENTIONS    SUBCATEGORY_OF
                       ↓                    ↓
                ┌──────────────┐    ┌──────────────┐
                │   Concept    │    │   Category   │
                └──────┬───────┘    └──────────────┘
                       │
                 RELATED_TO
                       ↓
                ┌──────────────┐
                │   Concept    │
                └──────────────┘
```

## 인덱스 및 제약조건

```cypher
// 고유성 제약
CREATE CONSTRAINT thought_id IF NOT EXISTS
FOR (t:Thought) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT concept_name IF NOT EXISTS
FOR (c:Concept) REQUIRE c.name IS UNIQUE;

CREATE CONSTRAINT category_name IF NOT EXISTS
FOR (cat:Category) REQUIRE cat.name IS UNIQUE;

// 검색용 인덱스
CREATE INDEX thought_title IF NOT EXISTS
FOR (t:Thought) ON (t.title);

CREATE INDEX thought_created IF NOT EXISTS
FOR (t:Thought) ON (t.created_at);

CREATE INDEX concept_frequency IF NOT EXISTS
FOR (c:Concept) ON (c.frequency);
```

## 출력 파일 형식

### Option 1: Markdown (기본)

`data/output/graph_export.md`:
```markdown
# Nodes

## Thoughts
- thought-001: "AI 학습 메모" (2024-01-15)
- thought-002: "딥러닝 정리" (2024-01-20)

## Concepts
- 머신러닝 (frequency: 15)
- 딥러닝 (frequency: 12)

## Categories
- 기술 > AI > 머신러닝

# Relationships

## MENTIONS
- thought-001 -> 머신러닝
- thought-001 -> 딥러닝

## RELATED_TO
- 머신러닝 <-> 딥러닝 (strength: 0.9, type: similar)
```

### Option 2: CSV (Neo4j LOAD CSV용)

`nodes_thoughts.csv`:
```csv
id,title,content,source_file,created_at
thought-001,"AI 학습 메모","오늘 머신러닝...",2024-01-15-ai-memo.md,2024-01-15
```

`relationships_mentions.csv`:
```csv
thought_id,concept_name,count,importance
thought-001,머신러닝,3,0.8
```

### Option 3: Cypher 쿼리

`import.cypher`:
```cypher
// 노드 생성
CREATE (:Thought {id: "thought-001", title: "AI 학습 메모", ...});
CREATE (:Concept {name: "머신러닝", ...});

// 관계 생성
MATCH (t:Thought {id: "thought-001"}), (c:Concept {name: "머신러닝"})
CREATE (t)-[:MENTIONS {count: 3}]->(c);
```

## 유용한 Cypher 쿼리

### 특정 개념과 관련된 모든 생각 찾기
```cypher
MATCH (t:Thought)-[:MENTIONS]->(c:Concept {name: "머신러닝"})
RETURN t.title, t.created_at
ORDER BY t.created_at
```

### 연관된 개념 네트워크
```cypher
MATCH (c1:Concept {name: "머신러닝"})-[r:RELATED_TO]-(c2:Concept)
RETURN c1.name, type(r), c2.name, r.strength
```

### 시간에 따른 생각 발전 추적
```cypher
MATCH path = (t1:Thought)-[:EVOLVED_TO*]->(t2:Thought)
WHERE t1.title CONTAINS "AI"
RETURN path
```

### 카테고리별 생각 수
```cypher
MATCH (t:Thought)-[:BELONGS_TO]->(c:Category)
RETURN c.name, count(t) as thought_count
ORDER BY thought_count DESC
```
