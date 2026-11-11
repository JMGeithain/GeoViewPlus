# Untersuchung 186 – Feldanalyse des Snapshot-Bereichs 0FE2h–0FF2h

**Projekt:** GeoViewPlus  
**Datei:** KERNEL.EXE aus Basebox-SVGA-Ensemble12  
**Methode:** schreibgeschützte statische Analyse des MZ-Ladebereichs und 8086-Disassemblierung  
**Abgrenzung:** GeoWorks / PC/GEOS 1.x. Keine Laufzeittests.

## 1. Ziel und Umfang

Die Routine 95A3h kopiert neun WORDs ab DS:0FE2h in einen Snapshotbereich ab DS:0FCEh und löscht danach die neun Quell-WORDs. Der untersuchte Bereich lautet damit:

- 0FE2h
- 0FE4h
- 0FE6h
- 0FE8h
- 0FEAh
- 0FECh
- 0FEEh
- 0FF0h
- 0FF2h

Die gemeinsame Snapshot-Behandlung beweist, dass die neun WORDs zusammenhängend gesichert und zurückgesetzt werden. Sie beweist nicht, dass alle neun Felder dieselbe semantische Funktion haben.

## 2. Snapshot- und Reset-Routine 95A3h

Die relevante Befehlsfolge:

    95A3  push cx
    95A4  push si
    95A5  push di
    95A6  push es
    95A7  mov si,ds
    95A9  mov es,si
    95AB  mov si,0FE2h
    95AE  mov di,0FCEh
    95B1  mov cx,0009h
    95B4  rep movsw
    95B6  mov di,0FE2h
    95B9  xor ax,ax
    95BB  mov cx,0009h
    95BE  rep stosw
    95C0  mov bx,0FF8h
    95C3  cmp word ptr ds:0FF6h,ax
    95C7  jne 95D0
    95C9  mov bx,[bx+6]
    95CC  or bx,bx
    95CE  je 95D3
    95D0  inc ax
    95D1  jmp 95C9
    95D3  mov ds:0FE0h,ax
    95D6  pop es
    95D7  pop di
    95D8  pop si
    95D9  pop cx
    95DA  ret

Die Kopie und das Löschen umfassen jeweils neun WORDs. Das entspricht 18 Bytes, von 0FE2h bis einschließlich 0FF3h. Das letzte WORD beginnt bei 0FF2h.

Die anschließende Schleife prüft 0FF6h und folgt einer verketteten Struktur, deren Startadresse bei 0FF8h liegt. Diese Felder gehören nicht zum Neun-WORD-Snapshot, sind aber für den Ablauf der Routine relevant.

## 3. Feld 0FE2h und 0FE4h – Timer-/Schleifenzähler

Die Felder werden gemeinsam inkrementiert:
- 0FE2h ist das niedrige WORD.
- Bei Überlauf wird 0FE4h als hohes WORD erhöht.

Das ist in den Schleifen bei 9AE1h und 115A6h direkt zu sehen. In der Routine 11511h werden beide WORDs mit XCHG gemeinsam in DX:AX übernommen. Die Routine 1159Fh multipliziert das niedrige WORD mit 30 und schreibt das Produkt nach 1088h/108Ah.

**Bewertung:** gemeinsamer 32-Bit-Zähler in den untersuchten Warte-/Schleifenroutinen. Die konkrete Zeiteinheit ist nicht bestätigt.

## 4. Feld 0FE6h und 0FE8h – gemeinsames Additions-/Ereignispaar

Die Routine bei 76E5h enthält:

    76FD  cli
    76FE  mov ax,WORD PTR [bx+0x2]
    7701  add WORD PTR ds:0FE6h,ax
    7705  inc WORD PTR ds:0FE8h
    7709  sti

Damit wird ein WORD-Wert aus einer durch BX adressierten Struktur zum Feld 0FE6h addiert; 0FE8h wird im selben kritischen Abschnitt inkrementiert.

Der Kontext zeigt eine Verarbeitung einer Struktur mit weiteren Feldern und indirekten Aufrufen. Die genaue Bedeutung des Quellwertes [BX+2] ist ohne Rekonstruktion des Objekt-/Callback-Typs nicht gesichert.

**Bewertung:** zusammengehöriges Paar aus akkumuliertem WORD-Wert und separat erhöhtem WORD-Zähler ist plausibel und durch gemeinsame Aktualisierung gestützt. Feldnamen und Semantik bleiben offen.

## 5. Feld 0FEAh und 0FECh – zweites Additions-/Ereignispaar

Die Routine ab 7763h verarbeitet eine weitere Struktur und endet mit:

    7795  cli
    7796  mov ax,WORD PTR [bx+0x2]
    7799  add WORD PTR ds:0FEAh,ax
    779D  inc WORD PTR ds:0FECh
    77A1  sti

