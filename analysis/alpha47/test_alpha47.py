import os
import tempfile
import unittest
from pathlib import Path
from geoviewplus_alpha47_control_flow import analyze

ARCHIVE = Path(os.environ.get("GEOWORKS_ZIP", "GEOWORKS.zip"))

class Alpha47Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.result = analyze(ARCHIVE, Path(cls.tmp.name) / "out")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_01_zip_integrity(self): self.assertTrue(self.result["zip_crc_ok"])
    def test_02_segment1_program_fixups(self): self.assertEqual(self.result["segment1_program_segment_fixup_rows"], 351)
    def test_03_unique_segment1_code_seeds(self): self.assertEqual(self.result["segment1_unique_code_pointer_seeds"], 321)
    def test_04_segment1_code_pointer_instruction_boundaries(self): self.assertEqual(self.result["segment1_code_pointer_targets_at_instruction_starts_resource_sweep"], 344)
    def test_05_type24_far_pointer_count(self): self.assertEqual(self.result["program_far_pointer_fixup_rows_type_0x24"], 20)
    def test_06_type24_unique_targets(self): self.assertEqual(self.result["program_far_pointer_unique_code_targets"], 7)
    def test_07_type24_targets_instruction_boundaries(self): self.assertEqual(self.result["program_far_pointer_targets_at_instruction_starts_resource_local_sweep"], 20)
    def test_08_export_entries(self): self.assertEqual(self.result["export_entry_count"], 16)
    def test_09_seed_count(self): self.assertEqual(self.result["unique_recursive_seeds"], 343)
    def test_10_basic_blocks_processed(self): self.assertGreater(self.result["processed_basic_blocks"], 1000)
    def test_11_decoded_instruction_addresses(self): self.assertGreater(self.result["decoded_instruction_addresses"], 10000)
    def test_12_control_flow_edges(self): self.assertGreater(self.result["control_flow_edges"], 2000)
    def test_13_decode_conflicts_recorded(self): self.assertGreater(self.result["overlapping_decode_conflicts"], 0)
    def test_14_no_unresolved_entries(self): self.assertEqual(self.result["unresolved_seed_or_branch_entries"], 0)
    def test_15_candidate_total(self): self.assertEqual(self.result["candidate_count"], 66)
    def test_16_candidate_reached(self): self.assertEqual(self.result["candidate_reached_count"], 48)
    def test_17_candidate_not_reached(self): self.assertEqual(self.result["candidate_not_reached_count"], 18)
    def test_18_candidate_reach_by_segment(self):
        self.assertEqual(self.result["candidate_reached_by_segment"], {"2":5,"3":13,"4":16,"5":5,"8":9})
    def test_19_all_unreached_candidates_in_segments_2_and_3(self):
        self.assertTrue(all(x["segment"] in (2,3) for x in self.result["candidate_not_reached"]))
    def test_20_no_code_icon_semantics_claim(self):
        self.assertIn("not proven dead", self.result["method_limit"])

if __name__ == "__main__": unittest.main(verbosity=2)
