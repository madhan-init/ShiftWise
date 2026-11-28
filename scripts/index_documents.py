"""CLI script to parse, chunk, embed, and store Spring Boot source pages into Postgres + pgvector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.config import get_settings
from app.parser import parse_file


def find_source_files(base_dir: Path, version_tag: str) -> list[Path]:
    """Finds key Java and configuration files, prioritizing autoconfigure module."""
    raw_dir = base_dir / f"spring-boot-{version_tag}"
    sample_dir = base_dir.parent / "sample" / f"spring-boot-{version_tag}"

    target_dir = raw_dir if raw_dir.exists() else sample_dir
    if not target_dir.exists():
        return []

    # Prioritize autoconfigure module
    auto_dir = target_dir / "spring-boot-project" / "spring-boot-autoconfigure"
    search_root = auto_dir if auto_dir.exists() else target_dir

    files: list[Path] = []
    # Collect Java source files
    files.extend(sorted(search_root.rglob("*.java")))
    # Collect property and factories metadata files
    files.extend(sorted(search_root.rglob("*.factories")))
    files.extend(sorted(search_root.rglob("*.imports")))
    files.extend(sorted(search_root.rglob("additional-spring-configuration-metadata.json")))

    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="Index Spring Boot documents into Postgres + pgvector")
    parser.add_argument(
        "--versions",
        nargs="+",
        default=["2.7.18", "3.3.13", "3.5.16"],
        help="Spring Boot versions to index",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory containing Spring Boot source folders",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=50,
        help="Number of lines per page (default: 50)",
    )
    parser.add_argument(
        "--limit-pages",
        type=int,
        default=600,
        help="Maximum total pages to index across versions (default: 600)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and count pages without embedding or connecting to database",
    )
    args = parser.parse_args()

    settings = get_settings()
    data_dir = args.data_dir
    print("=== ShiftWise Document Indexing Pipeline ===")
    print(f"Source Directory: {data_dir}")
    print(f"Versions to process: {', '.join(args.versions)}")
    print(f"Page size: {args.page_size} lines per page")
    print(f"Embedding Model: {settings.ollama_embed_model} (768-dim)")
    print()

    pages_per_version = max(1, args.limit_pages // len(args.versions))
    all_chunks = []
    for ver in args.versions:
        # Normalize version string (e.g. 2.7.18 -> 2.7)
        short_ver = ".".join(ver.split(".")[:2])
        files = find_source_files(data_dir, ver)
        print(f"Found {len(files)} files for Spring Boot {ver} ({short_ver})")

        ver_chunks = []
        for file in files:
            chunks = parse_file(file, version=short_ver, page_size_lines=args.page_size)
            ver_chunks.extend(chunks)
            if len(ver_chunks) >= pages_per_version:
                ver_chunks = ver_chunks[:pages_per_version]
                break

        print(f"  -> Generated {len(ver_chunks)} pages/chunks for version {short_ver}")
        all_chunks.extend(ver_chunks)

    print()
    print(f"Total Pages Parsed: {len(all_chunks)}")
    if all_chunks:
        mid_idx = len(all_chunks) // 2
        print(f"Sample Citation (start): {all_chunks[0].to_citation()} | {all_chunks[0].heading}")
        print(f"Sample Citation (mid):   {all_chunks[mid_idx].to_citation()} | {all_chunks[mid_idx].heading}")

    if args.dry_run:
        print("\n[Dry Run Completed] No database writes or embeddings requested.")
        return

    if not all_chunks:
        print("No chunks found. Check your data directories.")
        sys.exit(1)

    # Initialize Postgres & Embeddings
    print("\nConnecting to PostgreSQL & initializing pgvector extension...")
    from app.llm.embeddings import get_embedder
    from app.vector_db import init_vector_db, insert_chunks

    try:
        init_vector_db()
        print("PostgreSQL chunks table and indexes verified.")
    except Exception as exc:
        print(f"Database connection error: {exc}")
        print("Is PostgreSQL running? Start it via 'docker compose up -d db'.")
        sys.exit(1)

    embedder = get_embedder()
    embedder_name = type(embedder).__name__
    print(f"Embedding {len(all_chunks)} chunks with {embedder_name} (768-dim)...")

    batch_size = 20
    chunks_to_insert = []
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        texts = [c.content for c in batch]
        try:
            embeddings = embedder.embed_batch(texts)
        except Exception as exc:
            print(f"Embedding error: {exc}")
            sys.exit(1)

        for chunk, emb in zip(batch, embeddings):
            chunks_to_insert.append(
                {
                    "version": chunk.version,
                    "document": chunk.document,
                    "page": chunk.page,
                    "heading": chunk.heading,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "content": chunk.content,
                    "embedding": emb,
                    "metadata": chunk.metadata,
                }
            )
        print(f"  Embedded {min(i + batch_size, len(all_chunks))}/{len(all_chunks)} chunks...", end="\r")

    print("\nStoring chunks into PostgreSQL + pgvector...")
    inserted = insert_chunks(chunks_to_insert)
    print(f"Successfully inserted {inserted} chunks with page-level citations into pgvector!")


if __name__ == "__main__":
    main()

