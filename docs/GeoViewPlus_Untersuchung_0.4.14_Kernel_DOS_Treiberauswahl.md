# GeoView Plus – Untersuchung 0.4.14
## DOS-Treiberauswahl und Far-Pointer-Aufbau im Kernel

**Gegenstand:** ausschließlich PC/GEOS 1.x; deutsche GeoWorks-1.2-Installation.  
**Datei:** `KERNEL.EXE`, ergänzend Abgleich mit `KERNEL.OLD` noch ausstehend.  
**Untersuchungsbereich:** kopiertes Kernel-Segment `0F93h`, insbesondere `121Ah–12D6h`.  
**Originaldateien:** unverändert. Es wurden ausschließlich statische Bytes und Instruktionen untersucht.

## 1. Kernergebnis

Die Routine wählt anhand des Bytes `DS:[05ABh]` einen Dateinamen aus einer im Code-Segment liegenden Tabelle aus. Die sichtbaren Einträge sind:

- `DOS2.GEO`
- `DOS3.GEO`
- `DOS4.GEO`
- `DOS5.GEO`
- `DRDOS.GEO`

Der ausgewählte Eintrag wird über `SI` an eine nachfolgende Routine weitergegeben. Nach einem weiteren Aufruf werden zwei Wörter von `[SI]` und `[SI+2]` gelesen und als Far-Pointer unter `DS:05B8h`/`DS:05BAh` gespeichert. Bei gesetztem Bit `10h` in `ES:[0003h]` wird dieser Pointer indirekt aufgerufen.

Damit ist die Verbindung zwischen DOS-Treiber-Auswahl, dem dynamischen Far-Pointer und dem in Untersuchung 0.4.13 festgestellten Überschreiben von `DS:05BAh` konkret belegt.

## 2. Tabellenaufbau bei `CS:121Ah`

Der Code lädt zunächst `SI=1246h`. Das ist der Beginn des Strings `DRDOS.GEO`.

Wenn `DS:[05B1h]` gleich null ist, wird der Auswahlpfad ausgeführt:

1. `BL = DS:[05ABh]`, `BH=0`.
2. `BX -= 2`.
3. Bei Unterlauf (`JB`, Ziel `126Fh`) erfolgt ein Fehler-/Fallback-Aufruf; anschließend wird `AX=0019h` gesetzt.
4. `BX` wird verdoppelt.
5. `SI = word ptr CS:[BX+121Ah]`.

Die Wörter am Tabellenanfang lauten:

| Tabellenindex | Wortwert | Zielstring | Bei `DS:[05ABh]` |
|---:|---:|---|---:|
| 0 | `1222h` | `DOS2.GEO` | 2 |
| 1 | `122Bh` | `DOS3.GEO` | 3 |
| 2 | `1234h` | `DOS4.GEO` | 4 |
| 3 | `123Dh` | `DOS5.GEO` | 5 |
| 4 | `1246h` | `DRDOS.GEO` | 6 |

Die Zuordnung ergibt sich direkt aus den Tabellenwörtern, dem Indexausdruck und den NUL-terminierten ASCII-Strings im Kernel-Abbild. Der Initialwert `SI=1246h` entspricht ebenfalls `DRDOS.GEO`, wird aber im Null-Zweig von `DS:[05B1h]` durch die Tabellenwahl überschrieben.

## 3. Verzweigung über `DS:[05B1h]`

Bei `1258h` steht:

`cmp byte ptr DS:[05B1h],00h`

Wenn der Wert ungleich null ist, springt der Code direkt nach `1290h`. Der vorher gesetzte Wert `SI=1246h` bleibt damit erhalten; der ausgewählte String ist in diesem Pfad `DRDOS.GEO`.

Wenn der Wert null ist, wird der Wert aus `DS:[05ABh]` zur Tabellenindizierung verwendet. Der Pfad führt anschließend ebenfalls nach `1290h`.

Das belegt die Steuerlogik der beiden Pfade, aber noch nicht die semantische Bedeutung von `05B1h` oder `05ABh` außerhalb dieser Routine.

