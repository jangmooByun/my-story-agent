"""통합 문서 파서 - 다양한 파일 형식 지원"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime


@dataclass
class ParsedDocument:
    """파싱된 문서 (모든 형식 공통)"""
    file_path: str
    file_type: str  # "markdown", "text", "csv", "docx", "json"
    title: Optional[str] = None
    content: str = ""
    metadata: dict = field(default_factory=dict)
    sections: list[dict] = field(default_factory=list)
    raw_content: str = ""

    file_name: str = ""
    file_size: int = 0
    created_at: str = ""
    modified_at: str = ""


class DocumentParserTool:
    """다양한 형식의 문서를 파싱하는 통합 도구"""

    name: str = "document_parser"
    description: str = "다양한 형식(md, txt, csv, docx, json)의 문서를 파싱"

    SUPPORTED_EXTENSIONS = {".md", ".txt", ".csv", ".docx", ".json"}

    def __init__(self):
        self._md_parser = None
        self._text_parser = None
        self._csv_parser = None
        self._docx_parser = None

    def parse(self, file_path: str) -> ParsedDocument:
        """파일 파싱 (확장자에 따라 적절한 파서 사용)"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        ext = path.suffix.lower()

        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"지원하지 않는 형식: {ext}. "
                f"지원 형식: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

        stat = path.stat()
        base_doc = ParsedDocument(
            file_path=str(path.absolute()),
            file_type=self._ext_to_type(ext),
            file_name=path.name,
            file_size=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
            modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat()
        )

        if ext == ".md":
            return self._parse_markdown(path, base_doc)
        elif ext == ".txt":
            return self._parse_text(path, base_doc)
        elif ext == ".csv":
            return self._parse_csv(path, base_doc)
        elif ext == ".docx":
            return self._parse_docx(path, base_doc)
        elif ext == ".json":
            return self._parse_json(path, base_doc)

        return base_doc

    def _ext_to_type(self, ext: str) -> str:
        """확장자를 파일 타입으로 변환"""
        mapping = {
            ".md": "markdown",
            ".txt": "text",
            ".csv": "csv",
            ".docx": "docx",
            ".json": "json"
        }
        return mapping.get(ext, "unknown")

    def _parse_markdown(self, path: Path, doc: ParsedDocument) -> ParsedDocument:
        """마크다운 파싱"""
        from tools.parsers.md_parser import MarkdownParserTool

        if self._md_parser is None:
            self._md_parser = MarkdownParserTool()

        md_doc = self._md_parser.parse(str(path))

        doc.title = md_doc.title
        doc.content = md_doc.plain_text
        doc.raw_content = md_doc.raw_content
        doc.metadata = {
            "frontmatter": md_doc.frontmatter,
            "headings": md_doc.headings,
            "tags": md_doc.tags,
            "links": md_doc.links
        }
        doc.sections = [
            {
                "level": s.level,
                "title": s.title,
                "content": s.content
            }
            for s in md_doc.sections
        ]

        return doc

    def _parse_text(self, path: Path, doc: ParsedDocument) -> ParsedDocument:
        """텍스트 파싱"""
        from tools.parsers.text_parser import TextParserTool

        if self._text_parser is None:
            self._text_parser = TextParserTool()

        text_doc = self._text_parser.parse(str(path))

        doc.title = text_doc.title
        doc.content = text_doc.content
        doc.raw_content = text_doc.raw_content
        doc.metadata = text_doc.metadata
        doc.sections = text_doc.sections

        return doc

    def _parse_csv(self, path: Path, doc: ParsedDocument) -> ParsedDocument:
        """CSV 파싱"""
        from tools.parsers.csv_reader import CSVParserTool

        if self._csv_parser is None:
            self._csv_parser = CSVParserTool()

        csv_doc = self._csv_parser.parse(str(path))

        doc.title = csv_doc.title
        doc.content = csv_doc.content
        doc.raw_content = csv_doc.raw_content
        doc.metadata = csv_doc.metadata
        doc.sections = csv_doc.sections

        return doc

    def _parse_docx(self, path: Path, doc: ParsedDocument) -> ParsedDocument:
        """워드 문서 파싱"""
        from tools.parsers.docx_parser import DocxParserTool

        if self._docx_parser is None:
            self._docx_parser = DocxParserTool()

        docx_doc = self._docx_parser.parse(str(path))

        doc.title = docx_doc.title
        doc.content = docx_doc.content
        doc.raw_content = docx_doc.raw_content
        doc.metadata = docx_doc.metadata
        doc.sections = docx_doc.sections

        return doc

    def _parse_json(self, path: Path, doc: ParsedDocument) -> ParsedDocument:
        """JSON 파싱"""
        import json

        content = path.read_text(encoding='utf-8')
        doc.raw_content = content

        try:
            data = json.loads(content)

            if isinstance(data, dict):
                doc.title = data.get('title') or data.get('name') or path.stem
                doc.content = self._json_to_text(data)
                doc.metadata = {"keys": list(data.keys())}
            elif isinstance(data, list):
                doc.title = path.stem
                doc.content = self._json_to_text(data)
                doc.metadata = {"item_count": len(data)}
            else:
                doc.content = str(data)

        except json.JSONDecodeError as e:
            doc.metadata = {"error": str(e)}
            doc.content = content

        return doc

    def _json_to_text(self, data: Any, depth: int = 0) -> str:
        """JSON을 읽기 쉬운 텍스트로 변환"""
        lines = []
        indent = "  " * depth

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{indent}{key}:")
                    lines.append(self._json_to_text(value, depth + 1))
                else:
                    lines.append(f"{indent}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    lines.append(f"{indent}- item {i + 1}:")
                    lines.append(self._json_to_text(item, depth + 1))
                else:
                    lines.append(f"{indent}- {item}")
        else:
            lines.append(f"{indent}{data}")

        return "\n".join(lines)

    def parse_directory(
        self,
        directory: str,
        recursive: bool = True,
        extensions: list[str] = None
    ) -> list[ParsedDocument]:
        """디렉토리 내 모든 문서 파싱"""
        path = Path(directory)

        if not path.exists():
            raise FileNotFoundError(f"디렉토리를 찾을 수 없습니다: {directory}")

        if extensions is None:
            extensions = list(self.SUPPORTED_EXTENSIONS)
        else:
            extensions = [f".{e}" if not e.startswith(".") else e for e in extensions]

        documents = []
        pattern = "**/*" if recursive else "*"

        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                try:
                    doc = self.parse(str(file_path))
                    documents.append(doc)
                except Exception as e:
                    print(f"파싱 실패: {file_path} - {e}")

        return documents

    def get_supported_extensions(self) -> list[str]:
        """지원하는 확장자 목록"""
        return list(self.SUPPORTED_EXTENSIONS)
