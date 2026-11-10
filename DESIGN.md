# DESIGN — ShiftWise / Examate RAG

## API Endpoints

| Method | Path | Request Body | Response | Status Codes |
|--------|------|-------------|----------|-------------|
| GET | `/health` | — | `{ status, app, environment }` | 200 |
| POST | `/ask` | `{ question }` | `{ answer, model, fallback_used }` | 200, 422, 502 |
| GET | `/usage` | — | `{ total_calls, total_input_tokens, total_output_tokens, total_cost_usd, fallback_calls, by_model[] }` | 200 |

### POST /ask

Sends the question to the configured LLM provider (Ollama by default). If the primary model fails (timeout, connection error, 5xx), retries once on the fallback model. Returns 502 if both fail.

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

