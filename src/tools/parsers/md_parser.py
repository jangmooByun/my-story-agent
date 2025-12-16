"""마크다운 파일 파싱 도구"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import yaml


@dataclass
class MarkdownSection:
    """마크다운 섹션"""
    level: int
    title: str
    content: str
    line_start: int
    line_end: int


@dataclass
class MarkdownDocument:
    """파싱된 마크다운 문서"""
    file_path: str
    title: Optional[str] = None
    frontmatter: dict = field(default_factory=dict)
    sections: list[MarkdownSection] = field(default_factory=list)
    headings: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    raw_content: str = ""

    @property
    def plain_text(self) -> str:
        """마크다운 문법 제거한 순수 텍스트"""
        text = self.raw_content
        text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`[^`]+`', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)
        text = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', text)
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        return text.strip()


class MarkdownParserTool:
    """마크다운 파일 파싱 도구"""

    name: str = "markdown_parser"
    description: str = "마크다운 파일을 파싱하여 구조화된 정보 추출"

    def parse(self, file_path: str) -> MarkdownDocument:
        """마크다운 파일 파싱"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        content = path.read_text(encoding='utf-8')
        return self.parse_content(content, file_path)

    def parse_content(self, content: str, file_path: str = "") -> MarkdownDocument:
        """마크다운 문자열 파싱"""
        doc = MarkdownDocument(file_path=file_path, raw_content=content)

        doc.frontmatter = self._parse_frontmatter(content)
        doc.title = self._extract_title(content, doc.frontmatter)
        doc.headings = self._extract_headings(content)
        doc.sections = self._parse_sections(content)
        doc.links = self._extract_links(content)
        doc.tags = self._extract_tags(content, doc.frontmatter)

        return doc

    def _parse_frontmatter(self, content: str) -> dict:
        """YAML frontmatter 파싱"""
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError:
                return {}
        return {}

    def _extract_title(self, content: str, frontmatter: dict) -> Optional[str]:
        """제목 추출"""
        if 'title' in frontmatter:
            return frontmatter['title']

        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        return None

    def _extract_headings(self, content: str) -> list[str]:
        """모든 헤딩 추출"""
        content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

        headings = []
        for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append(f"{'#' * level} {title}")

        return headings

    def _parse_sections(self, content: str) -> list[MarkdownSection]:
        """섹션별로 내용 분리"""
        content_without_fm = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
        lines = content_without_fm.split('\n')

        sections = []
        current_section = None
        current_content_lines = []

        for i, line in enumerate(lines):
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if heading_match:
                if current_section:
                    current_section.content = '\n'.join(current_content_lines).strip()
                    current_section.line_end = i - 1
                    sections.append(current_section)

                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                current_section = MarkdownSection(
                    level=level,
                    title=title,
                    content="",
                    line_start=i,
                    line_end=i
                )
                current_content_lines = []
            elif current_section:
                current_content_lines.append(line)

        if current_section:
            current_section.content = '\n'.join(current_content_lines).strip()
            current_section.line_end = len(lines) - 1
            sections.append(current_section)

        return sections

    def _extract_links(self, content: str) -> list[str]:
        """링크 추출"""
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', content)

        links = [url for _, url in markdown_links]
        links.extend(urls)

        return list(set(links))

    def _extract_tags(self, content: str, frontmatter: dict) -> list[str]:
        """태그 추출"""
        tags = []

        if 'tags' in frontmatter:
            fm_tags = frontmatter['tags']
            if isinstance(fm_tags, list):
                tags.extend(fm_tags)
            elif isinstance(fm_tags, str):
                tags.extend([t.strip() for t in fm_tags.split(',')])

        for line in content.split('\n'):
            if not line.startswith('#'):
                inline_tags = re.findall(r'(?:^|\s)#([a-zA-Z가-힣][a-zA-Z0-9가-힣_-]*)', line)
                tags.extend(inline_tags)

        return list(set(tags))

    def parse_directory(self, directory: str, pattern: str = "*.md") -> list[MarkdownDocument]:
        """디렉토리 내 모든 마크다운 파일 파싱"""
        path = Path(directory)
        if not path.exists():
            raise FileNotFoundError(f"디렉토리를 찾을 수 없습니다: {directory}")

        documents = []
        for file_path in path.glob(pattern):
            if file_path.is_file():
                try:
                    doc = self.parse(str(file_path))
                    documents.append(doc)
                except Exception as e:
                    print(f"파싱 실패: {file_path} - {e}")

        return documents
