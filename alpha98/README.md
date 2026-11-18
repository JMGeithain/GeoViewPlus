# GeoViewPlus – Alpha98 PC/GEOS-2.x VM Directory

This branch adds the read-only PC/GEOS 2.x VM-directory parser and a reproducible synthetic test suite. The user's original TOKEN_DB files are not committed; they remain local test data.

Files:
- `geoviewplus_token_db_v2.py` – validated VM header and directory reader.
- `tests/test_token_db_v2_vm_directory.py` – synthetic regression tests.
- `docs/GeoViewPlus_0.5_Alpha98_PCGEOS2_VM_Verzeichnis.md` – format notes and measured results.
- `alpha98/GeoViewPlus_Alpha98_GUI_Integration.patch` – patch for the Alpha97 graphical GUI.

The parser validates the 256-byte GEOS file header, VM header at 0x100, 0x00FB directory header, and 12-byte directory entries. It reports numeric User-IDs only. It does not claim to decode DB groups, token records, moniker lists, or icons yet.

The tested local file `token_da(2).000` yielded a directory at file offset 0x537B8, 281 directory entries, 113 allocated blocks, VM map handle 0x0044, and DB map handle 0x00D4. The original binary is deliberately not published.

The GUI integration patch adds a VM block table. Apply it to the Alpha97 `GeoViewPlus.py` baseline together with the new parser module. The full historical GeoWorks sample databases are not included in this public branch.
