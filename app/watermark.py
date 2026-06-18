from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps


def apply_watermark(
    source_path: str | Path,
    watermark_path: str | Path,
    output_path: str | Path,
    *,
    scale_percent: int = 35,
    margin_px: int = 10,
) -> None:
    """Apply a bottom-right watermark to an image, honoring EXIF orientation."""
    if scale_percent <= 0 or scale_percent > 100:
        raise ValueError("scale_percent must be between 1 and 100")
    if margin_px < 0:
        raise ValueError("margin_px must be zero or greater")

    with Image.open(source_path) as source, Image.open(watermark_path) as watermark:
        base = ImageOps.exif_transpose(source).convert("RGBA")
        mark = watermark.convert("RGBA")

        mark_width = max(1, int(base.width * (scale_percent / 100)))
        mark_height = max(1, int(mark.height * (mark_width / mark.width)))
        mark = mark.resize((mark_width, mark_height), Image.Resampling.LANCZOS)

        x = max(0, base.width - mark.width - margin_px)
        y = max(0, base.height - mark.height - margin_px)
        base.alpha_composite(mark, (x, y))

        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.suffix.lower() in {".jpg", ".jpeg"}:
            base.convert("RGB").save(destination, format="JPEG", quality=95)
        else:
            base.save(destination)
