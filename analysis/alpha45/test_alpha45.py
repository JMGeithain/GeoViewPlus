import os, tempfile, unittest
from pathlib import Path
from geoviewplus_alpha45_disassembly_audit import analyze

ARCHIVE = Path(os.environ.get("GEOWORKS_ZIP", "GEOWORKS.zip"))

class Alpha45Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.result = analyze(ARCHIVE, Path(cls.tmp.name) / "out")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_01_archive_crc(self): self.assertTrue(self.result["zip_crc_ok"])
    def test_02_archive_entry_count(self): self.assertEqual(self.result["archive_members"], 2951)
    def test_03_write_file_size(self): self.assertEqual(self.result["write_geo_size"], 73110)
    def test_04_r11_resource_size(self): self.assertEqual(self.result["r11_size"], 0x066C)
    def test_05_r11_variants_identical(self): self.assertTrue(self.result["r11_identical_between_variants"])
    def test_06_first_variant_candidates(self): self.assertEqual(self.result["candidate_total_first_variant"], 66)
    def test_07_second_variant_candidates(self): self.assertEqual(self.result["candidate_total_second_variant"], 66)
    def test_08_candidate_offsets_equal(self): self.assertTrue(self.result["candidate_offsets_identical_between_variants"])
    def test_09_all_linear_instruction_starts(self): self.assertEqual(self.result["objdump_linear_sweep_instruction_starts"], 66)
    def test_10_all_mov_si_matches(self): self.assertEqual(self.result["objdump_linear_sweep_mov_si_matches"], 66)
    def test_11_all_candidates_outside_r11(self): self.assertTrue(self.result["all_candidates_outside_r11"])
    def test_12_per_handle_distribution(self):
        self.assertEqual(list(self.result["candidate_counts_first_variant"].values()), [3,8,6,4,5,12,10,15,3])
    def test_13_second_variant_linear_decode(self): self.assertEqual(self.result["second_variant_linear_sweep_mov_si_matches"], 66)
    def test_14_same_decode_both_variants(self): self.assertEqual(self.result["same_instruction_decode_both_variants"], 66)
    def test_15_all_candidate_offsets_outside_r11(self): self.assertTrue(self.result["all_candidates_outside_r11"])

if __name__ == "__main__": unittest.main(verbosity=2)