## 4. Übergabe des Dateinamens und Laden des Far-Pointers

Ab `1290h`:

- `DI = DS:[0044h]` – der zuvor gesicherte DS-Wert wird als Argument in `DI` übernommen.
- `push CS / pop DS` – `DS` wird auf das Kernel-Code-Segment umgestellt.
- `call 8CBh` – Aufruf einer internen Routine; deren vollständige Funktion ist noch nicht geklärt.
- Bei Carry wird ein weiterer Aufruf bei `0000:0399` ausgeführt und `AX=000Fh` gesetzt.
- `ES=AX`.
- `DS:[0613h] = BX`.
- `push DS`; Far-Aufruf `0000:257Eh`; danach `pop DS`.
- `AX = word ptr [SI]`; `BX = word ptr [SI+2]`.
- `DS:[05B8h] = AX`; `DS:[05BAh] = BX`.

Der entscheidende Punkt: Die Routine `0000:257Eh` wird mit dem ausgewählten `SI`-Wert aufgerufen bzw. erhält ihn über den Registerzustand. Danach werden die vier Bytes ab `[SI]` als Offset-/Segment-Paar übernommen. Das ist die konkrete Quelle des Far-Pointers, der in Untersuchung 0.4.13 beobachtet wurde.

Die genaue Funktion der Aufrufe `0000:0399`, `0000:257Eh` und `0000:08CBh` wird hier bewusst nicht benannt. Dazu muss der jeweilige Codepfad separat vollständig rekonstruiert werden.

## 5. Indirekter Far-Aufruf

Nach dem Speichern des Pointer-Paars:

- `test byte ptr ES:[0003h],10h`
- Wenn Bit `10h` nicht gesetzt ist, Rückkehr.
- Wenn Bit `10h` gesetzt ist, wird `BX=ES:[0040h]` geladen.
- `BL=byte ptr [BX]`.
- `DI=0014h`.
- `call far ptr DS:[05B8h]`.
- Danach wird `DI` wiederhergestellt und `BL` nach `[DI]` geschrieben.

Damit ist die bedingte Verwendung des Far-Pointers nachgewiesen. Das Bit `10h` wird aus einem durch `ES` adressierten Segment gelesen. `ES:[0040h]` ist nicht mit dem Kernel-Datenfeld `DS:[0040h]` gleichzusetzen; diese Unterscheidung war bereits in Untersuchung 0.4.13 wichtig.

## 6. Abgrenzung und offene Punkte

1. Die Tabelle und die Dateinamen sind direkt im Kernel-Abbild nachgewiesen.
2. Die Bedeutung der Konfigurations-/Statusbytes `DS:[05ABh]` und `DS:[05B1h]` ist aus diesem Ausschnitt allein nicht endgültig geklärt.
3. Die genaue Funktion der Routinen bei `0000:0399`, `0000:08CBh` und `0000:257Eh` bleibt offen.
4. Es ist noch nicht belegt, ob der ausgewählte Dateiname von `0000:257Eh` geöffnet, gesucht, geladen oder anderweitig verarbeitet wird. Die anschließende Verwendung von `[SI]` als Pointer-Quelle ist hingegen belegt.
5. Der entsprechende Code in `KERNEL.OLD` muss separat mit seinen abweichenden Segmentwerten abgeglichen werden.
6. Keine Änderung an GeoView-Plus-Quellcode, Zeichensatzzuordnungen oder GeoWorks-Originaldateien.

## 7. Nächster Schritt

Als nächstes ist die Routine bei `0000:257Eh` zu verfolgen. Dabei sind insbesondere Eingangsregister (`DS`, `ES`, `SI`, `DI`, `BX`, `AX`), Rückgaberegister und Carry-Verhalten zu dokumentieren. Danach kann geklärt werden, wie aus dem Dateinamen-Eintrag die zwei Pointer-Wörter bereitgestellt werden.

**Status:** statische Analyse der DOS-Dateinamen-Tabelle und Far-Pointer-Übergabe dokumentiert; keine Laufzeittests.
