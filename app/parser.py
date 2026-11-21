from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CLASS_PATTERN = re.compile(
    r"^\s*(?:public\s+|protected\s+|private\s+)?(?:abstract\s+|final\s+|static\s+)*"
    r"(?:class|interface|enum|record|@interface)\s+([A-Za-z0-9_]+)"
)
METHOD_PATTERN = re.compile(
    r"^\s*(?:public\s+|protected\s+|private\s+)?(?:abstract\s+|final\s+|static\s+|default\s+)*"
    r"(?:<[^>]+>\s+)?([A-Za-z0-9_<>\[\]]+)\s+([A-Za-z0-9_]+)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{?"
)


@dataclass
class CodeChunk:
    version: str
    document: str
    page: int
    heading: str
    start_line: int
    end_line: int
    content: str
    metadata: dict[str, Any]

    def to_citation(self) -> str:
        """Returns standard citation format: [document, Page X]."""
        doc_name = Path(self.document).name
        return f"[{doc_name}, Page {self.page}]"


def parse_file(
    file_path: Path | str,
    *,
    version: str,
    base_dir: Path | str | None = None,
    page_size_lines: int = 50,
) -> list[CodeChunk]:
    """
    Parses a source file into fixed-line pages (e.g. 50 lines = 1 page).
    Maintains active class/method/section heading and line numbers.
    """
    path = Path(file_path)
    if not path.is_file():
        return []

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    lines = text.splitlines()
    if not lines:
        return []

    if base_dir:
        try:
            rel_doc = str(path.relative_to(base_dir)).replace("\\", "/")
        except ValueError:
            rel_doc = path.name
    else:
        rel_doc = path.name

    chunks: list[CodeChunk] = []
    total_lines = len(lines)
    total_pages = (total_lines + page_size_lines - 1) // page_size_lines

    current_class = ""
    current_method = ""

    for page_idx in range(total_pages):
        start_line = page_idx * page_size_lines + 1
        end_line = min((page_idx + 1) * page_size_lines, total_lines)
        page_lines = lines[start_line - 1 : end_line]

        # Scan for headings in this slice or carry over from previous slice
        page_heading = ""
        for line in page_lines:
            c_match = CLASS_PATTERN.search(line)
            if c_match:
                current_class = c_match.group(1)
                page_heading = f"class {current_class}"

            m_match = METHOD_PATTERN.search(line)
            if m_match and not line.strip().startswith("//"):
                method_name = m_match.group(2)
                # Filter out control structures that look like methods
                if method_name not in {"if", "for", "while", "switch", "catch"}:
                    current_method = method_name
                    if current_class:
                        page_heading = f"{current_class}#{current_method}()"
                    else:
                        page_heading = f"{current_method}()"

        if not page_heading:
            if current_class and current_method:
                page_heading = f"{current_class}#{current_method}()"
            elif current_class:
                page_heading = f"class {current_class}"
            else:
                page_heading = path.stem

        content = "\n".join(page_lines)

        chunks.append(
            CodeChunk(
                version=version,
                document=rel_doc,
                page=page_idx + 1,
                heading=page_heading,
                start_line=start_line,
                end_line=end_line,
                content=content,
                metadata={
                    "file_name": path.name,
                    "extension": path.suffix,
                    "total_pages": total_pages,
                    "total_lines": total_lines,
                },
            )
        )

    return chunks
