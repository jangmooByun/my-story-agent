"""Writer Agent 전용 프롬프트"""

PROMPTS = {
    "system": """당신은 Neo4j Cypher 쿼리 전문가입니다.
그래프 데이터베이스에 저장할 노드와 관계를 정확하게 생성합니다.
중복을 피하고 일관된 명명 규칙을 사용합니다.""",

    "query_generation": """다음 정보를 바탕으로 Cypher 쿼리를 생성하세요.

## 문서 정보
제목: {title}
카테고리: {category}
개념들: {concepts}

## 기존 개념 (중복 방지)
{existing_concepts}

## 생성 규칙
1. MERGE 사용 (중복 방지)
2. 노드 ID는 label_name_timestamp 형식
3. 관계: Thought-[:BELONGS_TO]->Category, Thought-[:MENTIONS]->Concept

## 응답 형식 (JSON)
```json
{{
  "queries": [
    "MERGE (n:Thought {{...}})",
    "MERGE (n:Concept {{...}})",
    "MATCH ... MERGE ...-[:BELONGS_TO]->..."
  ],
  "new_concepts": ["새로 추가된 개념"],
  "skipped_concepts": ["중복으로 스킵된 개념"]
}}
```""",

    "relationship_query": """다음 관계를 Cypher 쿼리로 변환하세요.

## 관계 정보
소스: {source}
타겟: {target}
타입: {rel_type}
이유: {reason}

## 응답 형식
MATCH 쿼리만 반환 (설명 없이):
MATCH (a {{name: "..."}}), (b {{name: "..."}}) MERGE (a)-[:REL_TYPE]->(b)""",

    "validate_query": """다음 Cypher 쿼리가 올바른지 검증하세요.

## 쿼리
{query}

## 검증 항목
1. 문법 오류
2. 누락된 속성
3. 잘못된 관계 방향

## 응답 형식 (JSON)
```json
{{
  "is_valid": true,
  "issues": [],
  "corrected_query": "수정된 쿼리 (문제 있을 경우)"
}}
```""",
}
