# Untersuchung 184 – Datenfluss der Timer-Ergebnisfelder 1088h, 108Ah und 108Ch

**Projekt:** GeoViewPlus  
**Datei:** KERNEL.EXE aus Basebox-SVGA-Ensemble12  
**Methode:** vollständige lineare 8086-Disassemblierung des MZ-Ladebereichs, Prüfung aller Treffer und ihrer Instruktionskontexte  
**Abgrenzung:** GeoWorks / PC/GEOS 1.x. Statische Analyse, keine Laufzeittests.

## 1. Fragestellung

Nach der Auflösung des INT-8-Vektors (Untersuchung 183) sollten die Ergebnisfelder 1088h, 108Ah und 108Ch im gesamten Kernel verfolgt werden. Ziel war, alle Lese- und Schreibstellen zu identifizieren und die Art der Weitergabe zu bestimmen.

## 2. Trefferübersicht

Die Suche nach direkten Segmentzugriffen auf die drei Offsets ergab:

| Feld | Schreibzugriff | Lesezugriff |
|---|---|---|
| 1088h | 115BEh | 9574h |
| 108Ah | 115BAh | 9577h |
| 108Ch | 11543h | 956Bh |

Für 108Ch taucht zusätzlich eine Bytefolge bei E28Bh auf, die in der linearen Disassemblierung als speicherbezogene Instruktion erscheint. Der Bereich gehört jedoch zu einer Tabelle bzw. Datenzone und ist kein bestätigter Codezugriff. Er wird deshalb nicht als echter Leser gewertet.

Im untersuchten Ladebereich wurden somit für jedes der drei Felder genau eine eindeutige Schreibstelle und eine eindeutige Code-Lesestelle gefunden.

## 3. Ergebnisfelder 1088h und 108Ah

Die Routine 1159Fh wartet auf das Ereignisflag 0FFEh. Während es noch null ist, führt sie INT 28h aus und erhöht den 32-Bit-Zähler aus 0FE2h/0FE4h.

Nach Ende der Wartephase folgt:

    115B2  mov ax,ds:0FE2h
    115B5  mov cx,001Eh
    115B8  mul cx
    115BA  mov word ptr ds:108Ah,dx
    115BE  mov ds:1088h,ax

Die Multiplikation verwendet ausdrücklich nur das niedrige WORD 0FE2h. Das Produkt ist ein 32-Bit-Ergebnis in DX:AX. Das hohe Zählerwort 0FE4h wird an dieser Stelle nicht in die Multiplikation einbezogen.

Wichtig: Die gemeinsame Zählerführung 0FE2h/0FE4h ist zuvor belegt; diese konkrete Ausgabeformel nutzt aber nur 0FE2h. Daraus darf nicht abgeleitet werden, dass 1088h:108Ah in allen denkbaren Fällen ein mathematisch vollständiges Produkt des gesamten 32-Bit-Zählers enthält.

## 4. Ergebnisfeld 108Ch

Die zweite Routine (11511h) wartet ebenfalls auf 0FFEh und erhöht 0FE2h/0FE4h gemeinsam. Anschließend:

    11522  xor dx,dx
    11524  mov ax,dx
    11526  xchg word ptr ds:0FE4h,dx
    1152A  xchg word ptr ds:0FE2h,ax
    1152E  mov cx,4
    11531  shl ax,1
    11533  rcl dx,1
    11535  loop 11531
    11537  mov cx,0B01h
    1153A  div cx
    1153C  cmp dx,0580h
    11540  jbe 11543
    11542  inc ax
    11543  mov ds:108Ch,ax

Die Routine liest beide WORDs und verschiebt das 32-Bit-Paar vier Bits nach links. Anschließend dividiert sie durch 0B01h (dezimal 2817). Wenn der Rest größer als 0580h (dezimal 1408) ist, wird das Ergebnis aufgerundet.

Mathematisch entspricht das näherungsweise:

    Ergebnis = round((Zähler_32bit × 16) / 2817)

Die genaue beabsichtigte Einheit dieses Wertes ist noch nicht bestimmt. Der Code belegt die Rechenformel, nicht ihre semantische Benennung.

## 5. Leseroutinen: Weitergabe über FAR-Aufrufe

Die Lesezugriffe liegen in zwei kleinen FAR-Routinen:

    9567  push ds
    9568  call 961Ah
    956B  mov ax,ds:108Ch
    956E  pop ds
    956F  retf

und:

    9570  push ds
    9571  call 961Ah
    9574  mov ax,ds:1088h
    9577  mov bx,ds:108Ah
    957B  mov cx,ds:0E56h
    957F  sub cx,15F0h
    9583  shr cx,1
    9585  shr cx,1
    9587  shr cx,1
    9589  shr cx,1
    958B  pop ds
    958C  retf

Beide Routinen rufen 961Ah auf, sichern und restaurieren DS und enden mit RETF. Die erste gibt den WORD-Wert 108Ch in AX zurück. Die zweite gibt 1088h:108Ah in AX:BX zurück und berechnet zusätzlich einen Wert in CX aus dem Feld 0E56h.

Die Hilfsroutine 961Ah lautet:

    961A  mov ds,word ptr cs:[9618h]
    961F  ret

Die Bytes an 9618h/9619h bilden den konstanten WORD-Wert 0E34h. Damit wird DS für den Zugriff auf das Kernel-Datensegment gesetzt.

**Schlussfolgerung:** Die Felder werden über FAR-Routinen gezielt nach außen lesbar gemacht. Die Routine bei 9567h liefert 108Ch in AX; die Routine bei 9570h liefert 1088h/108Ah in AX:BX sowie einen zusätzlichen CX-Wert.

## 6. Interpretation und Grenzen

Gesichert:
- 1088h/108Ah bilden ein zusammengehöriges 32-Bit-Ergebnis einer WORD-Multiplikation.
- 108Ch ist das Ergebnis einer separaten Berechnung aus dem 32-Bit-Zähler 0FE2h/0FE4h.
- Jedes Feld hat im untersuchten Kernel genau eine bestätigte Schreibstelle und eine bestätigte Code-Lesestelle.
- Die Lesezugriffe sind in FAR-Routinen gekapselt, die DS auf 0E34h setzen.

Nicht gesichert:
- Die semantischen Namen der beiden Messwerte.
- Ihre Einheiten oder Umrechnungsfaktoren in allgemein verständliche Zeitmaße.
- Welche externen Kernelmodule oder Anwendungen die FAR-Routinen aufrufen. Dazu muss die Export-/Aufrufkette weiter verfolgt werden.

Die lineare Disassemblierung enthält Datenbereiche. Deshalb wurden Treffer, die nur aufgrund zufälliger Bytefolgen in Tabellen entstehen, nicht als Codezugriffe gezählt.

## 7. Nächster Schritt

Als nächstes sollte der Export-/Aufrufkontext der FAR-Routinen 9567h und 9570h untersucht werden. Die davor liegende Sprung-/Exporttabelle und Relokationen können zeigen, unter welchen Kernel-Einstiegsnummern diese Leser erreichbar sind. Danach lässt sich eventuell auch die Bedeutung der zurückgegebenen Messwerte enger bestimmen.

Es wurden keine Originaldateien verändert.
