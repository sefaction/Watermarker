import io
import zipfile

import pytest
from PIL import Image

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app({"TESTING": True, "JOB_STORAGE_DIR": str(tmp_path / "jobs")})
    return app.test_client()


def image_bytes(color=(0, 255, 0)):
    stream = io.BytesIO()
    Image.new("RGB", (80, 60), color).save(stream, format="PNG")
    stream.seek(0)
    return stream


def test_index_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Watermarker" in response.data


def test_upload_preview_single_download_and_zip_after_request(client):
    response = client.post(
        "/upload",
        data={"images": [(image_bytes(), "example.png")]},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"Download ZIP" in response.data

    html = response.data.decode()
    file_url = html.split('/jobs/')[1].split('"')[0]
    file_url = "/jobs/" + file_url
    image_response = client.get(file_url + "?download=1")
    assert image_response.status_code == 200
    assert image_response.mimetype == "image/png"

    job_id = file_url.split("/")[2]
    zip_response = client.get(f"/jobs/{job_id}/download.zip")
    assert zip_response.status_code == 200
    assert zip_response.mimetype == "application/zip"
    with zipfile.ZipFile(io.BytesIO(zip_response.data)) as archive:
        assert len(archive.namelist()) == 1
        assert archive.namelist()[0].endswith("example.png")


def test_rejects_invalid_upload(client):
    response = client.post(
        "/upload",
        data={"images": [(io.BytesIO(b"not image"), "bad.txt")]},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
