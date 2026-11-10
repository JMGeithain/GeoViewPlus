#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kleine, eigenstaendige Regressionstests fuer GeoViewPlus 0.4."""
import importlib.util
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent
MODULE_PATH = BASE / "GeoViewPlus.py"
spec = importlib.util.spec_from_file_location("geoviewplus_040", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ZeichensatzTests(unittest.TestCase):
    def test_deutsche_sonderzeichen(self):
        raw = b"\x86ber Anf\x8anger M\x9aller T\x9frme Mei\xa7en"
        self.assertEqual(
            module.decode_geos_name(raw, 0, len(raw)),
            "Über Anfänger Möller Türme Meißen"
        )

    def test_36_byte_ascii_name(self):
        raw = b"123456789012345678901234567890123456"
        self.assertEqual(module.decode_geos_name(raw, 0, 36), raw.decode("ascii"))

    def test_geoworks_name_table_is_present(self):
        self.assertEqual(module.GEOWORKS_1X_NAME_CHARS[0x86], "Ü")
        self.assertEqual(module.GEOWORKS_1X_NAME_CHARS[0x9A], "ö")
        self.assertEqual(module.GEOWORKS_1X_NAME_CHARS[0xA7], "ß")

    def test_author_and_ai_credits_are_present(self):
        source = (BASE / "GeoViewPlus.py").read_text(encoding="utf-8")
        self.assertIn("Johannes Möller", source)
        self.assertIn("ChatGPT (OpenAI)", source)
        self.assertIn("Grok (xAI)", source)

    def test_about_dialog_mentions_meeting_and_logo(self):
        source = (BASE / "GeoViewPlus.py").read_text(encoding="utf-8")
        self.assertIn("25. Geithainer PC/GEOS-Treffen", source)
        self.assertIn("2026 in Syhra", source)
        self.assertIn("JME-Spirallogo.png", source)

    def test_jme_logo_is_in_package_and_batch(self):
        self.assertTrue((BASE / "JME-Spirallogo.png").is_file())
        batch = (BASE / "make_exe.bat").read_text(encoding="utf-8")
        self.assertIn("JME-Spirallogo.png", batch)

    def test_about_dialog_has_wrapping_and_smaller_logo(self):
        source = (BASE / "GeoViewPlus.py").read_text(encoding="utf-8")
        self.assertIn("wraplength=510", source)
        self.assertIn("logo.thumbnail((104, 104)", source)
        self.assertIn("Möllerjaner © 2026 Johannes Möller", source)
        self.assertIn("'GEOS / GeoWorks File Information Viewer\\n\\n'", source)

    def test_icon_resource_is_in_package(self):
        self.assertTrue((BASE / "geoworks_motif_icon.ico").is_file())


    def test_open_dialog_includes_db_files(self):
        source = (BASE / "GeoViewPlus.py").read_text(encoding="utf-8")
        self.assertIn("*.db", source)
        self.assertIn("GEOS-Dateien inkl. TOKEN.DB", source)

    def test_valid_geoworks_1x_type_zero_is_not_non_geos(self):
        # Synthetic header: signature is GeoWorks 1.x; first type word is 0.
        data = bytearray(512)
        data[0:4] = bytes.fromhex("C7 45 CF 53")
        data[0x20:0x24] = b"Uhr\\x00"
        data[0xA8:0xC0] = b"(c) T. Wachsmann 1992\\x00"
        result = module.parse_geos_header(bytes(data))
        self.assertTrue(result["valid"])
        self.assertEqual(result["version"], 1)
        self.assertEqual(result["file_type_id"], 0)
        self.assertIn("Drittanbieter", result["file_type"])
        self.assertNotIn("Non-GEOS", result["file_type"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
