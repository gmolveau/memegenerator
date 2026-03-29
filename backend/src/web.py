"""FastAPI application factory."""

import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.sessions import SessionMiddleware

from src.config import get_settings
from src.routes.auth import router as auth_router
from src.routes.health import router as health_router
from src.routes.templates import router as templates_router
from src.storage import active_disk
from src.storage.local import LocalDisk


@asynccontextmanager
async def lifespan(app: FastAPI):
    active_disk.ensure()
    yield


def create_app() -> FastAPI:
    app: FastAPI = FastAPI(title="Meme Generator API", lifespan=lifespan)

    settings = get_settings()

    limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])
    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler,  # ty:ignore[invalid-argument-type]
    )
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SESSION_SECRET_KEY,
        max_age=settings.SESSION_COOKIE_MAX_AGE,
    )

    allowed_hosts: list[str] = os.environ["ALLOWED_HOSTS"].split(sep=",")
    app.add_middleware(
        middleware_class=TrustedHostMiddleware, allowed_hosts=allowed_hosts
    )

    allowed_origins: list[str] = os.environ["ALLOWED_ORIGINS"].split(sep=",")
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if isinstance(active_disk, LocalDisk):
        app.mount(
            path="/api/static", app=StaticFiles(directory="static"), name="static"
        )

    api_router = APIRouter(prefix="/api")
    api_router.include_router(router=auth_router)
    api_router.include_router(router=health_router)
    api_router.include_router(router=templates_router)
    app.include_router(api_router)

    return app


app = create_app()
