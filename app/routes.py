from __future__ import annotations

import shutil
import time
import uuid
import zipfile
from pathlib import Path

from flask import Blueprint, current_app, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from .watermark import apply_watermark

bp = Blueprint("main", __name__)


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in current_app.config["ALLOWED_EXTENSIONS"]


def _job_root() -> Path:
    return Path(current_app.config["JOB_STORAGE_DIR"])


def _job_dir(job_id: str) -> Path:
    safe_job_id = secure_filename(job_id)
    if safe_job_id != job_id:
        raise ValueError("invalid job id")
    return _job_root() / safe_job_id


def cleanup_old_jobs() -> None:
    cutoff = time.time() - (current_app.config["JOB_RETENTION_HOURS"] * 3600)
    root = _job_root()
    root.mkdir(parents=True, exist_ok=True)
    for path in root.iterdir():
        if path.is_dir() and path.stat().st_mtime < cutoff:
            shutil.rmtree(path, ignore_errors=True)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.post("/upload")
def upload():
    cleanup_old_jobs()
    files = request.files.getlist("images")
    valid_files = [file for file in files if file and file.filename and allowed_file(file.filename)]
    if not valid_files:
        return render_template("index.html", error="Upload at least one PNG, JPG, JPEG, or WEBP image."), 400

    job_id = uuid.uuid4().hex
    job_path = _job_dir(job_id)
    upload_path = job_path / "uploads"
    output_path = job_path / "outputs"
    upload_path.mkdir(parents=True)
    output_path.mkdir(parents=True)

    images = []
    watermark_path = Path(current_app.static_folder) / "watermark.png"
    for index, file in enumerate(valid_files, start=1):
        filename = secure_filename(file.filename) or f"image-{index}.png"
        source = upload_path / filename
        file.save(source)
        output_name = f"watermarked-{index}-{Path(filename).stem}.png"
        output = output_path / output_name
        try:
            apply_watermark(
                source,
                watermark_path,
                output,
                scale_percent=current_app.config["WATERMARK_SCALE_PERCENT"],
                margin_px=current_app.config["WATERMARK_MARGIN_PX"],
            )
        except Exception:
            shutil.rmtree(job_path, ignore_errors=True)
            return render_template("index.html", error=f"Could not process {filename} as an image."), 400
        images.append(
            {
                "name": output_name,
                "preview_url": url_for("main.download_file", job_id=job_id, filename=output_name),
                "download_url": url_for("main.download_file", job_id=job_id, filename=output_name),
            }
        )

    return render_template(
        "index.html",
        job_id=job_id,
        images=images,
        zip_url=url_for("main.download_zip", job_id=job_id),
    )


@bp.get("/jobs/<job_id>/files/<filename>")
def download_file(job_id: str, filename: str):
    output_dir = _job_dir(job_id) / "outputs"
    path = output_dir / secure_filename(filename)
    if not path.exists() or not path.is_file():
        return "Not found", 404
    return send_file(path, as_attachment=request.args.get("download") == "1", download_name=path.name)


@bp.get("/jobs/<job_id>/download.zip")
def download_zip(job_id: str):
    job_path = _job_dir(job_id)
    output_dir = job_path / "outputs"
    if not output_dir.exists():
        return "Not found", 404
    zip_path = job_path / "watermarked-images.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(output_dir.iterdir()):
            if file.is_file():
                archive.write(file, arcname=file.name)
    return send_file(zip_path, as_attachment=True, download_name="watermarked-images.zip", mimetype="application/zip")
