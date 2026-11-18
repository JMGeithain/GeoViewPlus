"""Render decoded PC/GEOS 2.x simple bitmap rasters to RGBA PNGs."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from PIL import Image

from geoviewplus_bitmap_raster import BMF_4BIT, BMF_MONO, BMF_8BIT, decode_simple_bitmap_raster
from geoviewplus_gstring_bitmap import BitmapHeader, GStringBitmapError
from geoviewplus_palette import VGA16_DEFAULT_PALETTE


def render_bitmap_rgba(header: BitmapHeader, data: bytes,
                       palette: Sequence[tuple[int, int, int]] = VGA16_DEFAULT_PALETTE) -> Image.Image:
    """Render a simple bitmap; 4-bit uses VGA16, mono uses black/white.

    A mask bit set to 1 keeps the pixel; a cleared bit becomes transparent.
    8-bit data is rejected until a matching 256-entry palette is supplied.
    """
    raster = decode_simple_bitmap_raster(header, data)
    image = Image.new("RGBA", (raster.width, raster.height), (0, 0, 0, 0))
    px = image.load()
    for y, row in enumerate(raster.pixel_rows):
        for x, index in enumerate(row):
            if raster.opacity_rows is not None and not raster.opacity_rows[y][x]:
                continue
            if raster.format_code == BMF_MONO:
                rgb = (0, 0, 0) if index else (255, 255, 255)
            elif raster.format_code == BMF_4BIT:
                if len(palette) < 16:
                    raise GStringBitmapError("The 4-bit palette needs at least 16 entries")
                rgb = palette[index]
            elif raster.format_code == BMF_8BIT:
                raise GStringBitmapError("8-bit PNG requires a matching 256-color palette")
            else:
                raise GStringBitmapError(f"Unsupported bitmap format {raster.format_code}")
            px[x, y] = (*rgb, 255)
    return image


def render_bitmap_png(header: BitmapHeader, data: bytes, destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    render_bitmap_rgba(header, data).save(path)
    return path
