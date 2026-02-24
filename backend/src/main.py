"""FastAPI application factory."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from src.db.database import ensure_data_dir
from src.routes.templates import router as templates_router
from src.storage import active_disk
from src.storage.local import LocalDisk


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_data_dir()
    active_disk.ensure()
    yield


def create_app() -> FastAPI:
    app: FastAPI = FastAPI(title="Meme Generator API", lifespan=lifespan)

    allowed_hosts: list[str] = os.environ.get(
        key="ALLOWED_HOSTS", default="localhost:5173,localhost"
    ).split(sep=",")
    app.add_middleware(
        middleware_class=TrustedHostMiddleware, allowed_hosts=allowed_hosts
    )

    allowed_origins: list[str] = os.environ.get(
        key="ALLOWED_ORIGINS", default="http://localhost:5173"
    ).split(sep=",")
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router=templates_router, prefix="/api")

    if isinstance(active_disk, LocalDisk):
        app.mount(path="/static", app=StaticFiles(directory="data"), name="static")

    return app


app = create_app()
