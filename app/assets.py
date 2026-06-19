from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


def ensure_static_assets(static_folder: str | Path) -> None:
    """Create default static image assets when they are not already present.

    The repository keeps these generated assets out of Git so PR tooling that
    rejects binary files can still review the project. Deployments do not need
    any manual copy step because the app creates the defaults on startup.
    """
    static_path = Path(static_folder)
    static_path.mkdir(parents=True, exist_ok=True)

    _save_png_if_missing(static_path / "background.png", _background())
    logo = _badge((256, 256), "WM", font_anchor=(83, 111))
    _save_png_if_missing(static_path / "logo.png", logo)
    icon = _badge((128, 128), "W", font_anchor=(54, 56))
    _save_png_if_missing(static_path / "icon.png", icon)
    _save_png_if_missing(static_path / "watermark.png", _watermark())

    favicon_path = static_path / "favicon.ico"
    if not favicon_path.exists():
        icon.save(favicon_path, sizes=[(16, 16), (32, 32), (48, 48)])


def _save_png_if_missing(path: Path, image: Image.Image) -> None:
    if not path.exists():
        image.save(path, format="PNG")


def _background() -> Image.Image:
    image = Image.new("RGBA", (1200, 800), (232, 238, 245, 255))
    draw = ImageDraw.Draw(image)
    for offset in range(-800, 1200, 140):
        draw.line((offset, 800, offset + 800, 0), fill=(207, 218, 232, 120), width=5)
    return image


def _badge(size: tuple[int, int], text: str, *, font_anchor: tuple[int, int]) -> Image.Image:
    image = Image.new("RGBA", size, (23, 105, 224, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((4, 4, size[0] - 4, size[1] - 4), radius=size[0] // 5, outline=(255, 255, 255, 180), width=4)
    draw.text(font_anchor, text, fill=(255, 255, 255, 255))
    return image


def _watermark() -> Image.Image:
    image = Image.new("RGBA", (400, 140), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((5, 5, 395, 135), radius=20, fill=(255, 255, 255, 165), outline=(16, 32, 51, 160), width=3)
    draw.text((150, 62), "WATERMARK", fill=(16, 32, 51, 230))
    return image
