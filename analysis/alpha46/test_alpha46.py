import os
import tempfile
import unittest
from pathlib import Path
from geoviewplus_alpha46_geode_resource_map import analyze

ARCHIVE = Path(os.environ.get("GEOWORKS_ZIP", "GEOWORKS.zip"))

class Alpha46Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.result = analyze(ARCHIVE, Path(cls.tmp.name) / "out")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_01_zip_crc(self): self.assertTrue(self.result["zip_crc_ok"])
    def test_02_archive_member_count(self): self.assertEqual(self.result["archive_members"], 2951)
    def test_03_write_geo_size(self): self.assertEqual(self.result["write_geo_size"], 73110)
    def test_04_geos_magic(self): self.assertEqual(self.result["geos_file_magic"], "0x53CF45C7")
    def test_05_v1_geode_header_offset(self): self.assertEqual(self.result["geode_header_offset_version1"], "0x00C0")
    def test_06_application_type(self): self.assertEqual(self.result["application_type"], 1)
    def test_07_permanent_name(self): self.assertEqual(self.result["permanent_name"], "write")
    def test_08_permanent_extension(self): self.assertEqual(self.result["permanent_extension"], "app")
    def test_09_segment_count(self): self.assertEqual(self.result["num_segments"], 36)
    def test_10_library_count(self): self.assertEqual(self.result["num_libraries"], 3)
    def test_11_export_count(self): self.assertEqual(self.result["num_exports"], 16)
    def test_12_segment_table_start(self): self.assertEqual(self.result["segment_table"]["start"], "0x018A")
    def test_13_segment_table_end(self): self.assertEqual(self.result["segment_table"]["end"], "0x02F2")
    def test_14_segment_tables_identical(self): self.assertTrue(self.result["segment_table_identical_between_variants"])
    def test_15_code_segments(self): self.assertEqual(self.result["code_segments"], [2,3,4,5,6,7,8])
    def test_16_candidate_total(self): self.assertEqual(self.result["candidate_count_first_variant"], 66)
    def test_17_candidate_offsets_same(self): self.assertTrue(self.result["candidate_offsets_identical_between_variants"])
    def test_18_all_candidate_instruction_starts(self): self.assertEqual(self.result["candidate_instruction_start_count_resource_local_sweep"], 66)
    def test_19_all_candidate_mov_si(self): self.assertEqual(self.result["candidate_mov_si_expected_count_resource_local_sweep"], 66)
    def test_20_candidate_segment_distribution(self):
        self.assertEqual(self.result["candidate_counts_by_segment"], {"2":7,"3":29,"4":16,"5":5,"8":9})
    def test_21_control_flow_categories(self):
        self.assertEqual(self.result["candidate_flow_categories_first_control_flow_within_next_4"],
                         {"far_call":28,"none_in_next_4":7,"near_call":22,"near_jmp":3,"far_jmp":6})
    def test_22_near_targets_instruction_starts(self): self.assertEqual(self.result["near_control_flow_targets_resolved_to_instruction_starts"], 25)
    def test_23_segment1_program_fixups(self): self.assertEqual(self.result["program_segment_fixup_count_in_segment_1"], 351)
    def test_24_all_program_refs_in_bounds(self): self.assertEqual(self.result["program_segment_references_in_target_bounds"], 351)
    def test_25_code_segment_reference_count(self): self.assertEqual(self.result["program_segment_references_to_code_segments"], 348)
    def test_26_target_instruction_start_count(self): self.assertEqual(self.result["program_segment_targets_at_instruction_starts_resource_local_sweep"], 344)
    def test_27_target_segment_distribution(self):
        self.assertEqual(self.result["program_segment_references_by_target_segment"],
                         {"2":55,"5":41,"6":6,"3":111,"4":90,"7":14,"1":3,"8":31})
    def test_28_r11_segment_index(self): self.assertEqual(self.result["r11_segment_index"], 11)
    def test_29_r11_file_offset(self): self.assertEqual(self.result["r11_file_offset"], "0x09B22")
    def test_30_r11_segment_length(self): self.assertEqual(self.result["r11_segment_length"], "0x0670")
    def test_31_r11_lmem_flag(self): self.assertTrue(int(self.result["r11_segment_flags"],16) & 0x0008)
    def test_32_r11_lmem_segment_number(self): self.assertEqual(self.result["r11_lmem_header"]["segment_number"], 11)
    def test_33_r11_handle_table_offset(self): self.assertEqual(self.result["r11_lmem_header"]["handle_list_offset"], 0x10)
    def test_34_r11_handle_count(self): self.assertEqual(self.result["r11_lmem_header"]["handle_count"], 20)
    def test_35_r11_block_size_field(self): self.assertEqual(self.result["r11_lmem_header"]["block_size_field"], 0x66C)
    def test_36_r11_nine_candidate_offsets(self):
        self.assertEqual(self.result["r11_handle_table_values"][11:], [f"0x{x:04X}" for x in range(0x03E2,0x0603,0x44)])
    def test_37_kernel_exe_present(self): self.assertTrue(self.result["kernel_exe_present"])
    def test_38_kernel_exe_is_mz(self): self.assertEqual(self.result["kernel_exe_magic"], "MZ")

if __name__ == "__main__":
    unittest.main(verbosity=2)
