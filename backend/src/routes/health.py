"""Health check endpoint."""

import os
from importlib.metadata import version

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck():
    app_version = os.environ.get("APP_VERSION") or version("lapp")
    return JSONResponse(content={"status": "ok", "version": app_version})
