"""텍스트 파일 파서"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TextDocument:
    """파싱된 텍스트 문서"""
    file_path: str
    title: Optional[str] = None
    content: str = ""
    raw_content: str = ""
    metadata: dict = field(default_factory=dict)
    sections: list[dict] = field(default_factory=list)


class TextParserTool:
    """텍스트 파일 파서"""

    name: str = "text_parser"
    description: str = "텍스트 파일(.txt) 파싱"

    def parse(self, file_path: str, encoding: str = 'utf-8') -> TextDocument:
        """텍스트 파일 파싱"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        content = self._read_with_fallback(path, encoding)

        doc = TextDocument(
            file_path=str(path.absolute()),
            raw_content=content,
            content=content
        )

        doc.title = self._extract_title(content, path)
        doc.metadata = self._extract_metadata(content)
        doc.sections = self._extract_sections(content)

        return doc

    def _read_with_fallback(self, path: Path, encoding: str) -> str:
        """여러 인코딩 시도"""
        encodings = [encoding, 'utf-8', 'cp949', 'euc-kr', 'latin-1']

        for enc in encodings:
            try:
                return path.read_text(encoding=enc)
            except UnicodeDecodeError:
                continue

        return path.read_bytes().decode('utf-8', errors='ignore')

    def _extract_title(self, content: str, path: Path) -> str:
        """제목 추출"""
        lines = content.strip().split('\n')

        for line in lines:
            line = line.strip()
            if line:
                return line[:100] if len(line) > 100 else line

        return path.stem

    def _extract_metadata(self, content: str) -> dict:
        """메타데이터 추출"""
        lines = content.split('\n')

        metadata = {
            "line_count": len(lines),
            "char_count": len(content),
            "word_count": len(content.split()),
            "has_urls": bool(re.search(r'https?://\S+', content)),
            "has_emails": bool(re.search(r'\S+@\S+\.\S+', content)),
        }

        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', content)
        if urls:
            metadata["urls"] = list(set(urls))

        emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', content)
        if emails:
            metadata["emails"] = list(set(emails))

        date_patterns = re.findall(
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4}',
            content
        )
        if date_patterns:
            metadata["dates"] = list(set(date_patterns))

        return metadata

    def _extract_sections(self, content: str) -> list[dict]:
        """섹션 추출 (빈 줄 기준 또는 구분선)"""
        sections = []

        separator_pattern = r'^[-=_]{3,}\s*$'
        parts = re.split(r'\n\s*\n|' + separator_pattern, content, flags=re.MULTILINE)

        for i, part in enumerate(parts):
            part = part.strip()
            if part:
                lines = part.split('\n')
                title = lines[0][:50] if lines else f"Section {i + 1}"

                sections.append({
                    "index": i,
                    "title": title,
                    "content": part,
                    "line_count": len(lines)
                })

        return sections
