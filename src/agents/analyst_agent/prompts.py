"""Analyst Agent 전용 프롬프트"""

PROMPTS = {
    "system": """당신은 개념 분석 전문가입니다.
개념들 간의 관계를 파악하고, 적절한 카테고리로 분류합니다.
응답은 반드시 지정된 JSON 형식으로 해주세요.""",

    "relationship_analysis": """다음 개념들 간의 관계를 분석하세요.

## 새로 추출된 개념
{new_concepts}

## 기존 그래프의 개념
{existing_concepts}

## 관계 타입
- RELATED_TO: 의미적으로 관련 있음
- MENTIONS: 한 개념이 다른 개념을 언급함
- EVOLVED_TO: 개념이 발전/진화함
- SUPPORTS: 한 개념이 다른 개념을 뒷받침함
- CONTRADICTS: 개념 간 상충됨

## 응답 형식 (JSON)
의미적으로 명확히 관련 있는 쌍만 포함하세요.
```json
{{
  "relationships": [
    {{
      "source": "새 개념",
      "target": "기존 개념",
      "type": "RELATED_TO",
      "confidence": 0.8,
      "reason": "관계 이유 (간단히)"
    }}
  ]
}}
```""",

    "categorization": """다음 문서에 적절한 카테고리를 할당하세요.

## 문서 정보
제목: {title}
요약: {summary}
추출된 개념: {concepts}

## 기존 카테고리
{existing_categories}

## 카테고리 선택 기준
1. 기존 카테고리 중 적절한 것이 있으면 선택
2. 없으면 새 카테고리 제안 (간결하고 명확하게)

## 응답 형식 (JSON)
```json
{{
  "category": "선택된 카테고리",
  "is_new": false,
  "confidence": 0.8,
  "reason": "선택 이유"
}}
```""",

    "concept_deduplication": """다음 개념이 기존 개념과 중복되는지 판단하세요.

## 새 개념
{new_concept}

## 기존 유사 개념
{similar_concepts}

## 판단 기준
- 완전히 같은 의미면 중복
- 상위/하위 관계면 별개
- 다른 맥락이면 별개

## 응답 형식 (JSON)
```json
{{
  "is_duplicate": true,
  "matched_concept": "일치하는 기존 개념명",
  "reason": "판단 이유"
}}
```""",

    "inter_concept_relations": """새로 추출된 개념들 간의 내부 관계를 분석하세요.

## 새 개념 목록
{concepts}

## 관계 타입
- RELATED_TO: 의미적으로 관련
- MENTIONS: 언급 관계
- SUPPORTS: 뒷받침 관계

## 응답 형식 (JSON)
```json
{{
  "relationships": [
    {{
      "source": "개념1",
      "target": "개념2",
      "type": "RELATED_TO",
      "reason": "이유"
    }}
  ]
}}
```""",
}
