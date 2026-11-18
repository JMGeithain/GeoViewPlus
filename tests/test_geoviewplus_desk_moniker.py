import os
from pathlib import Path
import unittest
from geoviewplus_desk_moniker import decode_desk_moniker_gstring
from geoviewplus_gstring_bitmap import GStringBitmapError

class DeskMonikerGStringTests(unittest.TestCase):
    def test_fill_bitmap_cp(self):
        bm=bytes([2,0,1,0,0,0,0x80])
        s=bytes([0x4D])+len(bm).to_bytes(2,"little")+bm+b"\x00"
        r=decode_desk_moniker_gstring(s)
        self.assertEqual(r.opcode_name,"GR_FILL_BITMAP_CP")
        self.assertEqual(r.bitmap.bitmap_data,b"\x80")
    def test_draw_bitmap_cp(self):
        bm=bytes([4,0,1,0,1,0x11,2,0x12,0x34,0])
        s=bytes([0x51])+len(bm).to_bytes(2,"little")+bm+b"\x00"
        r=decode_desk_moniker_gstring(s)
        self.assertEqual(r.opcode_name,"GR_DRAW_BITMAP_CP")
        self.assertEqual(r.bitmap.bitmap_data,bytes([0x12,0x34,0]))
    def test_rejects_other_opcode(self):
        with self.assertRaises(GStringBitmapError):
            decode_desk_moniker_gstring(b"\x4c\x00\x00\x00")
    def test_rejects_trailing_extra_element(self):
        bm=bytes([2,0,1,0,0,0,0x80])
        s=bytes([0x4D])+len(bm).to_bytes(2,"little")+bm+b"\x01"
        with self.assertRaises(GStringBitmapError):
            decode_desk_moniker_gstring(s)

class RealDeskTokenDatabaseTests(unittest.TestCase):
    def test_all_nine_desk_variants(self):
        sample=os.environ.get("GEOVIEWPLUS_TOKEN_DB_SAMPLE")
        if not sample: self.skipTest("GEOVIEWPLUS_TOKEN_DB_SAMPLE nicht gesetzt")
        from geoviewplus_token_db_v2 import parse_pcgeos2_vm_directory
        from geoviewplus_token_db_v2_database import analyze_token_database
        data=Path(sample).read_bytes()
        a=analyze_token_database(data,parse_pcgeos2_vm_directory(data))
        ms=sorted((m for m in a.resolved_monikers if m.token_chars==b"DESK"),
                  key=lambda m:m.list_entry.index)
        self.assertEqual(len(ms),9)
        expected=[
          (64,40,0x51,1,0x11,1600),(64,40,0x4D,1,0x00,320),
          (48,30,0x51,1,0x11,900),(48,30,0x4D,0,0x00,180),
          (32,20,0x51,1,0x11,400),(32,20,0x4D,0,0x00,80),
          (48,14,0x4D,0,0x00,84),(15,15,0x4D,0,0x00,30),
          (15,10,0x4D,0,0x00,20)]
        for m,e in zip(ms,expected):
            r=decode_desk_moniker_gstring(m.db_item.payload[5:])
            b=r.bitmap
            got=(b.header.width,b.header.height,r.opcode,b.header.compact,
                 b.header.bitmap_type,len(b.bitmap_data))
            self.assertEqual(got,e,f"DESK-Monikerindex {m.list_entry.index}")

if __name__=="__main__": unittest.main()
