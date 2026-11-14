# GeoViewPlus 0.5 – Alpha46

## Untersuchung 231: GeoWorks-1.x-Geode-Ressourcen und R11-Referenzen

Alpha46 rekonstruiert den Version-1-Geode-Kopf und die Ressourcentabelle von GeoWrite. Die 66 Alpha45-MOV-SI-Kandidaten werden den Code-Ressourcen 2–8 zugeordnet und in ihrem jeweiligen Segmentkontext dekodiert.

Ergebnis:
- 36 Ressourcensegmente, davon 7 mit HAF_CODE.
- Alle 66 Kandidaten liegen in Code-Ressourcen und dekodieren ressourcenlokal als erwartetes MOV SI.
- 351 Programmsegment-Fixups (Typ 0x0022) in Segment 1; 348 Ziele in Code-Ressourcen, 344 davon an Instruktionsanfängen des linearen Ressourcensweeps.
- R11 als LMem-Segment 11 mit 20 Handles gegengeprüft.
- 38 Tests bestanden.

**Grenze:** Der lineare Sweep innerhalb einer Code-Ressource ist noch kein rekursiver Kontrollflussnachweis. Die 344 Instruktionsanfänge sind Einsprungpunkt-Kandidaten. Die Bedeutung der neun R11-Grafik-Chunks ist weiterhin offen.

Bericht: [Untersuchung 231 – Alpha46](../../docs/GeoViewPlus_Untersuchung_231_Alpha46_Geode_ResourceMap.md).

Ausführung mit Python 3.10+, GNU objdump (i8086) und dem Originalarchiv GEOWORKS.zip:

```bash
python geoviewplus_alpha46_geode_resource_map.py GEOWORKS.zip --out output
GEOWORKS_ZIP=GEOWORKS.zip python -m unittest -v test_alpha46.py
```

