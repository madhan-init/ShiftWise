# DESIGN — ShiftWise / Examate RAG

## API Endpoints

| Method | Path | Request Body | Response | Status Codes |
|--------|------|-------------|----------|-------------|
| GET | `/health` | — | `{ status, app, environment }` | 200 |
| POST | `/ask` | `{ question, version?, top_k? }` | `{ answer, model, fallback_used, version, citations[] }` | 200, 422, 502 |
| GET | `/usage` | — | `{ total_calls, total_input_tokens, total_output_tokens, total_cost_usd, fallback_calls, by_model[] }` | 200 |

### POST /ask

Executes the ShiftWise RAG pipeline:
1. Generates dense embeddings for the user query using the configured embedder (Gemini or Ollama).
2. Performs vector similarity search in PostgreSQL (`pgvector`), strictly filtered by `version` when specified for version isolation.
3. Constructs a structured prompt with retrieved context chunks, each annotated with `[document, Page X]`.
4. Dispatches the prompt to the LLM (Gemini with fallback to Gemini 1.5 Flash 8B, or Ollama).
5. Cross-checks citations in the LLM answer against retrieved chunks to ensure verified page-level citations.
6. Returns 502 if primary and fallback models fail. Log call and token metrics into SQLite usage database.

### GET /usage

Aggregates all rows from the `llm_usage` table. `by_model` breaks down calls, tokens, and cost per model.

---

## Tables

### llm_usage (SQLite)

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | INTEGER | autoincrement | Primary key |
| ts | TEXT | current UTC timestamp | ISO 8601 timestamp |
| model | TEXT | — | Model name used |
| input_tokens | INTEGER | 0 | Prompt tokens (prompt_eval_count) |
| output_tokens | INTEGER | 0 | Completion tokens (eval_count) |
| cost_usd | REAL | 0.0 | Calculated cost |
| fallback_used | INTEGER | 0 | 1 if fallback model was used |
| latency_ms | REAL | 0.0 | Round-trip time in milliseconds |
| status | TEXT | ok | `ok` or `error` |

### chunks (PostgreSQL + pgvector)

Stores parsed 50-line page chunks of Spring Boot source files with 768-dimensional Ollama embeddings.

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | BIGSERIAL | autoincrement | Primary key |
| version | VARCHAR(20) | — | Framework release version (`2.7`, `3.3`, `3.5`) |
| document | VARCHAR(500) | — | Relative source file path |
| page | INTEGER | — | 1-based page number (50 lines = 1 page) |
| heading | TEXT | — | Active class or method heading for page |
| start_line | INTEGER | — | Starting line in file |
| end_line | INTEGER | — | Ending line in file |
| content | TEXT | — | Raw code chunk content |
| embedding | vector(768) | — | Ollama `nomic-embed-text` dense vector |
| metadata | JSONB | `'{}'::jsonb` | Additional file & AST attributes |
| created_at | TIMESTAMPTZ | `NOW()` | Ingestion timestamp |

- **Indexes:**
  - `idx_chunks_version` on `version` (version locking)
  - `idx_chunks_document` on `document`
  - `idx_chunks_version_page` on `(version, document, page)`
  - `idx_chunks_embedding` HNSW index using cosine distance (`vector_cosine_ops`)

---

## LLM Provider

Supports **Gemini** (hosted via Google AI Studio API) as the default provider and **Ollama** as a local provider. Selected via `LLM_PROVIDER` setting (`gemini` or `ollama`).

Both providers implement the `LLMProvider` abstract base class with automatic retry, timeout handling, and fallback model switching on failures.

### Settings

| Env Var | Default | Description |
|---------|---------|-------------|
| LLM_PROVIDER | gemini | `gemini` or `ollama` |
| GEMINI_API_KEY | *(required for gemini)* | Google Gemini API Key |
| GEMINI_MODEL | gemini-1.5-flash | Primary Gemini model |
| GEMINI_FALLBACK_MODEL | gemini-1.5-flash-8b | Fallback Gemini model |
| GEMINI_INPUT_PRICE_PER_MILLION | 0.075 | USD cost per 1M input tokens |
| GEMINI_OUTPUT_PRICE_PER_MILLION | 0.30 | USD cost per 1M output tokens |
| OLLAMA_BASE_URL | http://localhost:11434 | Ollama server URL |
| OLLAMA_MODEL | llama3.1:8b | Primary Ollama model |
| OLLAMA_FALLBACK_MODEL | llama3.1:8b | Fallback Ollama model |
| LLM_TIMEOUT_SECONDS | 60 | Request timeout in seconds |
| USAGE_DB_PATH | ./usage.db | SQLite database for usage tracking |

