"""Research Agent 전용 도구"""

from pathlib import Path
from typing import Optional

from src.tools.parsers import DocumentParserTool, ParsedDocument


class ResearchTools:
    """Research Agent가 사용하는 도구 모음

    이 클래스는 Research Agent에서만 사용됨.
    다른 에이전트는 자체 tools.py를 가짐.
    """

    def __init__(self):
        self._parser = DocumentParserTool()

    @property
    def parser(self) -> DocumentParserTool:
        """문서 파서"""
        return self._parser

    def collect_files(
        self,
        input_dir: str,
        extensions: Optional[list[str]] = None
    ) -> list[Path]:
        """지원되는 파일 수집

        Args:
            input_dir: 입력 디렉토리
            extensions: 파일 확장자 목록 (None이면 기본값)

        Returns:
            파일 경로 목록
        """
        if extensions is None:
            extensions = [".md", ".txt", ".csv", ".docx", ".json"]

        path = Path(input_dir)
        if not path.exists():
            return []

        files = []
        for ext in extensions:
            files.extend(path.glob(f"*{ext}"))

        return sorted(files)

    def parse_file(self, file_path: str) -> ParsedDocument:
        """파일 파싱

        Args:
            file_path: 파일 경로

        Returns:
            ParsedDocument
        """
        return self._parser.parse(file_path)

    def extract_dates_from_content(self, content: str) -> list[str]:
        """콘텐츠에서 날짜 추출

        Args:
            content: 텍스트 콘텐츠

        Returns:
            날짜 문자열 목록
        """
        import re

        patterns = [
            r'\d{4}-\d{2}-\d{2}',  # 2024-01-15
            r'\d{4}/\d{2}/\d{2}',  # 2024/01/15
            r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일',  # 2024년 1월 15일
        ]

        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            dates.extend(matches)

        return list(set(dates))

    def extract_tags_from_content(self, content: str) -> list[str]:
        """콘텐츠에서 태그 추출

        Args:
            content: 텍스트 콘텐츠

        Returns:
            태그 목록
        """
        import re

        # #태그 형식 (헤딩 제외)
        tags = []
        for line in content.split('\n'):
            if not line.strip().startswith('#'):
                inline_tags = re.findall(
                    r'(?:^|\s)#([a-zA-Z가-힣][a-zA-Z0-9가-힣_-]*)',
                    line
                )
                tags.extend(inline_tags)

        return list(set(tags))
