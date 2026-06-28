# PegaDocs

Open-source knowledge management platform. Connect your own LLM, embedding provider, vector store, and data sources — then query your knowledge base through a chatbot, Teams bot, or Telegram bot.

## Architecture

```text
┌─────────────────────────────────────────────────────────┐
│  Chat Clients (Web · Teams · Telegram · Slack)          │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  UI / Next.js 16       port 3000                        │
│  Marketing site + Console dashboard                     │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  API / FastAPI         port 8000                        │
│  ┌───────────┐  ┌──────────┐  ┌──────────────────┐     │
│  │ Auth      │  │ Chat     │  │ Collection Mgmt  │     │
│  │ (Supabase │  │ (RAG +   │  │ (data sources,   │     │
│  │  or local)│  │  stream) │  │  embeddings)     │     │
│  └───────────┘  └──────────┘  └────────┬─────────┘     │
│                                        │                │
└────────────────────────────────────────┼────────────────┘
                                         │
                      ┌──────────────────┴──────────────┐
                      │  Celery Workers (Redis broker)   │
                      │  Parallel embedding pipeline      │
                      │  Chunk → Embed → Vector Store    │
                      └──────────────────┬──────────────┘
                                         │
└──────┬────────────────┬──────────────────┼──────────────┘
       ▼                ▼                  ▼
┌──────────┐   ┌──────────────┐   ┌──────────────────┐
│ Postgres │   │ Vector Store │   │ LLM / Embedding  │
│ (pgvector│   │ (Pinecone ·  │   │ (Azure OpenAI ·  │
│  · meta) │   │  Chroma · S3)│   │  OpenRouter ·    │
│          │   │              │   │  Bedrock)        │
└──────────┘   └──────────────┘   └──────────────────┘
```

### Pluggable Adapters

Every integration point uses Python `Protocol` classes. Bring your own:

- **LLM & Embeddings** — Azure OpenAI, OpenRouter, AWS Bedrock, or any OpenAI-compatible API
- **Vector Stores** — pgvector (Postgres), Pinecone, ChromaDB, S3-backed
- **Data Sources** — SharePoint, S3, Google Drive, GitHub, Jira, Confluence, Web scraping
- **Chat Stores** — Postgres, Redis, DynamoDB
- **Auth** — Supabase (JWT passthrough) or local (SQLAlchemy + bcrypt + JWT)
- **Task Queues** — Redis or DynamoDB

## Quick Start

### Prerequisites

- Docker & Docker Compose

### Run Everything

```bash
git clone https://github.com/nubufi/pegadocs.git
cd pegadocs
docker compose up --build
```

This starts five services:

| Service         | Port | Description                              |
|-----------------|------|------------------------------------------|
| `ui`            | 3000 | Next.js frontend (marketing + console)   |
| `app`           | 8000 | FastAPI backend                          |
| `postgres`      | 5432 | PostgreSQL 17 with pgvector extension    |
| `redis`         | 6379 | Message broker for Celery task queue     |
| `celery_worker` | —    | Async workers (embedding pipeline, 2 replicas) |

### Mock API Mode (no external services needed)

The backend supports a mock API mode that skips all external dependencies — perfect for UI development. Set in `app/.env`:

```env
ENABLE_MOCK_API=true
AUTH_PROVIDER=local
DB_URL=postgresql+asyncpg://pegadocs:pegadocs@postgres:5432/pegadocs
LOCAL_AUTH_JWT_SECRET=dev-secret-change-in-production
```

Mock login credentials: `demo@pegadocs.local` / `demo1234`

## Development Setup (without Docker)

### Backend

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
cd app
cp .env.example .env      # edit with your values
uv sync
uv run uvicorn app.main:create_application --factory --reload
```

API runs at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

Useful commands:

```bash
make test     # run all tests with coverage
make lint     # ruff check
make format   # ruff format
```

For embedding pipeline parallelism, start a Celery worker (requires Redis):

```bash
celery -A app.tasks.celery_app worker --concurrency=4 --loglevel=info
```

Or run everything with Docker Compose (includes Redis + 2 worker replicas).

### Frontend

Requires Node.js 22+ and [pnpm](https://pnpm.io/).

```bash
cd UI
pnpm install
pnpm dev
```

UI runs at `http://localhost:3000`.

## Configuration

All backend configuration lives in `app/.env`. Copy the example file and fill in your values:

```bash
cp app/.env.example app/.env
```

### Required

| Variable              | Example                      | Purpose                      |
|-----------------------|------------------------------|------------------------------|
| `FERNET_SECRET_KEY`   | (generate below)             | Encrypts user credentials    |
| `AUTH_PROVIDER`       | `supabase` or `local`        | Auth backend selection       |

Generate a Fernet key:

```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Auth Backend

**Supabase** (default):

```env
AUTH_PROVIDER=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

**Local** (built-in):

```env
AUTH_PROVIDER=local
DB_URL=postgresql+asyncpg://user:pass@host:5432/pegadocs
LOCAL_AUTH_JWT_SECRET=your-secret-key
```

### Vector Store (pgvector)

pgvector is included by default via the Docker Compose Postgres container. No additional configuration needed for local development.

### LLM / Embedding Provider

Configure your model provider and API keys through the console dashboard after setup, or set them directly in the database.

### Additional Services (optional)

| Service       | Variables                                      |
|---------------|------------------------------------------------|
| Celery + Redis| `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `CELERY_WORKER_CONCURRENCY` |
| AWS S3        | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, bucket names |
| Sentry        | `SENTRY_DSN`                                   |
| Email         | `RESEND_API_KEY`, `RESEND_FROM_EMAIL`           |

See `app/.env.example` for the full list of available variables.

## Project Structure

```text
pegadocs/
├── UI/                          # Next.js 16 frontend
│   ├── app/(auth)/              # Login, register, password reset
│   ├── app/(console)/           # Dashboard: collections, chat, settings
│   ├── components/              # Shared UI components
│   └── lib/api/                 # API client layer
├── app/                         # FastAPI backend
│   ├── application/
│   │   ├── protocols/           # Python Protocol interfaces
│   │   └── services/            # Business logic orchestration
│   ├── infra/
│   │   ├── adapters/            # Concrete implementations (LLM, DB, readers)
│   │   ├── factories/           # Runtime adapter selection
│   │   └── utils/               # Encryption, Supabase helpers, token counter
│   ├── presentation/            # FastAPI routers, controllers, Pydantic schemas
│   └── tasks/                   # Background embedding + scan jobs
└── docker-compose.yml
```

## Testing

```bash
cd app
uv run pytest tests/ -v --cov=. --cov-report=term-missing
```

Tests require a `.env` file at `app/.env`. The test suite enforces 100% coverage.

## License

[Apache License 2.0](LICENSE)
