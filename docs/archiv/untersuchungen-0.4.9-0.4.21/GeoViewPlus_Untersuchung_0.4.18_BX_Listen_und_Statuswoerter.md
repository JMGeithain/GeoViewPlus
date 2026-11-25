# GeoView Plus – Untersuchung 0.4.18
## Rückverfolgung der BX-Quelle, Objektlisten und Kernel-Statuswörter

**Geltungsbereich:** ausschließlich PC/GEOS 1.x / deutsche GeoWorks-1.2-Kerneldateien.
**Dateien:** KERNEL.EXE (72.736 Bytes) und KERNEL.OLD (72.688 Bytes).
**Methode:** statische Disassemblierung des MZ-Ladebildes; MZ-Header 0x600 Bytes, Dateioffset = 0x600 + Ladebildoffset. Originaldateien unverändert; keine Laufzeittests.

## 1. Korrektur der Bereichsaufteilung

Der Bereich 2492h–255Dh enthält mehrere getrennte Routinen. Die Routine ab 248Ah setzt AX=SI und ruft 9D7Dh auf; ab 248Fh beginnt ein Scan mit BX=15F0h, der in 10h-Schritten bis DS:[0E56h] läuft. Daneben liegen ab 24F4h und 252Ah zwei Routinen, die eine verkettete Segment-/Objektliste über DS:[0607h] und ES:[0044h] durchlaufen.

## 2. Scan ab 248Ah / 248Fh

- 248Ah: MOV AX,SI; CALL 9D7Dh.
- 248Fh: MOV BX,15F0h.
- 2492h: BX wird gesichert; geprüft werden SS:[0000h], SI und [BX+8].
- Byte [BX+1] steuert Sonderpfade für FDh, F6h, F4h, FAh sowie Werte unter F0h.
- Am Ende wird BX um 10h erhöht und mit DS:[0E56h] verglichen; bei kleinerem BX beginnt der Scan erneut.

Gesichert ist ein 16-Byte-Schritt über einen Bereich ab BX=15F0h. Bedeutung der Einträge und Sonderwerte offen. Dieser Scan ist nicht automatisch die Herkunft von BX bei 423Bh/425Ah.

## 3. Liste ab 24F4h über DS:[0607h]

Die Routine ab 24F4h:
1. sichert ES und setzt DS=0E34h über 961Ah,
2. lädt AX aus DS:[0607h],
3. setzt ES=AX,
4. prüft ES:[0003h] auf Bit 08h,
5. legt bei erfüllter Bedingung ES:[0000h] und AX auf dem Stack ab,
6. folgt der Verkettung über ES:[0044h],
7. verarbeitet die Einträge durch Vergleich [BX+8] mit BX und ruft bei Übereinstimmung 2355h auf.

DS:[0607h] dient als Einstieg in eine verkettete Segmentliste; ES:[0044h] enthält den nächsten Knotenwert. Der Typ der Liste bleibt offen.

## 4. Liste ab 252Ah und Aufruf 255Eh

Die Routine ab 252Ah läuft ebenfalls ab DS:[0607h] über ES:[0044h]. Sie prüft ES:[0003h] mit Maske 28h und zusätzlich das Vorzeichenflag. Bei erfüllter Bedingung erhöht sie CX und legt ES:[0000h] auf den Stack.

Am Ende holt sie einen gespeicherten Knotenwert nach BX, prüft [BX+8] gegen BX und ruft bei Gleichheit 255Eh auf. Danach wird die Schleife mit LOOP fortgesetzt.

Damit stammt BX beim Aufruf 255Eh aus dem zuvor auf dem Stack abgelegten Wort ES:[0000h] eines Listenknotens. Das ist ein direkter Herkunftsnachweis für den Pfad 2563h.

## 5. BX bei 423Bh und 425Ah

Beide Aufrufer setzen DS über 961Ah auf 0E34h, prüfen BX und laden nur bei BX=0 den Wert aus DS:[0609h]. DS:[0609h] ist daher in diesen Pfaden ein Fallback für BX; der Wert wird hier gelesen, nicht erzeugt.

## 6. Status-/Parameterabfrage 258Ch

```asm
258C  push ds
258D  call 961Ah
2590  mov ax,ds:[060Fh]
2593  mov bx,ds:[0609h]
2597  mov cx,ds:[0611h]
259B  mov dx,ds:[0613h]
259F  pop ds
25A0  retf
```

Die Routine liefert vier Kernel-Datenwörter in Registern zurück: AX=DS:[060Fh], BX=DS:[0609h], CX=DS:[0611h], DX=DS:[0613h]. Damit ist DS:[0609h] ein bewusst herausgegebenes Kernel-Status-/Parameterwort; seine semantische Rolle ist nicht identifiziert.

In KERNEL.OLD liegt die entsprechende Routine ab 2596h und liest AX=DS:[0605h], BX=DS:[05FFh], CX=DS:[0607h], DX=DS:[0609h]. Die strukturelle Entsprechung ist belegt; Werte und Bedeutungen dürfen nicht gleichgesetzt werden.

## 7. Schreibstellen von DS:[0609h]

Klare Codezugriffe auf 0609h im disassemblierten KERNEL.EXE-Ladebild:
- 2593h: Lesen in BX durch die Statusabfrage.
- 4236h: Lesen als BX-Fallback.
- 4255h: Lesen als BX-Fallback.

Ein zusätzlicher Treffer bei E99Bh liegt in einem Bereich ohne gesicherte Codegrenze und wird nicht als Instruktion klassifiziert. In den klaren Codezugriffen wurde keine Schreibstelle gefunden. Herkunft und Initialisierung des Wertes bleiben offen.

## 8. Nächste Schritte

- Alle Aufrufer der Statusabfrage 258Ch und Verwendungen ihrer Rückgaberegister verfolgen.
- Herkunft und Schreibstellen von DS:[0607h], DS:[060Fh], DS:[0611h] und DS:[0613h] untersuchen.
- Routine 9D7Dh und den 16-Byte-Scan ab 248Fh separat analysieren.
- Entsprechende Bereiche in KERNEL.OLD mit den verschobenen Feldern abgleichen.

**Status:** BX-Herkunft für Pfad 2563h direkt aus einer verketteten Liste nachgewiesen; DS:[0609h] als bewusst ausgegebenes Kernel-Status-/Parameterwort identifiziert. Semantik und Schreibstelle bleiben offen. Keine Laufzeittests; keine Änderungen an Originaldateien oder am Zeichensatzdecoder.