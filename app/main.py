import logfire
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.llamaindex import LlamaIndexInstrumentor

load_dotenv(override=True)

import sentry_sdk
from app.infra.auth import get_user
from app.infra.config import settings
from app.logging_config import setup_logging

sentry_sdk.init(dsn=settings.SENTRY_DSN, send_default_pii=True)


def setup_routers(app: FastAPI) -> None:
    from app.presentation.health import health_router
    from app.presentation.routers.auth_routers import auth_router
    from app.presentation.routers.chat_routers import chat_router
    from app.presentation.routers.collection_routers import collection_router
    from app.presentation.routers.data_source_routers import data_source_router
    from app.presentation.routers.database_routers import database_router
    from app.presentation.routers.embedding_routers import embedding_router
    from app.presentation.routers.model_routers import model_router
    from app.presentation.routers.prompt_routers import prompt_router
    from app.presentation.routers.scanning_routers import scanning_router

    if settings.ENABLE_MOCK_API:
        from app.presentation.routers.mock_routers import mock_router
        app.include_router(mock_router, prefix="/mock")

    app.include_router(health_router)
    app.include_router(auth_router, prefix="/auth")
    app.include_router(chat_router, dependencies=[Depends(get_user)])
    app.include_router(embedding_router, dependencies=[Depends(get_user)])
    app.include_router(collection_router, dependencies=[Depends(get_user)])
    app.include_router(database_router, dependencies=[Depends(get_user)])
    app.include_router(scanning_router, dependencies=[Depends(get_user)])
    app.include_router(model_router, dependencies=[Depends(get_user)])
    app.include_router(data_source_router, dependencies=[Depends(get_user)])
    app.include_router(prompt_router, dependencies=[Depends(get_user)])


def create_application() -> FastAPI:
    setup_logging()

    if settings.AUTH_PROVIDER.lower() == "local":
        from app.infra.adapters.auth.models import create_all_tables
        create_all_tables()

    application = FastAPI()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    setup_routers(application)
    logfire.configure(environment=settings.ENV)
    logfire.instrument_fastapi(application)
    LlamaIndexInstrumentor().instrument()
    return application