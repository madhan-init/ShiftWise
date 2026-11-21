"""Tests for app.parser — Fixed-line code chunker with page numbers and headings."""

from pathlib import Path

from app.parser import CodeChunk, parse_file

SAMPLE_JAVA = """package com.example;

import org.springframework.boot.autoconfigure.AutoConfiguration;

@AutoConfiguration
public class SampleAutoConfiguration {

    public SampleAutoConfiguration() {
    }

    public String firstMethod() {
        return "first";
    }

    public void secondMethod() {
        System.out.println("second");
    }
}
"""


def test_parse_file_page_and_heading(tmp_path: Path):
    test_file = tmp_path / "SampleAutoConfiguration.java"
    # Create a 120-line file to test multi-page chunking (50 lines per page -> 3 pages)
    lines = [f"// line {i}" for i in range(1, 121)]
    lines[5] = "public class SampleAutoConfiguration {"
    lines[30] = "    public void methodA() {"
    lines[75] = "    public void methodB() {"
    test_file.write_text("\n".join(lines), encoding="utf-8")

    chunks = parse_file(test_file, version="3.3", page_size_lines=50)

    assert len(chunks) == 3
    # Page 1 (lines 1 - 50)
    assert chunks[0].page == 1
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 50
    assert chunks[0].version == "3.3"
    assert chunks[0].to_citation() == "[SampleAutoConfiguration.java, Page 1]"
    assert "SampleAutoConfiguration" in chunks[0].heading

    # Page 2 (lines 51 - 100)
    assert chunks[1].page == 2
    assert chunks[1].start_line == 51
    assert chunks[1].end_line == 100
    assert chunks[1].to_citation() == "[SampleAutoConfiguration.java, Page 2]"

    # Page 3 (lines 101 - 120)
    assert chunks[2].page == 3
    assert chunks[2].start_line == 101
    assert chunks[2].end_line == 120
    assert chunks[2].to_citation() == "[SampleAutoConfiguration.java, Page 3]"


def test_code_chunk_citation_format():
    chunk = CodeChunk(
        version="2.7",
        document="org/springframework/boot/autoconfigure/DataSourceAutoConfiguration.java",
        page=4,
        heading="class DataSourceAutoConfiguration",
        start_line=151,
        end_line=200,
        content="// code",
        metadata={},
    )
    assert chunk.to_citation() == "[DataSourceAutoConfiguration.java, Page 4]"
