# Untersuchung 166 – Kontrolle der Headerhypothese an weiteren GeoWorks-1.x-Dateien

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** Fünf weitere GEO-Dateien aus `Basebox-SVGA-Ensemble12(2).zip`  
**Geltungsbereich:** Ausschließlich Dateien mit GEOS-1.x-Signatur; direkte Bytebefunde.  
**Ziel:** Prüfen, ob die in BOUNCE.GEO und BCOLTEST.GEO untersuchte Ressourcenheader-Struktur auch in anderen GeoWorks-1.x-GEO-Dateien wiederkehrt.

## 1. Auswahl und Versionskontrolle

Im Archiv befinden sich sieben GEO-Dateien. Die ersten vier Bytes aller sieben Dateien lauten `C7 45 CF 53`, die vom mitgelieferten Inventarisierungsskript als GEOS 1.x erkannt werden.

Neben BOUNCE.GEO und BCOLTEST.GEO wurden fünf weitere Dateien geprüft:

| Datei | Dateigröße | SHA-256 |
|---|---:|---|
| BB120_64.GEO | 35.010 | `e78e91aacc8e9bd24e931ef78f72c0bf42e886003a1b75e2c36ba7c3e1593d05` |
| BB72_64.GEO | 35.010 | `694efa06840e605e214c39b20f4ee2a5ebafa4e290d45edc3cbe323aedb9317a` |
| BB96_64.GEO | 35.010 | `8bfb2d12e512b50d00909fc6f58522b053e0ca556eb7275e0d87f4aa085b4ab1` |
| S16_1280.GEO | 28.754 | `5c56db2b0c39ac66e7448a672a68c8722876b547c7822a006cd31da26f98654d` |
| V16_0720.GEO | 34.962 | `7b26608d30869235766384c8a2034a8ad653c738ad27e29cee4b80a78c53d20c` |

Alle fünf Dateien wurden vom Inventarisierungsskript als `GEOS 1.x geode` mit jeweils drei Ressourcen erkannt. Die Inventarisierung meldete keine Fehler. Die Dateien sind Treiberdateien und damit keine identischen Programmtypen wie die beiden kleinen Testprogramme; gerade deshalb eignen sie sich als Gegenprobe auf eine zu weit verallgemeinerte Headerhypothese.

## 2. Ressource 2: wiederkehrender, aber anderer Headerbefund

Die Ressource 2 ist in allen fünf Treiberdateien genau 1.776 Bytes (`06F0h`) groß. Ihre ersten 16 WORDs lauten:

| Offset | BB120_64 | BB72_64 | BB96_64 | S16_1280 | V16_0720 |
|---|---:|---:|---:|---:|---:|
| +00h | 0002 | 0002 | 0002 | 0002 | 0002 |
| +02h | 0020 | 0020 | 0020 | 0020 | 0020 |
| +04h | 0000 | 0000 | 0000 | 0000 | 0000 |
| +06h | 0000 | 0000 | 0000 | 0000 | 0000 |
| +08h | 06F0 | 06F0 | 06F0 | 06F0 | 06F0 |
| +0Ah | 0024 | 0024 | 0024 | 0024 | 0024 |
| +0Ch | 0000 | 0000 | 0000 | 0000 | 0000 |
| +0Eh | 0000 | 0000 | 0000 | 0000 | 0000 |
| +10h | 0001 | 0001 | 0001 | 0001 | 0001 |
| +12h | 0016 | 0016 | 0016 | 0016 | 0016 |
| +14h | 0000 | 0000 | 0000 | 0000 | 0000 |
| +16h | 0066 | 0062 | 0064 | 0046 | 003C |

Die übrigen WORDs bei `+18h` und `+1Ah` bis `+1Eh` sind in allen fünf Fällen null.

## 3. Vergleich mit BOUNCE.GEO und BCOLTEST.GEO

In den Ressourcen 3–10 von BOUNCE.GEO und BCOLTEST.GEO wurde folgende Struktur beobachtet:

- `+02h = 0020h`
- `+04h` ist `E000h` oder `C000h`
- `+06h = 0002h`
- `+08h` ist ein Grenzwert innerhalb oder am Ende der Ressource
- `+0Ah` stimmt mit der Anzahl der bekannten WORD-Tabellenplätze überein
- `+14h` stimmt mit der Ressourcengröße überein

Die fünf Treiberressourcen 2 zeigen dagegen:

- `+02h = 0020h` – gleich
- `+04h = 0000h` und `+06h = 0000h` – abweichend
- `+08h = 06F0h` – exakt gleich der vollständigen Ressourcengröße
- `+0Ah = 0024h` – konstant 36, nicht die zuvor ermittelte Tabellenanzahl 14, 6 oder 2
- `+14h = 0000h` – keine Übereinstimmung mit der Ressourcengröße

Damit ist belegt, dass die Felder `+08h`, `+0Ah` und `+14h` nicht ohne Weiteres mit derselben Bedeutung über unterschiedliche Ressourcentypen hinweg interpretiert werden dürfen.

## 4. Was diese Gegenprobe aussagt – und was nicht

**Gesichert:**
1. Fünf zusätzliche Dateien besitzen die GEOS-1.x-Signatur und werden als GEOS-1.x-Geodes erkannt.
2. Alle fünf enthalten drei Ressourcen.
3. Ressource 2 ist in allen fünf Dateien 1.776 Bytes groß und hat denselben 32-Byte-Anfang, bis auf das WORD bei `+16h`.
4. In diesen Treiberressourcen ist `+08h = 06F0h`, also die Ressourcengröße.
5. `+0Ah = 0024h` und `+14h = 0000h`; damit passt die Interpretation von `+0Ah` als Anzahl der Tabellenplätze aus den Ressourcen 3–10 nicht auf diese Ressource 2.

**Nicht bewiesen:**
- Die semantische Bedeutung der Felder in der Treiberressource 2.
- Dass `+0Ah` hier tatsächlich eine andere Art von Anzahl oder Handle-Tabelle beschreibt.
- Dass die Ressourcen 2 der fünf Treiber untereinander vollständig identisch sind; nur die ersten 32 Bytes und die Größe wurden hier verglichen.
- Dass die Headerstruktur von BOUNCE/BCOLTEST in allen anderen GeoWorks-1.x-Programmen oder Ressourcentypen gilt.

## 5. Konsequenz für GeoViewPlus

Keine Codeänderung. Der Parser muss Ressourcen zunächst nach ihrem tatsächlichen Typ bzw. ihrer Struktur klassifizieren, bevor Felder wie `+08h`, `+0Ah` oder `+14h` semantisch interpretiert werden.

Die in Untersuchung 165 gefundene Beziehung zwischen `+0Ah` und Tabellenplätzen bleibt ein lokaler Befund für die untersuchten Ressourcen 3–10 von BOUNCE.GEO und BCOLTEST.GEO. Sie darf nicht als universelle GeoWorks-1.x-Regel implementiert werden.

## 6. Integrität und Versionsgrenze

- Alle fünf zusätzlichen GEO-Dateien ausschließlich lesend untersucht.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Icon-/Moniker-Zuordnung vorgenommen.
- Keine PC/GEOS-2.x-Struktur als Beleg für GeoWorks 1.x verwendet.
