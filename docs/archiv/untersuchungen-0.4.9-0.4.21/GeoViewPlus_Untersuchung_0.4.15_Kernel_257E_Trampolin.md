# GeoView Plus – Untersuchung 0.4.15
## Routine 0000:257Eh: Registerübergabe und Trampolinstruktur

**Gegenstand:** ausschließlich PC/GEOS 1.x; deutsche GeoWorks-1.2-KERNEL.EXE.
**Quelle:** KERNEL.EXE, MZ-Headerlänge 0x600 Bytes. Statische 16-Bit-Disassemblierung mit objdump (i386, addr16, data16). Originaldateien unverändert.

## 1. Ergebnis und Korrektur

Die Routine bei Ladebildoffset 257Eh ist kein unmittelbar erkennbarer DOS-Dateiöffner, sondern ein kurzes Register-/Segment-Trampolin. Ihre symbolische Funktion ist nicht belegt.

257E  E8 99 70       call 9C1Ah
2581  8E 1F          mov ds,[bx]
2583  8B 36 28 00    mov si,[0028h]
2587  8E 1E 2A 00    mov ds,[002Ah]
258B  CB             retf

Nach dem Aufruf 9C1Ah wird BX als Speicherindex für einen Segmentwert verwendet. Danach wird SI aus DS:[0028h] geladen und DS aus DS:[002Ah]. Es folgt ein Far-Return. Die Bedeutung der Datenstruktur bleibt offen.

## 2. Aufrufkontext bei 25A1h

25A1  1E             push ds
25A2  E8 75 70       call 9C1Ah
25A5  3D 06 00       cmp ax,0006h
25A8  75 2D          jne 25D7h
25AA  E8 25 04       call 2FD2h
25AD  0E             push cs
25AE  E8 CD FF       call 257Eh
25B1  8B 04          mov ax,[si]
25B3  8B 74 02       mov si,[si+2]
25B6  E8 61 70       call 9C1Ah
25B9  87 06 46 07    xchg ax,[0746h]
25BD  89 36 48 07    mov [0748h],si
25C1  0B C0          or ax,ax
25C3  75 0F          jne 25D4h
25C5  BE 40 01       mov si,0140h
25C8  33 C9          xor cx,cx
25CA  E8 14 00       call 25E1h
25CD  C5 36 BA 00    lds si,[00BAh]
25D1  E8 0D 00       call 25E1h
25D4  E8 0D 04       call 29E4h
25D7  96             xchg ax,si
25D8  8B B4 57 06    mov si,[si+0657h]
25DC  89 1C          mov [si],bx
25DE  96             xchg ax,si
25DF  1F             pop ds
25E0  CB             retf

Belegte Fakten:
- Der Pfad wird nur fortgesetzt, wenn der Aufruf 9C1Ah AX=0006h liefert.
- Danach folgen 2FD2h und das Trampolin 257Eh.
- Direkt nach 257Eh werden AX=[SI] und SI=[SI+2] ausgeführt.
- Ein weiterer Aufruf 9C1Ah folgt; danach werden AX und SI in die globalen Speicherstellen 0746h und 0748h übernommen.
- Je nach AX folgen Aufrufe 25E1h und 29E4h.

Die Bedeutung von AX=6, 0746h/0748h und den Unterroutinen ist noch offen.

## 3. Stack-Hilfsroutine 2FD2h

2FD2  06             push es
2FD3  1E             push ds
2FD4  55             push bp
2FD5  57             push di
2FD6  56             push si
2FD7  52             push dx
2FD8  51             push cx
2FD9  53             push bx
2FDA  50             push ax
2FDB  8B EC          mov bp,sp
2FDD  FF 76 12       push [bp+12h]
2FE0  8B 6E 0C       mov bp,[bp+0Ch]
2FE3  C3             ret

2FE4h stellt den gesicherten Zustand wieder her. Das ist ein Stack-/Register-Hilfsmechanismus; eine weitergehende API-Bezeichnung ist nicht belegt.

## 4. Beziehung zur DOS-Dateinamen-Tabelle

Untersuchung 0.4.14 hat DOS2.GEO, DOS3.GEO, DOS4.GEO, DOS5.GEO und DRDOS.GEO sowie die Auswahl über DS:[05ABh] und DS:[05B1h] dokumentiert.

Der jetzt untersuchte Code zeigt einen Kontrollfluss über AX=6 und 257Eh, gefolgt von zwei Wortzugriffen über [SI] und [SI+2]. **Nicht bewiesen** ist, dass 257Eh selbst den DOS-Dateinamen öffnet oder dass diese beiden Wörter unmittelbar aus dem DOS-Dateinamen-Tabelleneintrag stammen. Das muss über 9C1Ah und den Registerzustand vor dem Aufruf geklärt werden.

## 5. Nächste Schritte

1. Routine 9C1Ah vollständig rekonstruieren, einschließlich ihres Sprungs zu 8B1Bh.
2. Aufrufkonvention von 2FD2h anhand sämtlicher Aufrufer bestimmen.
3. BX, SI, DS und ES vor/nach 257Eh über alle Pfade verfolgen.
4. Entsprechenden Bereich in KERNEL.OLD abgleichen.

**Status:** Instruktionswirkungen und Aufrufkontext statisch dokumentiert. Symbolische Funktionsnamen bleiben offen. Keine Laufzeittests und keine Änderungen an GeoWorks-Dateien oder GeoView-Plus-Zeichensatzcode.

---

## Korrekturhinweis – Untersuchung 0.4.16

Die Disassemblierung in diesem Bericht ordnet den Aufruf bei 257Eh falsch zu. Die Bytes `E8 99 70` rufen **961Ah**, nicht 9C1Ah, auf. Außerdem ist 2FD2h nicht die hier beschriebene Stack-Hilfsroutine; der relevante Sicherungsaufruf ist 29D2h, die Wiederherstellung erfolgt über 29E4h. Maßgeblich ist der korrigierende Bericht [Untersuchung 0.4.16](GeoViewPlus_Untersuchung_0.4.16_50_Pruefschritte.md). Die betroffenen Aussagen des ursprünglichen Berichts sind überholt.
