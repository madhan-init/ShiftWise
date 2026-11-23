from __future__ import annotations

import logging
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from app.config import Settings, get_settings
from app.llm import LLMResult, complete, get_embedder
from app.vector_db import search_chunks

logger = logging.getLogger(__name__)

CITATION_REGEX = re.compile(r"\[([^,\]]+),\s*Page\s*(\d+)\]", re.IGNORECASE)


def normalize_version(version: str | None) -> str | None:
    """Normalize version string e.g. '3.3.13' -> '3.3'."""
    if not version:
        return None
    parts = version.strip().split(".")
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}"
    return version.strip()


def format_citation(document: str, page: int) -> str:
    """Format citation tag as [filename, Page X]."""
    doc_name = Path(document).name
    return f"[{doc_name}, Page {page}]"


def extract_citations(text: str) -> list[str]:
    """Extract all [document, Page X] citation tags from a text string."""
    matches = CITATION_REGEX.findall(text)
    citations = []
    seen = set()
    for doc, page in matches:
        tag = f"[{doc.strip()}, Page {page.strip()}]"
        if tag not in seen:
            seen.add(tag)
            citations.append(tag)
    return citations


def build_rag_prompt(
    question: str,
    chunks: list[dict[str, Any]],
    version: str | None = None,
) -> str:
    """Construct prompt with retrieved context chunks, version constraints, and citation rules."""
    context_blocks = []
    for idx, c in enumerate(chunks, start=1):
        citation = format_citation(c["document"], c["page"])
        ver = c.get("version", "unknown")
        heading = c.get("heading") or "Code snippet"
        block = (
            f"--- Context {idx}: {citation} (Version: {ver}, Scope: {heading}) ---\n"
            f"{c['content'].strip()}\n"
        )
        context_blocks.append(block)

    context_text = "\n".join(context_blocks)
    ver_str = version or "Any (check each chunk's version)"

    prompt = f"""You are ShiftWise, an expert AI assistant specializing in Spring Boot code migration and version differences.

### INSTRUCTIONS:
1. Answer the developer's question accurately using ONLY the provided Spring Boot source code and configuration chunks.
2. CITATION REQUIREMENT: For every fact, property name, class, import, or code change you state, you MUST cite the exact source using the citation tag provided in the context, formatted exactly as: [DocumentName, Page X].
3. STRICT VERSION ISOLATION:
   - Target version requested: {ver_str}.
   - Rely strictly on code tagged with this version.
   - Do NOT cite or mix code from unrequested versions unless the question explicitly asks for a comparison between two versions.
4. OUT-OF-SCOPE / UNANSWERABLE QUESTIONS:
   - If a class, property, or concept cannot be found in the provided Spring Boot source context (e.g. it belongs to external libraries like Spring Security, Spring Cloud, or was removed), state explicitly:
     "This class/property is not found in the indexed Spring Boot source code for version {ver_str}."
   - Do NOT guess, invent, or hallucinate citations.

### RETRIEVED CONTEXT CHUNKS:
{context_text}

### DEVELOPER QUESTION:
{question}

### ANSWER:"""
    return prompt


def query_rag(
    question: str,
    version: str | None = None,
    top_k: int = 5,
    settings: Settings | None = None,
    completer: Callable[..., LLMResult] | None = None,
) -> tuple[LLMResult, list[str]]:
    """Execute RAG pipeline: retrieve chunks, build prompt with citations, call LLM, and verify citations."""
    settings = settings or get_settings()
    call_llm = completer or complete
    norm_version = normalize_version(version)

    chunks: list[dict[str, Any]] = []
    try:
        embedder = get_embedder(settings)
        query_embedding = embedder.embed_text(question)
        chunks = search_chunks(
            query_embedding,
            version=norm_version,
            top_k=top_k,
            database_url=settings.database_url,
        )
    except Exception as exc:
        logger.warning("Vector retrieval failed or unavailable (%s). Falling back to direct LLM.", exc)

    if chunks:
        valid_citations = {format_citation(c["document"], c["page"]) for c in chunks}
        prompt = build_rag_prompt(question, chunks, version=norm_version)
        result = call_llm(prompt)

        # Extract and verify citations from the LLM answer
        cited_in_text = extract_citations(result.text)
        verified = [c for c in cited_in_text if c in valid_citations]

        # If model used context but omitted brackets, include the top chunk citation as reference
        if not verified and chunks:
            top_chunk = chunks[0]
            verified.append(format_citation(top_chunk["document"], top_chunk["page"]))

        return result, verified

    # Fallback to direct completion if no chunks were found or DB is not initialized
    result = call_llm(question)
    return result, []
