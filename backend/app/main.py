from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import admin, auth, catalog, chat, interview, progress, quiz, submissions, users
from app.core.config import settings
from app.core.database import engine
from app.models import Base


API_DESCRIPTION = """
Backend for the **Studying App** — a LeetCode-style platform for computer-science courses,
lessons, and code exercises.

### How to authenticate in Swagger

1. Use **POST `/api/v1/auth/login`** with your email/username + password.
2. Copy the `access_token` value from the response.
3. Click the green **Authorize** button at the top of this page.
4. Paste the token (just the token — no `Bearer ` prefix). Click **Authorize**, then **Close**.
5. All endpoints below now use your token automatically.

For admin-only endpoints (`/api/v1/admin/...`) you must log in as a user with `role = admin`.
"""


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


def _custom_openapi(app: FastAPI):
    def openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=settings.app_name,
            version="0.1.0",
            description=API_DESCRIPTION,
            routes=app.routes,
        )
        schema.setdefault("components", {})["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Paste the JWT access token returned by `/api/v1/auth/login`.",
            }
        }
        # Apply BearerAuth globally; public endpoints still work without it.
        for path in schema.get("paths", {}).values():
            for method in path.values():
                if isinstance(method, dict) and method.get("operationId"):
                    method.setdefault("security", [{"BearerAuth": []}])
        app.openapi_schema = schema
        return schema

    return openapi


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=API_DESCRIPTION,
        debug=settings.app_debug,
        lifespan=lifespan,
        swagger_ui_parameters={
            "persistAuthorization": True,  # keep the pasted token across page reloads
            "displayRequestDuration": True,
            "filter": True,
            "tryItOutEnabled": True,
        },
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Authorization"],
    )

    prefix = settings.api_v1_prefix
    app.include_router(auth.router, prefix=prefix)
    app.include_router(users.router, prefix=prefix)
    app.include_router(catalog.router, prefix=prefix)
    app.include_router(submissions.router, prefix=prefix)
    app.include_router(progress.router, prefix=prefix)
    app.include_router(quiz.router, prefix=prefix)
    app.include_router(chat.router, prefix=prefix)
    app.include_router(interview.router, prefix=prefix)
    app.include_router(admin.router, prefix=prefix)

    # Serve Angular frontend from static/ folder (production only)
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    if os.path.isdir(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    @app.get("/health", tags=["meta"])
    def health():
        from app.services.code_runner import code_runner

        return {
            "status": "ok",
            "app": settings.app_name,
            "env": settings.app_env,
            "docker_runner_available": code_runner.available,
            "languages": code_runner.supported_languages(),
        }

    @app.get("/", tags=["meta"], include_in_schema=False)
    def root():
        return {
            "name": settings.app_name,
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/health",
            "api": prefix,
        }

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Return a proper JSON 500 so CORS middleware can attach headers."""
        return JSONResponse(
            status_code=500,
            content={"detail": f"{type(exc).__name__}: {exc}"},
        )

    app.openapi = _custom_openapi(app)
    return app


app = create_app()
