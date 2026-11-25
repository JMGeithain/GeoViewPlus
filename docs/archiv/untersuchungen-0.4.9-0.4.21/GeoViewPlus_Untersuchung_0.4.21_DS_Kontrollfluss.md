# GeoView Plus – Untersuchung 0.4.21
## Kontrollfluss und DS-Erhaltung am Schreibkandidaten FFFAh

**Geltungsbereich:** ausschließlich PC/GEOS 1.x / GeoWorks 1.2.  
**Quelle:** `GEOWORKS.zip`, Einträge `GEOWORKS/KERNEL.EXE` und `GEOWORKS/KERNEL.OLD`.  
**Methode:** Originaleinträge frisch aus dem ZIP-Archiv extrahiert; MZ-Header von `0600h` Bytes berücksichtigt; statische 8086-Disassemblierung. Adressen sind Ladebildoffsets. Keine Laufzeittests, keine Änderungen an Originaldateien.

## 1. Integrität der verwendeten Kerneldateien

| Datei | Größe | SHA-256 |
|---|---:|---|
| `KERNEL.EXE` | 72.736 Bytes | `c2cc8952cdb01d0f459bf281ee3b78f8ce9464aba0b58c3758f8c73e24fb6eb5` |
| `KERNEL.OLD` | 72.688 Bytes | `bd4d680b15f8dd66b2b09b506de96672972f716a11e0a38220477bf07b6c1e9b` |

Die Werte stimmen mit dem zuvor dokumentierten Archivvergleich überein.

## 2. Korrekte Abgrenzung der Routine in KERNEL.EXE

Der lineare Disassembler zeigt ab `FFB7h` zunächst Dateinamensdaten (`kbd.geo`, `nimbus.geo`, `ui.geo`, `disk.geo`). Der Stringbereich endet mit dem Nullbyte bei `FFD9h`. Der Codepfad beginnt danach:

```asm
FFDA  BA 40 0B       mov dx,0B40h
FFDD  BE 37 0B       mov si,0B37h
FFE0  E8 A6 01       call 0189h
FFE3  72 05          jb FFEAh
FFE5  E8 FC 01       call 01E4h
FFE8  73 10          jae FFFAh
FFEA  BE 87 06       mov si,0687h
FFED  E8 8B 01       call 017Bh
FFF0  73 08          jae FFFAh
FFF2  9A 99 03 00 00 call far 0000:0399h
FFF7  B8 10 00       mov ax,0010h
FFFA  89 1E 0F 06    mov [060Fh],bx
FFFE  E8 CB 01       call 01CCh
10001 C3             ret
```

Damit ist `FFFAh` Teil dieses Kontrollflusses. Der Schreibbefehl ist als Instruktion bestätigt; die Zielsegmentzuordnung ist damit noch nicht bestätigt.

## 3. Aufruf und Segmenterhaltung

Der direkte Aufruf erfolgt bei `FF9Dh`:

```asm
FF92  E8 0A 01       call 009Fh
FF95  B0 01          mov al,01h
FF97  BB F5 00       mov bx,00F5h
FF9A  E8 19 FB       call FAB6h
FF9D  E8 3A 00       call FFDAh
```

Der Hilfsaufruf `FAB6h` sichert `DS` am Eintritt und stellt es vor der Rückkehr wieder her:

```asm
FAB6  51             push cx
FAB7  52             push dx
FAB8  06             push es
FAB9  1E             push ds
...
FAF2  1F             pop ds
FAF3  07             pop es
FAF4  5A             pop dx
FAF5  59             pop cx
FAF6  C3             ret
```

Der unmittelbar vorausgehende Aufruf `FEEDh` sichert ebenfalls `DS` und restauriert es (`FEEDh: push ds`, `FF02h: pop ds`, Rückkehr bei `FF0Fh`). Im sichtbaren Pfad zwischen diesen Sicherungs-/Wiederherstellungspunkten und `FFFAh` ist kein abschließender Wechsel auf `DS=CS` oder ein anderes Segment zu sehen. Die Routine verwendet damit den beim Eintritt in den übergeordneten Pfad geltenden DS-Wert.

## 4. Was damit bewiesen ist – und was offen bleibt

**Bewiesen:**
- `FFFAh` ist ein echter Schreibbefehl in einem aufrufbaren Codepfad.
- Er schreibt den Inhalt von BX nach `DS:060Fh`.
- Die unmittelbar davor untersuchten Hilfsroutinen restaurieren DS; sie liefern keinen Beleg für einen Wechsel auf das Kernel-Datensegment.
- Der direkte Aufruf erfolgt bei `FF9Dh`.

**Noch offen:**
- Welchen konkreten Wert DS beim Eintritt in den Pfad `FF92h` besitzt.
- Ob dieser Wert `0E34h` ist.
- Ob `FFFAh` folglich tatsächlich `0E34h:060Fh` beschreibt.

Daher bleibt `FFFAh` ein **bestätigter Schreibbefehl mit unbestätigtem Zielsegment**. Er darf nicht als bestätigter Kernel-Datensegment-Schreiber geführt werden.

## 5. Vergleichshinweis zu KERNEL.OLD

Im älteren Kernel steht der entsprechende Schreibbefehl bei `FFCAh` und adressiert `DS:0605h`. Die Instruktionspositionen und Feldoffsets sind gegenüber `KERNEL.EXE` verschoben. Für `KERNEL.OLD` ist der Segmentwert an dieser Stelle gesondert zu verfolgen; eine automatische Gleichsetzung der Felder ist nicht zulässig.

## 6. Nächster Schritt

Als nächstes ist der Eintritt in den übergeordneten Initialisierungspfad zu verfolgen: Wer ruft den Block mit `FF92h` auf, welches Segment ist beim Eintritt aktiv, und bleibt es über die Aufrufe `009Fh` und `FAB6h` erhalten? Erst danach kann `FFFAh` als Kernel-Datenfeldschreiber bestätigt oder ausgeschlossen werden.

**Integrität:** Originaldateien wurden ausschließlich aus dem Archiv gelesen. Keine Binärdatei wurde verändert oder ausgeführt.
