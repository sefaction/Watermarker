# Watermarker

A clean Flask image watermarking app ready for GitHub Container Registry (GHCR) and Portainer deployments.

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

### Pull the GitHub-hosted image

The default `docker-compose.yml` is intended for Portainer and pulls an image from GitHub Container Registry (GHCR). Set `WATERMARKER_IMAGE` to your published image name:

```bash
WATERMARKER_IMAGE=ghcr.io/<github-owner>/<repo-name>:latest docker compose up
```

Visit <http://localhost:8000>. Generated files are stored in the `watermarker-instance` named volume mounted at `/app/instance`.

### Build locally from the Git checkout

Use the build override file when developing locally or before your first GHCR image exists:

```bash
docker compose -f docker-compose.build.yml up --build
```

## Publishing the GitHub image

The `Publish Docker image` GitHub Actions workflow builds the Dockerfile and pushes images to GHCR on pushes to `main` and manual workflow runs. It publishes:

- `ghcr.io/<github-owner>/<repo-name>:latest` for the default branch.
- `ghcr.io/<github-owner>/<repo-name>:sha-<commit>` for immutable commit images.

If your GHCR package is private, configure Portainer with GitHub Container Registry credentials before deploying.

## Portainer Git deployment

1. Push this repository to GitHub.
2. Let the `Publish Docker image` workflow complete successfully so `ghcr.io/<github-owner>/<repo-name>:latest` exists.
3. In Portainer, create a stack from a Git repository.
4. Point Portainer at the repository URL and use `docker-compose.yml` as the compose path.
5. Set the stack environment variable `WATERMARKER_IMAGE=ghcr.io/<github-owner>/<repo-name>:latest`.
6. Deploy the stack. The app exposes container port `8000` and maps it to host port `8000` by default.
7. Adjust the runtime environment variables in `docker-compose.yml` or Portainer if needed.

No manual file copying or image building on the Portainer host is required; Portainer pulls the GitHub-hosted image and generated job files persist in the Docker volume.

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

GitHub Actions runs the pytest suite on pushes and pull requests, and a separate workflow publishes the Docker image to GHCR on `main`.
