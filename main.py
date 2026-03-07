import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from domain.exceptions import (
    DomainException,
    EntityNotFoundException,
    UnauthorizedException,
    ValidationException,
)
from presentation.api.middleware.error_handler import (
    domain_exception_handler,
    entity_not_found_handler,
    generic_exception_handler,
    unauthorized_handler,
    validation_exception_handler,
)
from presentation.api.routers import categories_router, expenses_router

settings = get_settings()

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Contabilidad Familiar API",
        description="API para gestión de gastos familiares",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Manejadores de errores de dominio
    app.add_exception_handler(EntityNotFoundException, entity_not_found_handler)
    app.add_exception_handler(UnauthorizedException, unauthorized_handler)
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Routers
    app.include_router(expenses_router.router, prefix="/api/v1")
    app.include_router(categories_router.router, prefix="/api/v1")

    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
