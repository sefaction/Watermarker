from __future__ import annotations

import os
from pathlib import Path

from flask import Flask


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    max_upload_mb = _env_int("MAX_UPLOAD_MB", 16)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
        MAX_UPLOAD_MB=max_upload_mb,
        MAX_CONTENT_LENGTH=max_upload_mb * 1024 * 1024,
        WATERMARK_SCALE_PERCENT=_env_int("WATERMARK_SCALE_PERCENT", 35),
        WATERMARK_MARGIN_PX=_env_int("WATERMARK_MARGIN_PX", 10),
        JOB_RETENTION_HOURS=_env_int("JOB_RETENTION_HOURS", 24),
        JOB_STORAGE_DIR=str(Path(app.instance_path) / "jobs"),
        ALLOWED_EXTENSIONS={"png", "jpg", "jpeg", "webp"},
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["JOB_STORAGE_DIR"]).mkdir(parents=True, exist_ok=True)

    from .assets import ensure_static_assets

    ensure_static_assets(app.static_folder)

    from .routes import bp

    app.register_blueprint(bp)
    return app
