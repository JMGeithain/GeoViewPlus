# Untersuchung 186 – Feldanalyse des Snapshot-Bereichs 0FE2h–0FF2h

**Projekt:** GeoViewPlus  
**Datei:** KERNEL.EXE aus Basebox-SVGA-Ensemble12  
**Methode:** statische 8086-Disassemblierung des MZ-Ladebereichs; direkte Segmentzugriffe und Instruktionskontexte geprüft  
**Abgrenzung:** ausschließlich GeoWorks / PC/GEOS 1.x.

## 1. Ziel und Korrektur der Ausgangsannahme

Untersuchung 185 zeigte, dass Routine 95A3h neun WORDs ab DS:0FE2h in einen Snapshotbereich ab DS:0FCEh kopiert und anschließend neun WORDs ab 0FE2h löscht.

Der Bereich umfasst genau diese neun WORD-Offsets:

    0FE2h  0FE4h  0FE6h  0FE8h  0FEAh
    0FECh  0FEEh  0FF0h  0FF2h

Die vorliegende Untersuchung prüft die einzelnen Felder. Das Ergebnis korrigiert eine zu enge Interpretation: Der Bereich enthält nicht nur Timerwerte. Er ist ein gemeinsamer Snapshot-/Zählerbereich, in dem mehrere voneinander unterscheidbare Aktivitätszähler geführt werden.

## 2. Direkte Referenzen im Code

Die lineare Disassemblierung enthält folgende bestätigte direkte Speicherzugriffe innerhalb des Bereichs:

| Offset | Instruktionen / Fundstellen | Befund |
|---|---|---|
| 0FE2h | INC bei 9AE1h, 11516h, 115A6h; MOV/XCHG/Reset bei 1152Ah, 115B2h, 115C6h | niedriger WORD des Timer-/Wartezählers |
| 0FE4h | INC bei 9AE7h, 1151Ch, 115ACh; XCHG/Reset bei 11526h, 115C3h | hoher WORD des Timer-/Wartezählers |
| 0FE6h | ADD bei 7701h | akkumuliert einen übergebenen WORD-Wert |
| 0FE8h | INC bei 7705h | zählt Ereignisse der zugehörigen Routine |
| 0FEAh | ADD bei 7799h | akkumuliert einen übergebenen WORD-Wert |
| 0FECh | INC bei 779Dh | zählt Ereignisse der zugehörigen Routine |
| 0FEEh | INC bei 9AF1h | wird nach dem Aufruf 9CE0h erhöht |
| 0FF0h | INC bei 97CDh und 9E6Ch | wird in zwei getrennten Routinen erhöht |
| 0FF2h | kein direkter absoluter Segmentzugriff in der linearen Code-Disassemblierung gefunden | direkte Funktion offen |

Die Treffer wurden anhand der Instruktionsbytes und des lokalen Codekontexts geprüft. Ein bloßes Vorkommen des Zahlenwertes in Daten wurde nicht als Speicherzugriff gezählt.

## 3. Felder 0FE2h und 0FE4h: Warte-/Schleifenzähler

Diese beiden WORDs werden als Paar behandelt:
- Routine 9AC0h wartet auf das Ereignisflag 0FFEh und erhöht 0FE2h; bei Überlauf erhöht sie 0FE4h.
- Routine 11511h erhöht das Paar ebenfalls und übernimmt beide WORDs anschließend gemeinsam in DX:AX.
- Routine 1159Fh erhöht das Paar während einer weiteren Wartephase. Danach wird der niedrige WORD-Wert 0FE2h mit 30 multipliziert und in 1088h/108Ah gespeichert.
- Die beiden WORDs werden nach den Berechnungen zurückgesetzt.

Damit ist ihre Funktion als gemeinsamer 32-Bit-Schleifen-/Wartezähler bestätigt. Dass der zweite Teil der Berechnung bei 1159Fh nur 0FE2h multipliziert, bleibt als Besonderheit bestehen.

## 4. Felder 0FE6h und 0FE8h

Die Routine ab 76E5h enthält bei 7701h/7705h:

    76FD  cli
    76FE  mov ax,WORD PTR [bx+2]
    7701  add WORD PTR ds:0FE6h,ax
    7705  inc WORD PTR ds:0FE8h
    7709  sti

Die Routine übernimmt einen WORD-Wert aus einem über BX adressierten Datensatz, addiert ihn zum Summenfeld 0FE6h und erhöht den zugehörigen Zähler 0FE8h. Die Aktualisierung ist durch CLI/STI geschützt.

Das belegt eine Summe-plus-Anzahl-Kombination. Was genau die addierte Größe repräsentiert, ist aus diesem lokalen Ausschnitt nicht sicher abzuleiten. Die umgebende Routine verarbeitet einen über BX/SI referenzierten Eintrag und ruft danach weitere Verwaltungsroutinen auf.

