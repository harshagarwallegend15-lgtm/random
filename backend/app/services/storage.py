"""Cloudinary upload helper.

If credentials are not set, falls back to a local `/uploads` static path so the
app remains functional for local development without a Cloudinary account.
"""
from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

from app.config import settings

log = logging.getLogger(__name__)

_LOCAL_UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
_LOCAL_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

_cloudinary_configured = bool(
    settings.cloudinary_cloud_name and settings.cloudinary_api_key and settings.cloudinary_api_secret
)


def _init_cloudinary():
    if not _cloudinary_configured:
        return False
    try:
        import cloudinary
        import cloudinary.uploader
        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            secure=True,
        )
        return True
    except Exception as e:
        log.warning("Cloudinary init failed, using local fallback: %s", e)
        return False


def upload_image(data: bytes, user_id: int, angle: str) -> tuple[str, str]:
    """Upload image bytes. Returns (public_url, public_id)."""
    public_id_base = f"workout_app/user_{user_id}/{angle}_{uuid.uuid4().hex[:8]}"

    if _init_cloudinary():
        try:
            import cloudinary.uploader
            res = cloudinary.uploader.upload(
                data,
                folder=f"workout_app/user_{user_id}",
                public_id=public_id_base.split("/")[-1],
                overwrite=True,
                resource_type="image",
            )
            return res["secure_url"], res["public_id"]
        except Exception as e:
            log.warning("Cloudinary upload failed, falling back to local: %s", e)

    # Local fallback
    local_name = f"{angle}_{uuid.uuid4().hex[:8]}.jpg"
    out_path = _LOCAL_UPLOAD_DIR / f"user_{user_id}" / local_name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(data)
    return f"/uploads/user_{user_id}/{local_name}", public_id_base
