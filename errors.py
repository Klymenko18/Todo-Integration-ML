from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    """Resource not found."""


class ValidationAppError(Exception):
    """Domain validation error (not Pydantic validation error)."""


def register_error_handlers(app: FastAPI) -> None:
    """Attach custom error handlers to FastAPI app."""

    @app.exception_handler(NotFoundError)
    async def _nf_handler(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "code": "not_found",
                "message": str(exc) or "Not found",
            },
        )

    @app.exception_handler(ValidationAppError)
    async def _val_handler(_: Request, exc: ValidationAppError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "code": "validation_error",
                "message": str(exc) or "Invalid data",
            },
        )
