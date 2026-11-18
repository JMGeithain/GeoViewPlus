import unittest
from geoviewplus_gstring_bitmap import BitmapHeader, GStringBitmapError
from geoviewplus_palette import VGA16_DEFAULT_PALETTE, palette_rgb
from geoviewplus_bitmap_png import render_bitmap_rgba


class VGA16PaletteTests(unittest.TestCase):
    def test_exact_first_and_last_vga16_entries(self):
        self.assertEqual(palette_rgb(0), (0, 0, 0))
        self.assertEqual(palette_rgb(1), (0, 0, 170))
        self.assertEqual(palette_rgb(6), (170, 85, 0))
        self.assertEqual(palette_rgb(15), (255, 255, 255))
        self.assertEqual(len(VGA16_DEFAULT_PALETTE), 16)

    def test_rejects_invalid_palette_index(self):
        with self.assertRaises(ValueError):
            palette_rgb(16)


class BitmapPngTests(unittest.TestCase):
    def test_4bit_palette_and_mask_to_rgba(self):
        header = BitmapHeader(2, 1, 0, 0x11)
        image = render_bitmap_rgba(header, bytes([0x80, 0x14]))
        self.assertEqual(image.getpixel((0, 0)), (0, 0, 170, 255))
        self.assertEqual(image.getpixel((1, 0)), (0, 0, 0, 0))

    def test_mono_bit_one_is_black(self):
        header = BitmapHeader(2, 1, 0, 0x00)
        image = render_bitmap_rgba(header, bytes([0x80]))
        self.assertEqual(image.getpixel((0, 0)), (0, 0, 0, 255))
        self.assertEqual(image.getpixel((1, 0)), (255, 255, 255, 255))

    def test_8bit_requires_palette_implementation(self):
        with self.assertRaises(GStringBitmapError):
            render_bitmap_rgba(BitmapHeader(1, 1, 0, 0x02), b"\x01")


if __name__ == "__main__":
    unittest.main()
