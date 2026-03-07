import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from domain.exceptions import (
    DomainException,
    EntityNotFoundException,
    UnauthorizedException,
    ValidationException,
)

logger = logging.getLogger(__name__)


async def entity_not_found_handler(request: Request, exc: EntityNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "message": str(exc)},
    )


async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=403,
        content={"error": "forbidden", "message": str(exc)},
    )


async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=422,
        content={"error": "validation_error", "message": str(exc)},
    )


async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=422,
        content={"error": "domain_error", "message": str(exc)},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "An unexpected error occurred"},
    )
