import unittest

from geoviewplus_gstring_bitmap import (
    GStringBitmapError, decode_draw_bitmap_cp, unpack_packbits,
)


class PackBitsTests(unittest.TestCase):
    def test_literal(self):
        self.assertEqual(unpack_packbits(bytes([2, 1, 2, 3]), 3), bytes([1, 2, 3]))

    def test_repeat(self):
        self.assertEqual(unpack_packbits(bytes([0xFD, 0xAA]), 4), bytes([0xAA] * 4))

    def test_noop(self):
        self.assertEqual(unpack_packbits(bytes([0x80, 0, 0x55]), 1), b"\x55")

    def test_truncated_literal(self):
        with self.assertRaises(GStringBitmapError):
            unpack_packbits(bytes([3, 1, 2]))


class DrawBitmapCPTests(unittest.TestCase):
    def test_rejects_trailing_unknown_gstring_element(self):
        bitmap = bytes([4, 0, 1, 0, 1, 0x11, 2, 0x12, 0x34, 0x00])
        gstring = bytes([0x51]) + len(bitmap).to_bytes(2, "little") + bitmap + b"\x01"
        with self.assertRaises(GStringBitmapError):
            decode_draw_bitmap_cp(gstring)

    def test_one_command_decode(self):
        # width=4, height=1, 4-bit format plus mask: 2+1 raw bytes.
        # PackBits encodes three literals with control=2.
        bitmap = bytes([4, 0, 1, 0, 1, 0x11, 2, 0x12, 0x34, 0x00])
        gstring = bytes([0x51]) + len(bitmap).to_bytes(2, "little") + bitmap + b"\x00"
        result = decode_draw_bitmap_cp(gstring)
        self.assertEqual((result.header.width, result.header.height), (4, 1))
        self.assertEqual(result.bitmap_data, bytes([0x12, 0x34, 0x00]))
        self.assertEqual(result.expected_uncompressed_size, 3)

    def test_wrong_opcode(self):
        with self.assertRaises(GStringBitmapError):
            decode_draw_bitmap_cp(b"\x4d\x00\x00\x00")


class RealTokenDatabaseIntegrationTests(unittest.TestCase):
    def test_real_desk_large_moniker_when_sample_is_configured(self):
        import os
        from pathlib import Path
        from geoviewplus_token_db_v2 import parse_pcgeos2_vm_directory
        from geoviewplus_token_db_v2_database import analyze_token_database

        sample = os.environ.get("GEOVIEWPLUS_TOKEN_DB_SAMPLE")
        if not sample:
            self.skipTest("GEOVIEWPLUS_TOKEN_DB_SAMPLE nicht gesetzt")
        data = Path(sample).read_bytes()
        analysis = analyze_token_database(data, parse_pcgeos2_vm_directory(data))
        moniker = next(
            item for item in analysis.resolved_monikers
            if item.token_chars == b"DESK" and item.list_entry.index == 0
        )
        decoded = decode_draw_bitmap_cp(moniker.db_item.payload[5:])
        self.assertEqual((decoded.header.width, decoded.header.height), (64, 40))
        self.assertEqual(decoded.header.compact, 1)
        self.assertEqual(decoded.header.bitmap_type, 0x11)
        self.assertEqual(len(decoded.bitmap_data), 1600)


if __name__ == "__main__":
    unittest.main()
