import os
import struct
import unittest

from geoviewplus_token_db_v2_database import (
    TokenDBFormatError, parse_db_map_block, parse_moniker_list,
    parse_token_entries, parse_vis_moniker_header, analyze_token_database,
)
from geoviewplus_token_db_v2 import parse_pcgeos2_vm_directory


class TokenDBStructureTests(unittest.TestCase):
    def test_db_map_block_fields(self):
        raw = struct.pack('<6H', 0x00D4, 0x3030, 0x008C, 0x000E, 0x00F8, 0)
        result = parse_db_map_block(raw, expected_vm_handle=0x00D4)
        self.assertEqual((result.map_group, result.map_item), (0x008C, 0x000E))
        self.assertEqual(result.ungrouped_group, 0x00F8)

    def test_db_map_block_rejects_wrong_handle(self):
        raw = struct.pack('<6H', 0x00D4, 0, 0x008C, 0x000E, 0, 0)
        with self.assertRaises(TokenDBFormatError):
            parse_db_map_block(raw, expected_vm_handle=0x00D5)

    def test_token_entry_size_and_dummy(self):
        dummy = bytes(24)
        entry = struct.pack('<4sH2HH4H2H', b'DESK', 0, 0x0068, 0x000E,
                            0, 0, 0, 0, 0, 0, 0)
        parsed, skipped, warnings = parse_token_entries(dummy + entry)
        self.assertTrue(skipped)
        self.assertFalse(warnings)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].token_chars, b'DESK')
        self.assertEqual((parsed[0].moniker_group, parsed[0].moniker_item), (0x68, 0x0E))

    def test_token_entry_rejects_bad_length(self):
        with self.assertRaises(TokenDBFormatError):
            parse_token_entries(b'bad')

    def test_moniker_list_entries(self):
        raw = struct.pack('<3H', 0x23C6, 0x0140, 0x000E) + struct.pack('<3H', 0x23C1, 0x0188, 0x000E)
        entries = parse_moniker_list(raw)
        self.assertEqual(len(entries), 2)
        self.assertEqual((entries[0].type_word, entries[0].group_handle, entries[0].item_handle),
                         (0x23C6, 0x0140, 0x000E))
        self.assertTrue(entries[0].is_gstring)

    def test_moniker_list_rejects_bad_length(self):
        with self.assertRaises(TokenDBFormatError):
            parse_moniker_list(b'12345')

    def test_vis_moniker_header(self):
        header = parse_vis_moniker_header(bytes([0x46]) + struct.pack('<HH', 64, 40) + b'GSTRING')
        self.assertIsNotNone(header)
        self.assertEqual((header.width, header.height), (64, 40))
        self.assertTrue(header.is_gstring)
        self.assertEqual(header.payload_size, 7)

    def test_real_user_database_integration(self):
        path = os.environ.get('GEOVIEWPLUS_TOKEN_DB_SAMPLE')
        if not path:
            self.skipTest('GEOVIEWPLUS_TOKEN_DB_SAMPLE nicht gesetzt')
        with open(path, 'rb') as f:
            data = f.read()
        directory = parse_pcgeos2_vm_directory(data, path)
        result = analyze_token_database(data, directory)
        self.assertEqual(len(result.token_entries), 268)
        self.assertEqual(len(result.resolved_monikers), 1081)
        self.assertTrue(result.skipped_dummy_entry)
        desk = [m for m in result.resolved_monikers if m.token_chars == b'DESK']
        self.assertEqual(len(desk), 9)
        self.assertEqual((desk[0].header.width, desk[0].header.height), (64, 40))


if __name__ == '__main__':
    unittest.main()
