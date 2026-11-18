import os
from pathlib import Path
import unittest

from geoviewplus_bitmap_raster import decode_simple_bitmap_raster
from geoviewplus_gstring_bitmap import BitmapHeader, GStringBitmapError


class SimpleBitmapRasterTests(unittest.TestCase):
    def test_4bit_high_nibble_first_and_mask_before_pixels_per_row(self):
        h = BitmapHeader(4, 2, 0, 0x11)
        raw = bytes([0b10100000, 0x12, 0x34,
                     0b01010000, 0xAB, 0xCD])
        r = decode_simple_bitmap_raster(h, raw)
        self.assertEqual(r.pixel_rows, ((1, 2, 3, 4), (10, 11, 12, 13)))
        self.assertEqual(r.opacity_rows, ((True, False, True, False),
                                          (False, True, False, True)))
        self.assertEqual((r.image_bytes_per_row, r.mask_bytes_per_row), (2, 1))

    def test_mono_bit_order_and_mask(self):
        h = BitmapHeader(8, 1, 0, 0x10)
        r = decode_simple_bitmap_raster(h, bytes([0b10000001, 0b01011010]))
        self.assertEqual(r.opacity_rows, ((True, False, False, False,
                                           False, False, False, True),))
        self.assertEqual(r.pixel_rows, ((0, 1, 0, 1, 1, 0, 1, 0),))

    def test_unmasked_mono(self):
        h = BitmapHeader(5, 1, 0, 0x00)
        r = decode_simple_bitmap_raster(h, bytes([0b10101000]))
        self.assertEqual(r.pixel_rows, ((1, 0, 1, 0, 1),))
        self.assertIsNone(r.opacity_rows)

    def test_rejects_wrong_size_and_complex(self):
        with self.assertRaises(GStringBitmapError):
            decode_simple_bitmap_raster(BitmapHeader(4, 1, 0, 0x11), b"\x00")
        with self.assertRaises(GStringBitmapError):
            decode_simple_bitmap_raster(BitmapHeader(4, 1, 0, 0x09), b"\x00\x00")


class RealDeskRasterTests(unittest.TestCase):
    def test_all_nine_desk_variants_split_to_rows(self):
        sample = os.environ.get("GEOVIEWPLUS_TOKEN_DB_SAMPLE")
        if not sample:
            self.skipTest("GEOVIEWPLUS_TOKEN_DB_SAMPLE nicht gesetzt")
        from geoviewplus_token_db_v2 import parse_pcgeos2_vm_directory
        from geoviewplus_token_db_v2_database import analyze_token_database
        from geoviewplus_desk_moniker import decode_desk_moniker_gstring

        data = Path(sample).read_bytes()
        analysis = analyze_token_database(data, parse_pcgeos2_vm_directory(data))
        variants = sorted(
            (m for m in analysis.resolved_monikers if m.token_chars == b"DESK"),
            key=lambda m: m.list_entry.index,
        )
        self.assertEqual(len(variants), 9)
        for moniker in variants:
            decoded = decode_desk_moniker_gstring(moniker.db_item.payload[5:])
            raster = decode_simple_bitmap_raster(decoded.bitmap.header,
                                                 decoded.bitmap.bitmap_data)
            self.assertEqual(len(raster.pixel_rows), raster.height)
            self.assertTrue(all(len(row) == raster.width for row in raster.pixel_rows))
            if decoded.bitmap.header.has_mask:
                self.assertEqual(len(raster.opacity_rows), raster.height)
                self.assertTrue(all(len(row) == raster.width for row in raster.opacity_rows))


if __name__ == "__main__":
    unittest.main()
