"""Storage module — builds the active disk singleton from environment variables.

Environment variables
---------------------
STORAGE_DRIVER              ``local`` or ``s3``          default: local
STORAGE_LOCAL_PATH          root dir for local disk       default: data/templates
STORAGE_LOCAL_BASE_URL      URL prefix for local disk     default: /static/templates
STORAGE_S3_BUCKET            bucket name                   required when STORAGE_DRIVER=s3
STORAGE_S3_REGION            region                        default: us-east-1
STORAGE_S3_PREFIX            key prefix inside bucket      default: templates/
STORAGE_S3_ENDPOINT_URL      custom endpoint (MinIO, R2…)  optional (omit for AWS)
STORAGE_S3_ACCESS_KEY_ID     explicit credentials          optional
STORAGE_S3_SECRET_ACCESS_KEY explicit credentials          optional
"""

import os

from src.storage.disk import StorageDisk
from src.storage.local import LocalDisk
from src.storage.s3 import S3Disk

_disk_type = os.environ.get("STORAGE_DRIVER", "local").lower()

if _disk_type == "s3":
    _bucket = os.environ["STORAGE_S3_BUCKET"]
    active_disk: StorageDisk = S3Disk(
        bucket=_bucket,
        region=os.environ.get("STORAGE_S3_REGION", "us-east-1"),
        prefix=os.environ.get("STORAGE_S3_PREFIX", "templates/"),
        endpoint_url=os.environ.get("STORAGE_S3_ENDPOINT_URL"),
        access_key=os.environ.get("STORAGE_S3_ACCESS_KEY_ID"),
        secret_key=os.environ.get("STORAGE_S3_SECRET_ACCESS_KEY"),
    )
else:
    active_disk = LocalDisk(
        root=os.environ.get("STORAGE_LOCAL_PATH", "data/templates"),
        base_url=os.environ.get("STORAGE_LOCAL_BASE_URL", "/static/templates"),
    )


def get_disk() -> StorageDisk:
    """FastAPI Depends-compatible factory returning the active disk singleton."""
    return active_disk
