# Untersuchung 182 – INT-8-Einsprungpunkt und CS-relative Adressierung (korrigierte Fassung)

**Projekt:** GeoViewPlus  
**Untersuchungsgegenstand:** KERNEL.EXE aus Basebox-SVGA-Ensemble12  
**Methode:** schreibgeschützte statische Analyse, 8086-Disassemblierung und MZ-Relokationsprüfung  
**Abgrenzung:** GeoWorks / PC/GEOS 1.x.

## 1. Ausgangsfrage

Die Routine 11458h schreibt den neuen INT-8-Vektor mit Offset 1B72h und dem aktuellen CS-Segment. Die frühere Prüfung hatte den Offset 1B72h fälschlich als absoluten linearen Dateioffset betrachtet. Bei segmentiertem Code muss jedoch die Basis des tatsächlichen CS-Segments berücksichtigt werden.

## 2. MZ-Programmeinstieg

Der MZ-Header nennt:
- Initiales CS:IP = 0000h:02B1h
- Initiales SS:SP = 0E34h:15F0h
- Headergröße = 96 Paragraphen = 0600h Bytes.

Am Ladeoffset 02B1h steht:

    0002B1  call far 0F93h:0000h

Die vier Bytes lauten 9A 00 00 93 0F. Die Segmentadresse 0F93h ist zusätzlich durch einen MZ-Relokationseintrag am Ladeoffset 02B4h erfasst. Damit ist belegt, dass der Programmeinstieg aus dem anfänglichen MZ-Segment 0000h in das Kernel-Code-Segment 0F93h wechselt.

## 3. CS-relative Lage der Routine 11458h

Die in den vorangegangenen Untersuchungen als linearer Ladeoffset 11458h bezeichnete Routine liegt innerhalb des Segments 0F93h. Die Umrechnung lautet:

    Segmentbasis 0F93h × 10h = 0F930h
    Ladeoffset 11458h − 0F930h = 1B28h

Damit liegt die Routine 11458h tatsächlich bei 0F93h:1B28h.

Der Vektorschreibzugriff lautet:

    11470  mov word ptr es:[0020h],1B72h
    11477  mov word ptr es:[0022h],cs

Da CS in dieser Routine 0F93h ist, installiert sie den Vektor 0F93h:1B72h.

## 4. Auflösung des INT-8-Ziels

Die lineare Ladeadresse des Vektorziels ergibt sich aus:

    0F93h × 10h + 1B72h
    = 0F930h + 1B72h
    = 114A2h

Am Ladeoffset 114A2h beginnt exakt die zuvor untersuchte Routine:

    114A2  push ax
    114A3  push ds
    114A4  mov al,60h
    114A6  out 20h,al
    114A8  mov ax,0E34h
    114AB  mov ds,ax
    114AD  dec byte ptr ds:1097h
    114B1  jne 114B9
    114B3  mov word ptr ds:0FFEh,1
    114B9  pop ds
    114BA  pop ax
    114BB  iret

Damit ist die Zuordnung eindeutig: 0F93h:1B72h zeigt auf den Code bei Ladeoffset 114A2h. Die Routine 114A2h ist tatsächlich der von 11458h installierte INT-8-Handler.

## 5. Korrektur der vorherigen Interpretation

Die frühere lineare Disassemblierung des Dateioffsets 1B72h hatte Code aus einem anderen Bereich gezeigt. Das war für die Vektorauflösung die falsche Basisannahme. Maßgeblich ist die CS-Segmentbasis 0F930h.

Die zuvor offene Frage ist damit geschlossen. Die in Untersuchung 181 beschriebene Kette ist nun vollständig belegt:
1. 11458h sichert den alten INT-8-Vektor.
2. 11458h installiert 0F93h:1B72h.
3. Dieses Ziel wird auf Ladeoffset 114A2h abgebildet.
4. Der Handler zählt 1097h herunter.
5. Bei Erreichen von null setzt er 0FFEh auf 1.
6. Die Warte-/Folgeroutinen prüfen 0FFEh.

## 6. Zusatzbefund: Laufzeit-Ausrichtung der Schleife

Die Hilfsroutine 114BCh kopiert 17 Bytes ab CS:1BE1h an eine um den Rest von 1BE1h mod 16 nach unten verschobene Adresse und füllt den ursprünglichen Bereich mit NOP-Bytes (90h). Die Quelladresse CS:1BE1h entspricht bei Segmentbasis 0F930h dem Ladeoffset 11511h.

Die kopierten 17 Bytes sind genau die Schleifenfolge ab 11511h:
- Vergleich des Ereignisflags,
- bedingter Sprung,
- Inkrement des niedrigen Zählerworts,
- Überlaufbehandlung über das hohe Zählerwort,
- Rücksprung.

Damit wird diese Schleife zur Laufzeit auf eine 16-Byte-Grenze ausgerichtet. Die zweite Routine ab 11547h führt eine vergleichbare Ausrichtung für die Schleife ab Ladeoffset 1159Fh durch; dort werden 19 Bytes ab CS:1C6Fh kopiert und die ursprünglichen Bytes mit NOPs gefüllt.

Dieser Befund erklärt die zuvor irritierenden Kopier-/NOP-Sequenzen. Es handelt sich um dynamische Codeverschiebung zur Ausrichtung der engen Schleifen, nicht um die Herstellung des INT-8-Handlers.

## 7. Ergebnis

**Gesichert:** Das Segment 0F93h ist das aktive Kernel-Code-Segment für diese Routinen. Die Vektoradresse 0F93h:1B72h entspricht exakt dem Ladeoffset 114A2h. Der dortige IRET-Code ist der installierte INT-8-Handler.

**Ebenfalls gesichert:** Die Hilfsroutinen 114BCh und 11547h richten zwei Schleifen durch Kopieren und NOP-Füllen auf 16-Byte-Grenzen aus.

Die Analyse ist statisch. Es wurden keine Originaldateien verändert und keine Laufzeittests durchgeführt.

## 8. Nächster Schritt

Als nächstes sollten die Zielwerte 1088h, 108Ah und 108Ch weiterverfolgt werden. Ihre Leser und Verwendungen können die Bedeutung der gemessenen Warte-/Schleifenwerte eingrenzen.
