"""Research Agent 전용 프롬프트"""

PROMPTS = {
    "system": """당신은 문서 분석 전문가입니다.
주어진 문서에서 핵심 개념, 키워드, 메타데이터를 정확하게 추출합니다.
응답은 반드시 지정된 JSON 형식으로 해주세요.""",

    "concept_extraction": """다음 문서에서 핵심 개념들을 추출하세요.

## 문서
{content}

## 추출 기준
1. 개념 (Concept): 문서의 핵심 아이디어, 주제, 키워드
2. 타입 분류:
   - keyword: 단순 키워드 (예: Python, API)
   - idea: 추상적 개념 (예: 마이크로서비스 아키텍처)
   - entity: 구체적 엔티티 (예: OpenAI, LangChain)

## 응답 형식 (JSON)
```json
{{
  "concepts": [
    {{"name": "개념명", "type": "keyword|idea|entity", "confidence": 0.8}}
  ],
  "category": "적절한 카테고리 (예: 프로그래밍, AI, 비즈니스)",
  "summary": "문서 요약 (1-2문장)"
}}
```""",

    "metadata_extraction": """다음 문서에서 메타데이터를 추출하세요.

## 문서
{content}

## 추출 항목
1. 날짜: 문서에 언급된 날짜들
2. 태그: 명시적 태그 (#태그 형식)
3. 저자/출처: 언급된 저자나 출처

## 응답 형식 (JSON)
```json
{{
  "dates": ["2024-01-15"],
  "tags": ["태그1", "태그2"],
  "authors": ["저자명"],
  "source": "출처 정보"
}}
```""",

    "summary": """다음 문서를 간결하게 요약하세요.

## 문서
{content}

## 요약 기준
- 핵심 내용만 포함
- 1-3문장으로 작성
- 전문 용어 유지

## 응답
요약 텍스트만 작성 (JSON 아님)""",
}
