#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression checks for GeoViewPlus 0.3.

Usage:
    py -3.15 GeoViewPlus_0.3_Regressionstest.py TOKEN.DB GeoViewPlus.py
"""
import hashlib
import importlib.util
import sys
from pathlib import Path
import unittest

EXPECTED_TOKEN_DB_SHA256 = "912e8acc120cdc8ae9a113766abff1ffa432440330af4042c60106d33a88b6a9"
EXPECTED_MONIKERS = 1493
SPECIAL_OFFSET = 0x1CD2


def load_module(path):
    spec = importlib.util.spec_from_file_location("geoviewplus_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GeoViewPlusRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if len(sys.argv) < 3:
            raise RuntimeError("Aufruf: py -3.15 GeoViewPlus_0.3_Regressionstest.py TOKEN.DB GeoViewPlus.py")
        cls.token_path = Path(sys.argv[1])
        cls.source_path = Path(sys.argv[2])
        cls.data = cls.token_path.read_bytes()
        cls.module = load_module(cls.source_path)
        cls.records = cls.module.scan_token_db_monikers(cls.data)

    def test_original_file_integrity(self):
        self.assertEqual(len(self.data), 1_016_048)
        self.assertEqual(hashlib.sha256(self.data).hexdigest(), EXPECTED_TOKEN_DB_SHA256)

    def test_token_db_is_geoworks_1x_vm_file(self):
        self.assertEqual(self.data[:4], bytes.fromhex("C7 45 CF 53"))
        self.assertEqual(self.data[0xC8:0xCA], bytes.fromhex("EB AD"))

    def test_moniker_count_and_distribution(self):
        self.assertEqual(len(self.records), EXPECTED_MONIKERS)
        distribution = {}
        for record in self.records:
            key = (record["width"], record["height"], record["type"], record["bitmap_type"])
            distribution[key] = distribution.get(key, 0) + 1
        self.assertEqual(distribution[(32, 32, 0x46, 0x11)], 636)
        self.assertEqual(distribution[(48, 30, 0x41, 0x00)], 346)
        self.assertEqual(distribution[(48, 30, 0x46, 0x11)], 351)
        self.assertEqual(distribution[(64, 40, 0x41, 0x00)], 80)
        self.assertEqual(distribution[(64, 40, 0x46, 0x11)], 80)

    def test_64x40_candidate_boundary(self):
        record = next((r for r in self.records if r["offset"] == SPECIAL_OFFSET), None)
        self.assertIsNotNone(record)
        self.assertEqual((record["width"], record["height"]), (64, 40))
        self.assertEqual(record["bitmap_length"], 0x03CB)
        self.assertEqual(record["decoded_length"], 1600)
        block_end = SPECIAL_OFFSET + 8 + record["bitmap_length"]
        self.assertEqual(block_end, 0x20A5)
        self.assertEqual(self.data[block_end:block_end + 6], bytes.fromhex("00 01 20 D8 03 00"))

    def test_packbits_rejects_unconsumed_or_truncated_input(self):
        decode = self.module._decode_packbits
        self.assertEqual(decode(bytes([0x00, 0x41]), 1), b"A")
        self.assertIsNone(decode(bytes([0x00, 0x41, 0x42]), 1))
        self.assertIsNone(decode(bytes([0x01, 0x41]), 2))
        self.assertEqual(decode(bytes([0x80, 0x00, 0x41]), 1), b"A")

    def test_geoworks_1x_palette_matches_dump_geo_tables(self):
        self.assertEqual(self.module.GEOWORKS_1X_PALETTE[0], (0, 0, 0))
        self.assertEqual(self.module.GEOWORKS_1X_PALETTE[1], (0, 0, 170))
        self.assertEqual(self.module.GEOWORKS_1X_PALETTE[6], (170, 85, 0))
        self.assertEqual(self.module.GEOWORKS_1X_PALETTE[8], (85, 85, 85))
        self.assertEqual(self.module.GEOWORKS_1X_PALETTE[15], (255, 255, 255))
        self.assertEqual(len(self.module.GEOWORKS_1X_PALETTE), 16)

    def test_color_bitmap_high_nibble_precedes_low_nibble(self):
        if not self.module.HAS_PIL:
            self.skipTest("Pillow is not installed")
        record = {"width": 2, "height": 1, "bitmap_type": 0x11,
                  "decoded_data": bytes((0xC0, 0x1E))}
        app = self.module.GeoViewPlusApp.__new__(self.module.GeoViewPlusApp)
        image = app._moniker_preview_image(record, 1)
        self.assertEqual(image.getpixel((0, 0)), (0, 0, 170, 255))
        self.assertEqual(image.getpixel((1, 0)), (255, 255, 85, 255))


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]], verbosity=2)
