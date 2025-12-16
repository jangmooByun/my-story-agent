"""CSV 파일 파서"""

import csv
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from io import StringIO


@dataclass
class CSVDocument:
    """파싱된 CSV 문서"""
    file_path: str
    title: Optional[str] = None
    content: str = ""
    raw_content: str = ""
    metadata: dict = field(default_factory=dict)
    sections: list[dict] = field(default_factory=list)

    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    data: list[dict] = field(default_factory=list)


class CSVParserTool:
    """CSV 파일 파서"""

    name: str = "csv_parser"
    description: str = "CSV 파일(.csv) 파싱"

    def parse(
        self,
        file_path: str,
        encoding: str = 'utf-8',
        delimiter: str = ',',
        has_header: bool = True
    ) -> CSVDocument:
        """CSV 파일 파싱"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        raw_content = self._read_with_fallback(path, encoding)

        doc = CSVDocument(
            file_path=str(path.absolute()),
            raw_content=raw_content
        )

        reader = csv.reader(StringIO(raw_content), delimiter=delimiter)
        all_rows = list(reader)

        if not all_rows:
            doc.title = path.stem
            return doc

        if has_header:
            doc.headers = all_rows[0]
            doc.rows = all_rows[1:]
        else:
            doc.headers = [f"col_{i}" for i in range(len(all_rows[0]))]
            doc.rows = all_rows

        doc.data = [
            dict(zip(doc.headers, row))
            for row in doc.rows
        ]

        doc.title = doc.headers[0] if doc.headers else path.stem
        doc.content = self._create_text_content(doc)

        doc.metadata = {
            "row_count": len(doc.rows),
            "column_count": len(doc.headers),
            "headers": doc.headers,
            "delimiter": delimiter,
            "encoding": encoding
        }

        doc.sections = self._create_sections(doc)

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

    def _create_text_content(self, doc: CSVDocument) -> str:
        """텍스트 콘텐츠 생성 (분석용)"""
        lines = []

        if doc.headers:
            lines.append(" | ".join(doc.headers))
            lines.append("-" * 40)

        for row in doc.rows[:100]:
            lines.append(" | ".join(str(cell) for cell in row))

        if len(doc.rows) > 100:
            lines.append(f"... ({len(doc.rows) - 100}개 행 생략)")

        return "\n".join(lines)

    def _create_sections(self, doc: CSVDocument) -> list[dict]:
        """섹션 생성 (각 행을 섹션으로)"""
        sections = []

        for i, row_dict in enumerate(doc.data[:50]):
            first_value = list(row_dict.values())[0] if row_dict else f"Row {i + 1}"

            sections.append({
                "index": i,
                "title": str(first_value)[:50],
                "content": " | ".join(f"{k}: {v}" for k, v in row_dict.items()),
                "data": row_dict
            })

        return sections

    def get_column(self, doc: CSVDocument, column_name: str) -> list:
        """특정 열의 값들 추출"""
        if column_name not in doc.headers:
            raise ValueError(f"존재하지 않는 열: {column_name}")

        return [row.get(column_name) for row in doc.data]

    def filter_rows(
        self,
        doc: CSVDocument,
        column: str,
        value: str,
        exact: bool = True
    ) -> list[dict]:
        """조건에 맞는 행 필터링"""
        result = []

        for row in doc.data:
            cell_value = str(row.get(column, ""))

            if exact:
                if cell_value == value:
                    result.append(row)
            else:
                if value.lower() in cell_value.lower():
                    result.append(row)

        return result

    def to_markdown_table(self, doc: CSVDocument, max_rows: int = 20) -> str:
        """마크다운 테이블로 변환"""
        if not doc.headers:
            return ""

        lines = []
        lines.append("| " + " | ".join(doc.headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(doc.headers)) + " |")

        for row in doc.rows[:max_rows]:
            lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

        if len(doc.rows) > max_rows:
            lines.append(f"\n*... {len(doc.rows) - max_rows}개 행 생략*")

        return "\n".join(lines)