## 5. Felder 0FEAh und 0FECh

Eine zweite, strukturell ähnliche Folge liegt bei 7799h/779Dh:

    7795  cli
    7796  mov ax,WORD PTR [bx+2]
    7799  add WORD PTR ds:0FEAh,ax
    779D  inc WORD PTR ds:0FECh
    77A1  sti

Auch hier wird ein WORD-Wert aus einem Datensatz zu einer Summe addiert und ein Zähler inkrementiert. Die zwei Felder bilden daher ebenfalls ein Summe-plus-Anzahl-Paar.

Die beiden Paare 0FE6h/0FE8h und 0FEAh/0FECh werden in getrennten Pfaden aktualisiert. Eine semantische Bezeichnung der jeweiligen Kategorien ist noch nicht belegt.

## 6. Feld 0FEEh

In Routine 9AC0h wird nach dem Warten auf 0FFEh und nach dem Aufruf von 9CE0h das WORD-Feld 0FEEh erhöht:

    9AED  cli
    9AEE  call 9CE0h
    9AF1  inc WORD PTR ds:0FEEh

Der Zugriff liegt innerhalb eines größeren Ablaufes, der den Stackzustand wechselt und Kernel-/Prozesszustand sichert. Damit ist der Zusammenhang mit diesem Ablauf belegt, aber die Bedeutung des Zählers bleibt offen.

## 7. Feld 0FF0h

Zwei direkte Inkrementierungen:
- 97CDh in einer FAR-Routine, die zuvor DS auf 0E34h setzt und außerdem 1006h inkrementiert.
- 9E6Ch in der Routine ab 9E5Bh, die auch 10A3h dekrementiert, einen PIC-Befehl über Port 20h ausgibt und 1098h/1097h/109Ch verändert.

Die zweite Routine ist Teil einer zeit-/interruptnahen Verarbeitung. Das allein beweist aber nicht, dass 0FF0h ausschließlich ein Timerwert ist: Das Feld wird zusätzlich in der anderen Routine bei 97CDh erhöht. Eine gemeinsame semantische Interpretation ist noch offen.

## 8. Feld 0FF2h

Für 0FF2h wurde kein direkter absoluter Segmentzugriff in der linearen Code-Disassemblierung gefunden. Das Feld wird jedoch von Routine 95A3h als neuntes WORD des Snapshotbereichs mitkopiert und anschließend auf null gesetzt.

Das Fehlen direkter Treffer beweist nicht, dass das Feld unbenutzt ist. Es könnte indirekt über Register-/Zeigerzugriffe oder von Code außerhalb der korrekt linear disassemblierten Bereiche verwendet werden.

## 9. Bedeutung des Snapshot-Verfahrens

Routine 95A3h führt folgende Operationen aus:

    mov si,0FE2h
    mov di,0FCEh
    mov cx,9
    rep movsw

    mov di,0FE2h
    xor ax,ax
    mov cx,9
    rep stosw

Sie liest also die neun WORDs als zusammenhängenden Block aus und setzt danach alle neun Felder zurück. Routine 958Dh kopiert zehn WORDs ab 0FCEh an den vom Aufrufer vorgegebenen Zielort.

Das ist ein Snapshot-and-clear-Verfahren. Es erlaubt einem Aufrufer, die seit dem letzten Snapshot angesammelten Werte auszulesen, während der Kernel anschließend wieder bei null zählt. Die genaue API-Bezeichnung und die Feldnamen sind noch nicht bekannt.

## 10. Ergebnis

Die neun WORDs bilden einen gemeinsamen Snapshotbereich, aber keinen einheitlichen Timerzähler:

- 0FE2h/0FE4h: 32-Bit-Warte-/Schleifenzähler.
- 0FE6h/0FE8h: Summe und Anzahl in einem eigenen Verwaltungs-/Ereignispfad.
- 0FEAh/0FECh: zweites Summe-/Anzahl-Paar in einem anderen Pfad.
- 0FEEh: separater Ablaufzähler nach Routine 9CE0h.
- 0FF0h: Zähler mit mindestens zwei getrennten Inkrementierungsstellen.
- 0FF2h: als Snapshotfeld vorhanden, direkte Verwendung noch offen.

Die Bezeichnung der Summe-/Anzahl-Paare als Statistikzähler ist eine strukturelle Beschreibung, kein nachgewiesener offizieller Name.

## 11. Nächster Schritt

Die Routinen um 76E5h/7795h sowie die FAR-Routine 958Dh sollen weiter zurückverfolgt werden. Insbesondere müssen die Aufrufer und die Bedeutung der über BX+2 übergebenen WORD-Werte gefunden werden. Das könnte die Felder 0FE6h/0FE8h und 0FEAh/0FECh semantisch identifizieren.

Es wurden keine Originaldateien verändert und keine Laufzeittests durchgeführt.
