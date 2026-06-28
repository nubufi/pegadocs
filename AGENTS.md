# AGENTS.md

This file provides guidance to Codex and other coding agents when working with code in this repository.

## Project Overview

PegaDocs is an open-source knowledge management platform. Users connect their own LLM/embedding providers (Azure OpenAI, OpenRouter, Bedrock, etc.), vector stores (Pinecone, pgvector, ChromaDB, etc.), and data sources (SharePoint, S3, Google Drive, GitHub, Jira, etc.), then query those knowledge bases via chatbot, Teams bot, Telegram bot, etc.

## Repository Structure

```text
pegadocs/
├── UI/                          # Next.js 16 frontend (React 19, Tailwind v4, pnpm)
├── pegadocs-website-redesign/   # HTML/CSS design prototypes from Claude Design export
└── app/                         # FastAPI backend package and Python project root
```

## Frontend (UI/)

**Stack:** Next.js 16, React 19, TypeScript, Tailwind CSS v4, pnpm

```bash
cd UI
pnpm install       # install dependencies
pnpm dev           # start dev server (localhost:3000)
pnpm build         # production build
pnpm lint          # ESLint
```

The `pegadocs-website-redesign/project/` folder contains HTML prototype files (`PegaDocs Site.dc.html`, `PegaDocs Console.dc.html`, `PegaDocs Auth.dc.html`) that serve as the pixel-perfect design reference for implementing the Next.js UI. Implement from the HTML source; do not copy prototype structure, just match the visual output.

## Backend (FastAPI)

**Stack:** Python 3.13, FastAPI, LlamaIndex, uv, Supabase (auth + metadata), pytest

All backend commands run from the `app/` directory. Always use `uv` to run Python code and tools; do not call `python`, `python3`, `pip`, `pytest`, `ruff`, or `uvicorn` directly.

```bash
cd app
uv sync                            # install dependencies
make run                           # start API on :8000 with hot reload
make test                          # run all tests (requires 100% coverage)
make lint                          # ruff check
make format                        # ruff format

# Run a specific test file
uv run pytest tests/unit/test_chat_service.py -v

# Run with coverage but without the 100% threshold (useful during dev)
uv run pytest tests/ -v --cov=. --cov-report=term-missing

# Start with mock API (no Supabase/vector store/LLM needed)
PYTHONPATH=.. ENABLE_MOCK_API=true uv run uvicorn app.main:create_application --factory --reload
```

Mock login: `demo@pegadocs.local` / `demo1234`. Pass returned token as `Authorization: Bearer <token>`.

## Backend Architecture

The backend follows a clean three-layer architecture:

```text
app/
├── presentation/     # FastAPI routers, controllers, Pydantic schemas
├── application/      # Business logic services + Protocol interfaces
│   ├── protocols/    # Python Protocol classes (interfaces) for all adapters
│   └── services/     # Orchestration: chat, collection, embedding, auth, etc.
├── infra/
│   ├── adapters/     # Concrete implementations of protocols
│   │   ├── readers/        # Data source connectors (S3, SharePoint, GitHub, etc.)
│   │   ├── vector_stores/  # Vector DB adapters (Postgres/pgvector, Pinecone, Chroma, S3)
│   │   ├── chat_stores/    # Chat history backends (Postgres, Redis, DynamoDB)
│   │   └── models/         # LLM/embedding adapters (currently Azure OpenAI)
│   ├── factories/    # Factory classes that select the right adapter at runtime
│   └── utils/        # Shared helpers (Supabase queries, encryption, token counting)
├── tasks/            # Background embedding + scan jobs
└── lambdas/          # AWS Lambda handlers for async document processing
```

### Key Extension Points

All pluggable components use Python `Protocol` classes in `app/application/protocols/`. To add a new provider:

- **Vector store**: implement `VectorStoreProtocol`, add to `VectorStoreFactory` (`infra/factories/vector_store.py`), keyed by `database_type` string.
- **Data source / reader**: implement `ReaderProtocol`, register in `reader_map` in `infra/factories/reader.py`, keyed by `data_source.type` string.
- **LLM/embedding model**: implement the model adapter, add a provider branch in `ModelFactory` (`infra/factories/models.py`), keyed by `model.provider` string.
- **Chat store**: implement `ChatStoreProtocol`, update `ChatStoreFactory`.

### Data Flow

1. User attaches a **data source** -> `reader_service` calls the matching `ReaderProtocol` adapter to fetch documents -> documents chunked and persisted as embedding job nodes.
2. **Embedding job** (background task or Lambda) picks up nodes -> calls the user's embedding model -> stores vectors in the user's vector store via `VectorStoreProtocol`.
3. **Chat** request -> `chat_service` retrieves the `VectorStoreIndex` for the collection -> runs RAG query against the user's LLM -> streams response.

### Configuration

All config is in `app/infra/config.py` via pydantic-settings, loaded from `.env`. Key groups:

- `SUPABASE_*` - metadata DB and auth
- `REDIS_*` / `DDB_TABLE` - task store (switchable via `TASK_STORE=redis|dynamodb`)
- `S3_*`, `AWS_*` - S3 file storage and Lambda triggers
- `SENTRY_DSN`, `LOGFIRE_*` - observability
- `FERNET_SECRET_KEY` - used to encrypt/decrypt user-supplied credentials stored in Supabase

User-supplied provider credentials (API keys, connection strings) are always encrypted with Fernet before being stored in Supabase and decrypted at runtime via `infra/utils/encrypt_utils.py`.

### Testing

Tests require a `.env` file at the backend root. The test suite enforces 100% coverage (`--cov-fail-under=100`). Tests are organised as `app/tests/unit/` and `app/tests/routers/` (integration-style, using FastAPI `TestClient`). The `conftest.py` loads `.env` automatically.
