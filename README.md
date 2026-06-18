# Watermarker

A clean Flask image watermarking app ready for GitHub-based Portainer deployments.

## Features

- Upload one or more PNG, JPG/JPEG, or WEBP images.
- Correct image orientation with Pillow EXIF transpose support.
- Apply `app/static/watermark.png` at the bottom-right of each image. Default image assets are generated on startup when absent so the Git diff remains text-only.
- Default watermark width is 35% of the base image width with a 10px margin.
- Preview processed images in the browser.
- Download individual processed images.
- Download all processed images as a ZIP from job-based temporary storage.
- Persist generated jobs in `/app/instance`, which is backed by a named Docker volume in Compose.

## Configuration

| Variable | Default | Description |
| --- | ---: | --- |
| `MAX_UPLOAD_MB` | `16` | Maximum request upload size in megabytes. |
| `WATERMARK_SCALE_PERCENT` | `35` | Watermark width as a percentage of the base image width. |
| `WATERMARK_MARGIN_PX` | `10` | Bottom/right margin in pixels. |
| `JOB_RETENTION_HOURS` | `24` | Age after which old job folders are removed on upload. |

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
flask --app wsgi run --debug
```

Visit <http://127.0.0.1:5000>.

## Docker

```bash
docker compose up --build
```

Visit <http://localhost:8000>. Generated files are stored in the `watermarker-instance` named volume mounted at `/app/instance`.

## Portainer Git deployment

1. Push this repository to GitHub.
2. In Portainer, create a stack from a Git repository.
3. Point Portainer at the repository URL and use `docker-compose.yml` as the compose path.
4. Deploy the stack. The app exposes container port `8000` and maps it to host port `8000` by default.
5. Adjust the environment variables in `docker-compose.yml` or Portainer if needed.

No manual file copying is required; text sources and startup-generated default static assets are included in the app, and generated job files persist in the Docker volume.

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

GitHub Actions runs the same pytest suite on pushes and pull requests.
