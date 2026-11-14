# GeoViewPlus 0.5 – R11-Analyse, Untersuchungen 221–228

**Stand:** 14.11.2026  
**Projektgrenze:** GeoWorks / PC/GEOS 1.x. PC/GEOS 2.x und FreeGEOS werden nicht als Belegquelle für konkrete GeoWorks-1.x-Feldsemantik verwendet.

## Zweck

Dieser Bericht führt die bisherige Alpha37–Alpha44-Arbeit zur R11-Ressource von `GEOWORKS/WORLD/WRITE.GEO` zusammen. Rohdaten des ursprünglichen Installationsarchivs werden nicht in dieses öffentliche Repository übernommen.

## Gesicherte Strukturbeobachtungen aus den bisherigen Alpha-Paketen

- In WRITE.GEO wurden neun zusammenhängende 68-Byte-Bereiche als Kandidaten erfasst.
- Die ersten 64 Bytes jedes Bereichs wurden als zwei 32-Byte-Ebenen untersucht; die letzten vier Bytes wurden zunächst als Trailer bezeichnet.
- Die neun Datenbereiche wurden in zwei WRITE.GEO-Varianten byteidentisch gefunden. Die vorherigen Crossfile-Läufe meldeten keine identischen 32-/64-/68-Byte-Treffer in den übrigen untersuchten GEO-Dateien.
- Der frühere Tabellenindex 11–19 ist nicht mit dem tatsächlichen ChunkHandle gleichzusetzen. Alpha42 ordnet die Kandidaten den Werten `0x0026` bis `0x0036` zu.
- Alpha42/43 untersuchten außerdem ChunkHandle `0x0024` und dessen interne Datensatz-/Offsetstruktur. Die genaue Semantik dieser Daten ist nicht nachgewiesen.

## Wichtige Einschränkungen und Korrekturregeln

Die Benennung als „Grafik“, „Icon“, „Cursor“ oder „Maske“ bleibt eine Arbeitshypothese, solange keine Code- oder Ressourcenreferenzkette die Funktion belegt. Ebenso sind Bitreihenfolge, Bitpolarität und Feldbedeutungen nicht allein aus 16×16-Darstellungen abzuleiten.

Die Alpha44-Auswertung hatte nach dem vorherigen Arbeitsbericht 66 Fundstellen des Byte-Musters `BE xx xx` gezählt (MOV SI,imm16 als Kandidat). Ein Opcode-Byte-Muster allein beweist jedoch noch keine gültige Instruktionsgrenze oder tatsächliche Verwendung als ChunkHandle. Daher sind diese Fundstellen ausdrücklich als **Kandidaten** zu behandeln, bis sie mit verlässlichen Disassemblierungsgrenzen, Segment-/Ressourcenbezug und aufgelösten Kontrollflusskontexten validiert wurden.

## Alpha-Stufen im Arbeitsverlauf

| Alpha | Untersuchung | Status laut Arbeitsprotokoll |
|---|---|---|
| 37 | 16×16-Zwei-Ebenen-Struktur der neun Kandidaten | Strukturhypothese; Semantik offen |
| 38 | Dateiübergreifender Identitäts- und Transformationstest | Crossfile-Befund dokumentiert |
| 39 | Werkzeug für Bytepositions-/Traileranalyse | Werkzeug erstellt |
| 40 | Konsistenz-Audit der vorhandenen Tabellen | Konsistenzlauf dokumentiert |
| 41 | Bytepositions- und Trailer-Analyse am Archiv | Feldsemantik weiterhin offen |
| 42 | Ressourcenkarte und Chunkgrenzen | ChunkHandles 0x0026–0x0036 zugeordnet |
| 43 | Interne Struktur von Chunk 0x0024 | 28 interne Datensätze als Strukturbeobachtung |
| 44 | Suche nach Code-Referenzkandidaten | 66 Musterfundstellen; Instruktions-/Referenzstatus noch zu validieren |

Die konkreten Alpha-ZIP-Dateien werden in diesem Schritt nicht automatisch in GitHub eingebettet, weil die Binärpakete im Arbeitsverzeichnis nicht als einzeln geprüfte Quelldateien vorliegen. Die README- und Markdown-Dokumentation dieses Commits halten den Stand und die Vorbehalte fest.

## Nächster Schritt – Alpha45

1. Die vollständigen `WRITE.GEO`-Dateien anhand echter Instruktionsgrenzen disassemblieren (nicht nur nach `BE xx xx` scannen).
2. Die Kandidatenfundstellen auf zulässige Codebereiche, Segmentgrenzen und Ressourcenkontexte begrenzen.
3. Kontrollfluss und Aufrufziele der umgebenden Routinen rekonstruieren.
4. Prüfen, ob und wie der Wert in SI in eine Handle-Tabelle / Chunk-Auflösung eingeht.
5. Für jede Referenz eine Evidenztabelle führen: Datei, Dateioffset, Instruktionsbytes, Disassemblierung, Ziel, Status (bestätigt / Kandidat / verworfen).
6. Erst nach bestätigter Referenzkette die Grafiksemantik einordnen.

## Reproduzierbarkeit

Für eine vollständige Wiederholung werden die Originaldateien aus dem GeoWorks-1.x-Archiv benötigt. Das Archiv `GEOWORKS.zip` selbst wird aus Gründen der Herkunfts- und Lizenzklarheit nicht in dieses öffentliche Repository übernommen. Analyseprogramme und abgeleitete, unkritische Tabellen sollen separat versioniert werden, sobald ihre Dateien einzeln geprüft und verfügbar sind.

---

## Alpha45 / Untersuchung 230 – Instruktionskontext-Audit

Am 14.11.2026 wurden die 66 Alpha44-Bytekandidaten in beiden vollständigen WRITE.GEO-Varianten mit GNU objdump 2.44 (i8086) linear dekodiert. An allen 66 Kandidatenpositionen dekodiert der lineare Sweep MOV SI mit dem erwarteten Immediate; die Dekodierungen stimmen zwischen beiden Varianten überein. 15 Tests bestanden.

**Methodische Einschränkung:** Der Sweep lief ab Dateioffset 0 über den vollständigen GEO-Dateiinhalt. Header, Tabellen, Code und Ressourcen wurden nicht zuvor getrennt. Deshalb sind die Stellen als Instruktionskontext-Kandidaten dokumentiert, nicht als endgültig bestätigte Code-Referenzen. Details: [Untersuchung 230](GeoViewPlus_Untersuchung_230_Alpha45_R11_Instruktionskontext.md).
