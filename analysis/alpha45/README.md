# GeoViewPlus 0.5 – Alpha45

## Untersuchung 230: Instruktionskontext-Audit der 66 MOV-SI-Kandidaten

Alpha45 dekodiert die 66 Alpha44-Bytekandidaten in beiden vollständigen WRITE.GEO-Varianten mit GNU objdump (8086).

- 66 Kandidaten je Datei.
- Alle 66 werden im linearen Sweep als MOV SI mit passendem Immediate dekodiert.
- Die Instruktionskontexte stimmen an allen 66 Positionen in beiden Varianten überein.
- 15 automatisierte Tests bestanden.

**Methodische Grenze:** Die Disassemblierung läuft linear ab Dateioffset 0 über die vollständige GEO-Datei. Header, Tabellen, Code und Ressourcen sind nicht vorher getrennt. Damit sind die Befunde keine abschließende Bestätigung echter Codegrenzen oder Laufzeitreferenzen. Alpha46 rekonstruiert zuerst Code-Ressourcen und Einsprungpunkte.

Voraussetzungen: Python 3.10+, GNU objdump mit i8086-Unterstützung und GEOWORKS.zip.

```bash
python geoviewplus_alpha45_disassembly_audit.py GEOWORKS.zip --out output
GEOWORKS_ZIP=GEOWORKS.zip python -m unittest -v test_alpha45.py
```

Dateien: Analyseprogramm, Tests, Testprotokoll, Bericht, 66-Kontext-CSV und JSON-Zusammenfassung. Kein GUI-Umbau und kein EXE-Build.


## Repository-Ausgaben

- [Maschinenlesbare Zusammenfassung](GEO_alpha45_summary.json)
- [66 Kandidatenpositionen](GEO_alpha45_candidate_offsets.csv)
- [Testprotokoll](TEST_RESULTS_Alpha45.txt)
