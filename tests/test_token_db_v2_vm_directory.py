import struct
import unittest
from geoviewplus_token_db_v2 import TokenDBFormatError, parse_pcgeos2_vm_directory, summarize_vm_directory


def fixture():
    b = bytearray(0x500)
    b[:4] = bytes.fromhex("C7 45 C1 53")
    struct.pack_into("<H", b, 0x28, 2)
    struct.pack_into("<HHI", b, 0x100, 0xADEB, 0x100, 0x200)
    d = 0x300
    struct.pack_into("<8H", b, d, 0x00FB, 0, 0, 0x40, 56, 0, 0, 1)
    struct.pack_into("<H", b, d + 20, 0x2C)
    struct.pack_into("<I", b, d + 24, 60)
    struct.pack_into("<HHHHI", b, d + 32, 0x1000, 0xFF, 0x8000, 56, 0x200)
    struct.pack_into("<HHHHI", b, d + 44, 0x2000, 0xFF, 0x1234, 4, 0x300)
    b[0x400:0x404] = b"MAP!"
    return bytes(b)


class VMDirectoryTests(unittest.TestCase):
    def test_directory_entries_and_handles(self):
        info = parse_pcgeos2_vm_directory(fixture())
        self.assertEqual(info.directory_file_offset, 0x300)
        self.assertEqual(len(info.entries), 2)
        self.assertEqual(info.map_block_handle, 0x2C)
        self.assertEqual(info.entries[1].vm_handle, 0x2C)
        self.assertEqual(info.entries[1].file_offset, 0x400)

    def test_numeric_user_id_summary(self):
        self.assertIn("0x1234: 1", summarize_vm_directory(parse_pcgeos2_vm_directory(fixture())))

    def test_bad_signature_rejected(self):
        b = bytearray(fixture()); b[0] = 0
        with self.assertRaises(TokenDBFormatError):
            parse_pcgeos2_vm_directory(bytes(b))

    def test_bad_vm_magic_rejected(self):
        b = bytearray(fixture()); struct.pack_into("<H", b, 0x100, 0)
        with self.assertRaises(TokenDBFormatError):
            parse_pcgeos2_vm_directory(bytes(b))

    def test_bad_directory_pointer_rejected(self):
        b = bytearray(fixture()); struct.pack_into("<I", b, 0x104, 0xFFFFFF00)
        with self.assertRaises(TokenDBFormatError):
            parse_pcgeos2_vm_directory(bytes(b))


if __name__ == "__main__":
    unittest.main()
