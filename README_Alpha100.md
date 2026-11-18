# GeoViewPlus 0.5 Alpha100 – GString Bitmap Extraction

Alpha100 adds a conservative read-only decoder for `GR_DRAW_BITMAP_CP` (0x51) and PackBits-compressed simple bitmaps. The first large `DESK` moniker in the private PC/GEOS 2.x Token DB is structurally validated: 64×40, BMCompact=1, BMF_4BIT with mask, 166-byte bitmap block, 1,600 decompressed bytes, and a valid `GR_END_GSTRING` terminator.

The decoder preserves raw decompressed bytes. It does **not** yet render colors, interpret mask semantics, decode other GString opcodes, or modify any input file. See `docs/GeoViewPlus_0.5_Alpha100_GString_Bitmap_Extraktion.md`.

Run tests:

```bat
set GEOVIEWPLUS_TOKEN_DB_SAMPLE=C:\\path\\to\\your\\private\\token_db_file
python -m unittest -v test_geoviewplus_gstring_bitmap.py test_token_db_v2_vm_directory.py test_token_db_v2_database.py test_token_db_detection.py
```

The private Token DB is deliberately not included in this package or the public repository.