Auch hier wird ein WORD aus [BX+2] zu einem akkumulierten Feld addiert und ein zweites WORD im selben kritischen Abschnitt erhöht.

**Bewertung:** strukturell analog zum Paar 0FE6h/0FE8h. Eine gemeinsame Funktion beider Paare ist durch das Muster nahegelegt, aber nicht abschließend bewiesen.

## 6. Feld 0FEEh – separater Zähler

In der Routine ab 9AC0h wird nach dem Ende einer Wartephase und nach einem Aufruf bei 9CE0h ausgeführt:

    9AED  cli
    9AEE  call 9CE0h
    9AF1  inc WORD PTR ds:0FEEh
    9AF5  mov WORD PTR ds:0FF6h,si

0FEEh wird hier separat inkrementiert. Eine Addition aus einem anderen Feld oder ein Überlaufverbund mit einem benachbarten WORD ist in diesem Kontext nicht zu sehen.

**Bewertung:** eigenständiger WORD-Zähler; seine fachliche Bedeutung ist offen.

## 7. Feld 0FF0h – separates Inkrement, weitere Verwendung

Für 0FF0h wurden WORD-Inkremente bei 97CDh und 9E6Ch gefunden. Die Routine bei 9E5Bh ist ein weiterer zeit-/interruptnaher Ablauf: Sie arbeitet mit dem Kernel-Datensegment 0E34h, dekrementiert 10A3h und erhöht 0FF0h sowie 1098h. Daraus allein folgt nicht, dass 0FF0h ein Zeitwert ist.

In anderen Routinen wird der konstante Offset 0FF0h als Basisregister verwendet, um auf DS:0FFCh zuzugreifen. Das ist ein Zugriff auf das Feld 0FFCh, nicht auf den Inhalt von 0FF0h. Diese Unterscheidung ist wichtig, damit kein falscher Feldverweis angenommen wird.

**Bewertung:** separates WORD-Inkrementfeld; Bedeutung noch nicht bestimmt.

## 8. Feld 0FF2h – kein eigenständiger Zugriff nachgewiesen

In der geprüften linearen Disassemblierung wurde kein eindeutiger direkter Codezugriff auf DS:0FF2h als Einzeloperand gefunden. Das Feld wird jedoch als neuntes WORD durch die Snapshot-/Reset-Routine 95A3h kopiert und gelöscht.

**Bewertung:** Teil des gesicherten Snapshot-Bereichs; eigenständige Funktion unbekannt. Das Fehlen eines direkten Treffers in der linearen Disassemblierung ist kein Beweis, dass das Feld nie indirekt oder über andere Mechanismen verwendet wird.

## 9. Feldübersicht

| Offset | Befund | Sicherheit |
|---|---|---|
| 0FE2h | niedriges WORD des gemeinsam erhöhten Zählers | direkt belegt |
| 0FE4h | hohes WORD / Überlaufwort | direkt belegt |
| 0FE6h | Akkumulator: Addition von [BX+2] | direkt belegt |
| 0FE8h | Zähler, gemeinsam mit 0FE6h aktualisiert | direkt belegt |
| 0FEAh | zweiter Akkumulator: Addition von [BX+2] | direkt belegt |
| 0FECh | Zähler, gemeinsam mit 0FEAh aktualisiert | direkt belegt |
| 0FEEh | separat inkrementierter WORD-Zähler | direkt belegt |
| 0FF0h | separat inkrementierter WORD-Zähler | direkt belegt |
| 0FF2h | nur im Snapshot-/Reset-Block als WORD enthalten | begrenzter Befund |

## 10. Schlussfolgerung

Der Bereich 0FE2h–0FF2h ist eine zusammenhängende, neun WORD große Snapshot-Gruppe. Er ist aber intern heterogen:

1. Ein Timer-/Schleifenzählerpaar (0FE2h/0FE4h).
2. Zwei analog aktualisierte Akkumulator-/Zählerpaare (0FE6h/0FE8h und 0FEAh/0FECh).
3. Zwei separat inkrementierte WORD-Felder (0FEEh und 0FF0h).
4. Ein Feld 0FF2h, dessen eigenständige Funktion noch offen ist.

Die Snapshot-Routine 95A3h löscht die neun WORDs nach dem Kopieren. Das spricht für eine Sammel-/Intervallauswertung, aber die Absicht des Designs und die Namen der Felder sind ohne weitere Leser und Aufrufer nicht gesichert.

## 11. Nächster Schritt

Als nächstes sollten die Leser der Snapshot-Kopie ab 0FCEh untersucht werden. Sie können die Bedeutung der neun Felder erschließen, weil die Daten dort nach dem Zurücksetzen der Originalfelder weiter verfügbar sind. Außerdem sollten die Objektstrukturen an [BX+2] in den Routinen 76E5h und 7763h identifiziert werden.

Es wurden keine Originaldateien verändert und keine Laufzeittests durchgeführt.
