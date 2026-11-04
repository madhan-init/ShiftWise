# Progress

Commit after every class. Tag every Friday: `git tag week-N && git push origin week-N`.

## Week 1 (tag week-1 by Fri 23 Oct)
- [x] Repo created from the Examate template and registered on the form
- [x] README top section filled from my project card
- [x] /health runs locally
- [x] docs/QUESTIONS.md: 10 real questions
- [x] 50+ pages collected, DATASET.md filled, sample in data/sample/
- [x] Tag week-1 pushed

## Week 2 (tag week-2 by Fri 30 Oct)
- [x] POST /chat calls an LLM and returns structured JSON
- [x] Streaming, timeouts, retry and a fallback model
- [x] Cost log + GET /usage
- [x] Docker Compose (API + Postgres/pgvector) runs
- [x] CI green, live link in README
- [x] Tag week-2 pushed

## Week 3 (tag week-3 by Fri 6 Nov)
- [ ] Parser keeps page numbers and headings
- [ ] 500+ pages chunked, embedded and stored in pgvector
- [ ] POST /ask answers with [document, page] citations
- [ ] docs/EVAL_v0.md with my 10 questions scored
- [ ] Tag week-3 pushed

## Daily log
| Date | What I did today | Commit |
|---|---|---|
| 21 Oct 2026 | Initialized repository from Examate template, /health route, Dockerfile, and CI workflow | d669627 |
| 21 Oct 2026 | Added README with project description and problem statement | e89e9dc |
| 22 Oct 2026 | Collected Spring Boot source code samples (2.7.18, 3.3.13, 3.5.16) in data/sample/ | 4c5a75f |
| 22 Oct 2026 | Documented dataset details and licenses in DATASET.md | a6d96c8 |
| 22 Oct 2026 | Updated README with framework version change clarifications | aeefb14 |
| 24 Oct 2026 | Added 10 evaluation questions and setup instructions in README (tag week-1) | d82e2ef |
| 29 Oct 2026 | Implemented LLM client with Ollama provider, retry, fallback, and tests | 2e62a8e |
| 29 Oct 2026 | Added /ask and /usage endpoints with Pydantic schemas | a9f5f5b |
| 31 Oct 2026 | Added SQLite usage storage (llm_usage table) and full endpoint test suite | 41fb098 |
| 31 Oct 2026 | Updated .env.example with LLM and database settings | f2a757c |
| 01 Nov 2026 | Created DESIGN.md with API endpoints and database schema | 541e473 |
| 01 Nov 2026 | Resolved ruff lint checks across codebase | 75cdc37 |
| 01 Nov 2026 | Fixed CI runner pytest module path in pyproject.toml (tag week-2) | b8b51f6 |
| 03 Nov 2026 | Streaming /chat, safe retries, fallback model, cost log, GET /usage (refactored to app/llm) | e156957 |
| 03 Nov 2026 | Docker Compose (API + pgvector), /ready route, .dockerignore | adac692 |
| 04 Nov 2026 | CI workflow (test + docker-smoke), pre-commit hooks, deployed to Render, live link in README | 49b430f |
