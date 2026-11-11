# Untersuchung 174 – Aufbau und Grenzen der vorliegenden KERNEL.EXE

## Ziel

Die elf in Untersuchung 173 gruppierten FAR-CALL-Ziel-Offsets sollen mit der im SVGA-Ensemble enthaltenen `KERNEL.EXE` abgeglichen werden. Diese Untersuchung prüft zuerst Dateiformat, DOS-Ladebereich und die unmittelbare Bedeutung der Offsetwerte. Eine Kernel-Funktionsbenennung wird nur vorgenommen, wenn sie durch konkrete Daten belegt ist.

## Untersuchte Datei

Pfad im Archiv:

`Basebox-SVGA-Ensemble12/source/pm-backport/target-original/GWSVGA/KERNEL.EXE`

- Dateigröße: 72.736 Byte
- SHA-256: `c2cc8952cdb01d0f459bf281ee3b78f8ce9464aba0b58c3758f8c73e24fb6eb5`
- Dateianfang: `4D 5A` (`MZ`)
- Copyright-Zeichenfolge im DOS-Headerbereich: `Copyright GeoWorks 1991`

Der Hash dient dazu, genau dieses Exemplar von anderen gleichnamigen Kernel-Dateien zu unterscheiden. Die Copyright-Zeichenfolge allein beweist keine genaue Versionsnummer oder Binärkompatibilität.

## 1. MZ-Header

Die relevanten DOS-MZ-Felder wurden little-endian aus dem Dateianfang gelesen:

| Feld | Wert |
|---|---:|
| Signatur | `MZ` |
| Bytes im letzten Dateisegment (`e_cblp`) | 32 |
| Dateisegmente (`e_cp`) | 143 |
| DOS-Relokationseinträge (`e_crlc`) | 276 (`0114h`) |
| Headergröße (`e_cparhdr`) | 96 Paragraphen |
| Headergröße in Byte | 1.536 (`0600h`) |
| Relokationstabelle ab | `003Ch` |
| Initialer `CS:IP` | `0000:02B1` |

Die MZ-Dateilänge ist mit den Feldern konsistent: `142 × 512 + 32 = 72.736` Byte. Der DOS-Ladebereich beginnt nach dem 1.536 Byte großen MZ-Header bei Dateioffset `0600h`.

## 2. Warum die elf Treiber-Offsets nicht direkt Kernel-Dateioffsets sind

Die aus den SVGA-Treibern ermittelten Zielwerte lauten:

`0000h, 0002h, 0005h, 0006h, 00AAh, 00ABh, 00C2h, 00D0h, 0126h, 01C2h, 01C4h`.

Ein rein mechanischer Abgleich mit dem Anfang des MZ-Ladebereichs ergibt:

| Zielwert | Dateioffset im MZ-Ladebereich | Bytes am Ziel (Anfang) |
|---:|---:|---|
| `0000h` | `0600h` | `00 00 00 00 00 00 00 6B 65 72 6E 65 6C...` |
| `0002h` | `0602h` | `00 00 00 00 00 6B 65 72 6E 65 6C...` |
| `0005h` | `0605h` | `00 00 6B 65 72 6E 65 6C 2E 65 78...` |
| `0006h` | `0606h` | `00 6B 65 72 6E 65 6C 2E 65 78 65...` |
| `00AAh` | `06AAh` | `E9 00 B4 09 CD 21 B8 07 0C CD 21...` |
| `00ABh` | `06ABh` | `00 B4 09 CD 21 B8 07 0C CD 21 3C...` |
| `00C2h` | `06C2h` | `8C C1 BB FF FF B4 4A CD 21 73 3C...` |
| `00D0h` | `06D0h` | `75 2B 06 8C C0 8E 06 00 00 03 C3...` |
| `0126h` | `0726h` | `03 B9 22 00 F3 A5 91 BB 9D 03 0E E8...` |
| `01C2h` | `07C2h` | `0E CD 21 8B D3 B4 3B CD 21 5A CB...` |
| `01C4h` | `07C4h` | `21 8B D3 B4 3B CD 21 5A CB 36 A3...` |

Die Stellen im Bereich `0600h` bis `07C4h` liegen im DOS-Ladebereich. Die Bytes bei `00AAh` und den benachbarten Zielen enthalten unter anderem DOS-Interrupt-Aufrufe (`CD 21`). Das ist kein Nachweis dafür, dass die gleichlautenden Werte aus den Treiber-Relokationen auf diese Dateistellen zeigen.

**Schlussfolgerung:** Die Treiber-Offsets sind Werte in dem vom Relokationstyp bezeichneten Kernel-Segment-/Importkontext. Die vorliegende MZ-Datei darf nicht ohne Nachweis als flach adressierbarer Speicherbereich behandelt werden. Der direkte Vergleich `MZ-Ladebasis + Zieloffset` liefert keine gültige Funktionsnamenszuordnung.

## 3. Eingebettete Signaturfolge

In der Datei findet sich einmal die Bytefolge `C7 45 CF 53` bei Dateioffset `F9F6h`. Wenn man 200 Byte davor eine GEOS-Headerposition annimmt, ergeben die dort gelesenen Ressourcenzähler jedoch null Ressourcen.

Damit ist diese einzelne Signaturfolge **kein ausreichender Beleg**, dass an dieser Stelle ein vollständiger, regulärer GEO-Geode-Header beginnt. Sie wird hier ausdrücklich nicht als Kernel-Geode-Header klassifiziert.

## 4. Konsequenz für die weitere Analyse

Die vorliegende `KERNEL.EXE` ist ein MZ-DOS-Programm. Für eine belastbare Zuordnung der Kernel-Funktionsziele müssen wir zuerst die tatsächliche Segment-/Export-/Importadressierung der GeoWorks-1.x-Kernel-Schnittstelle rekonstruieren. Die 276 MZ-Relokationseinträge sind DOS-Laderelokationen und dürfen nicht mit den 72 GeoWorks-Relokationseinträgen der Treiber-Ressource 1 vermischt werden.

Insbesondere gilt:

- Die 44 `info=00h`-Einträge der Treiber bleiben als FAR-CALL-Operanden bestätigt.
- Die elf gespeicherten Offsetwerte bleiben bestätigt.
- Kein symbolischer Kernel-Funktionsname wird aus dem MZ-Offsetvergleich abgeleitet.
- Die MZ-Relokationstabelle und die GeoWorks-Relokationstabelle sind zwei verschiedene Ebenen.

## 5. Nächster Schritt

Untersuchung 175 sollte die MZ-Relokationstabelle und den DOS-Ladebereich getrennt kartieren und danach nach einem belastbaren GeoWorks-1.x-Kernel-Export-/Dispatch-Verzeichnis suchen. Dafür sind insbesondere die im Ensemble enthaltenen Kernel- und Treiberdateien sowie die tatsächliche Relokationssemantik relevant. Moderne PC/GEOS-2.x- oder FreeGEOS-Quellen dürfen dabei nur als Vergleich, nicht als Beweis für GeoWorks 1.x dienen.

---
*Read-only-Analyse. Die KERNEL.EXE im ZIP wurde nicht verändert. Keine Änderung am GeoViewPlus-Programmcode.*
