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
- [ ] Docker Compose (API + Postgres/pgvector) runs
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
| 2026-10-29 | Implemented LLM client with Ollama provider, retry, fallback, and tests | 2e62a8e |
| 2026-10-29 | Added /ask and /usage endpoints with Pydantic schemas | a9f5f5b |
| 2026-10-31 | Added SQLite usage storage (llm_usage table) and full endpoint test suite | 41fb098 |
| 2026-10-31 | Updated .env.example with LLM and database settings | f2a757c |
| 2026-11-01 | Created DESIGN.md with API endpoints and database schema | 541e473 |
| 2026-11-01 | Resolved ruff lint checks across codebase | 75cdc37 |
| 2026-11-01 | Fixed CI runner pytest module path in pyproject.toml | b8b51f6 |
| 2026-11-03 | Refactored LLM module into modular app/llm package | e156957 |
