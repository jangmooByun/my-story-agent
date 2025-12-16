"""Research Agent - 문서 파싱 및 개념 추출"""

from pathlib import Path
from typing import Optional

from core.base_agent import BaseAgent
from core.config import get_config
from agents.research_agent.tools import ResearchTools
from agents.research_agent.prompts import PROMPTS


class ResearchAgent(BaseAgent):
    """Research Agent

    역할 (ARCHITECTURE.md 스펙):
    - 문서 파싱 (md, txt, csv, docx)
    - 개념/키워드 추출 (LLM)
    - 메타데이터 수집 (날짜, 태그)

    사용법:
        agent = ResearchAgent()
        result = agent.run({"input_dir": "data/input"})

        # result 구조:
        # {
        #     "parsed_docs": [...],
        #     "new_concepts": [...],
        #     "metadata": {...}
        # }
    """

    name = "research_agent"
    description = "문서를 파싱하고 개념/메타데이터를 추출합니다"

    def __init__(self, model_name: Optional[str] = None):
        super().__init__(model_name=model_name)

        # 에이전트 전용 프롬프트
        self.prompts = PROMPTS

        # 에이전트 전용 도구
        self.tools = ResearchTools()

        # 설정
        self.config = get_config()

    def run(self, state: dict) -> dict:
        """에이전트 실행

        순수 함수: 입력 state를 수정하지 않고 새 값만 반환

        Args:
            state: {input_dir, ...}

        Returns:
            {parsed_docs, new_concepts, metadata}
        """
        self.logger.info("=== Research Agent 시작 ===")

        input_dir = Path(state.get("input_dir", "data/input"))
        parsed_docs = []
        all_concepts = []
        all_metadata = {
            "dates": [],
            "tags": [],
            "sources": []
        }

        # 1. 파일 수집
        extensions = self.config.paths.supported_extensions
        input_files = self.tools.collect_files(str(input_dir), extensions)
        self.logger.info(f"입력 파일 수: {len(input_files)}")

        # 2. 각 파일 처리
        for file_path in input_files:
            self.logger.info(f"분석 중: {file_path.name}")

            try:
                doc_result = self._process_document(file_path)
                parsed_docs.append(doc_result)

                # 개념 수집
                for concept in doc_result.get("analysis", {}).get("concepts", []):
                    concept["source_file"] = doc_result["file_name"]
                    all_concepts.append(concept)

                # 메타데이터 수집
                meta = doc_result.get("metadata", {})
                all_metadata["dates"].extend(meta.get("dates", []))
                all_metadata["tags"].extend(meta.get("tags", []))

            except Exception as e:
                self.logger.error(f"파일 분석 실패 {file_path.name}: {e}")
                continue

        # 중복 제거
        all_metadata["dates"] = list(set(all_metadata["dates"]))
        all_metadata["tags"] = list(set(all_metadata["tags"]))

        self.logger.info(
            f"분석 완료: {len(parsed_docs)}개 문서, "
            f"{len(all_concepts)}개 개념"
        )

        # 순수 함수: 새 값만 반환 (state 수정 안함)
        return {
            "parsed_docs": parsed_docs,
            "new_concepts": all_concepts,
            "metadata": all_metadata
        }

    def _process_document(self, file_path: Path) -> dict:
        """단일 문서 처리"""
        # 1. 파싱
        doc = self.tools.parse_file(str(file_path))

        # 2. LLM 분석
        analysis = self._analyze_with_llm(doc.content)

        # 3. 메타데이터 추출
        metadata = self._extract_metadata(doc)

        return {
            "file_name": doc.file_name,
            "file_path": str(file_path),
            "file_type": doc.file_type,
            "title": doc.title or file_path.stem,
            "content": doc.content,
            "analysis": analysis,
            "metadata": metadata
        }

    def _analyze_with_llm(self, content: str) -> dict:
        """LLM으로 개념 추출"""
        prompt = self.get_prompt("concept_extraction", content=content[:3000])

        try:
            result = self.invoke_llm_json(prompt)
            return result
        except Exception as e:
            self.logger.warning(f"LLM 분석 실패: {e}")
            return self._fallback_analysis(content)

    def _extract_metadata(self, doc) -> dict:
        """메타데이터 추출"""
        dates = self.tools.extract_dates_from_content(doc.content)
        tags = self.tools.extract_tags_from_content(doc.content)

        # 마크다운 frontmatter에서 추가 태그
        if hasattr(doc, 'metadata') and isinstance(doc.metadata, dict):
            fm_tags = doc.metadata.get("tags", [])
            if isinstance(fm_tags, list):
                tags.extend(fm_tags)

        return {
            "dates": list(set(dates)),
            "tags": list(set(tags)),
            "links": doc.metadata.get("links", []) if hasattr(doc, 'metadata') else []
        }

    def _fallback_analysis(self, content: str) -> dict:
        """폴백 분석 (LLM 실패 시)"""
        import re

        # 간단한 키워드 추출
        words = re.findall(r'[가-힣]{2,}|[a-zA-Z]{4,}', content)
        word_freq = {}

        for word in words:
            w = word.lower()
            word_freq[w] = word_freq.get(w, 0) + 1

        top_words = sorted(
            word_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            "concepts": [
                {"name": word, "type": "keyword", "confidence": 0.5}
                for word, freq in top_words if freq >= 2
            ],
            "category": "미분류",
            "summary": content[:100]
        }
