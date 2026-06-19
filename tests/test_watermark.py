from PIL import Image

from app.watermark import apply_watermark


def test_apply_watermark_scales_and_positions(tmp_path):
    source = tmp_path / "source.png"
    mark = tmp_path / "mark.png"
    output = tmp_path / "output.png"
    Image.new("RGBA", (100, 100), (255, 255, 255, 255)).save(source)
    Image.new("RGBA", (10, 10), (255, 0, 0, 255)).save(mark)

    apply_watermark(source, mark, output, scale_percent=50, margin_px=10)

    with Image.open(output) as result:
        assert result.size == (100, 100)
        assert result.getpixel((40, 40))[:3] == (255, 0, 0)
        assert result.getpixel((39, 39))[:3] == (255, 255, 255)
