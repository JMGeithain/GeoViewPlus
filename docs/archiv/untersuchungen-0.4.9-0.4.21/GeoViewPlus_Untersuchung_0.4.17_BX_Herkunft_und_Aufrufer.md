# GeoView Plus – Untersuchung 0.4.17
## Herkunft von BX und vier Aufrufpfade des Trampolins 257Eh

**Geltungsbereich:** ausschließlich PC/GEOS 1.x / deutsche GeoWorks-1.2-Kerneldateien. Dateien: KERNEL.EXE und KERNEL.OLD. Statische Analyse der MZ-Ladebilder; Headerlänge jeweils 0x600 Bytes. Originaldateien unverändert; keine Laufzeittests.

## 1. Aufruferzahl bytegenau bestätigt

Suche nach Near-CALL-Instruktionen E8 disp16 mit Ziel 257Eh ergibt in KERNEL.EXE exakt vier Treffer:
- 2563h → 257Eh
- 25AEh → 257Eh
- 423Bh → 257Eh
- 425Ah → 257Eh

In KERNEL.OLD liegen die entsprechenden Aufrufe bei 256Dh, 25B8h, 4245h und 4264h; Ziel ist dort 2588h. Damit ist die Viererzahl aus 0.4.16 bestätigt. Der vierte Aufruf ist 25AEh.

## 2. Aufrufpfad 2563h: Objekt aus einer Liste

254F jcxz 255Ch; 2551 pop bx; 2552 cmp [bx+8],bx; 2555 jne 255Ah; 2557 call 255Eh.
255E call 29D2h; 2561 push bx; 2562 push cs; 2563 call 257Eh; 2566 mov di,0002h; 2569 call far [si]; 256B pop bx; 256C call 961Ah; 256F dec word ptr ds:[0605h]; 2573 mov ds,[bx]; 2575 and byte ptr ds:[0003h],0DFh; 257A call 29E4h; 257D ret.

BX wird bei 2551h aus dem Stack geholt und vor dem Trampolin nochmals gesichert. 257Eh erhält diesen Wert. Danach folgt ein indirekter Far-Aufruf über [SI] mit DI=2. Anschließend wird BX wiederhergestellt, DS über 961Ah auf 0E34h gesetzt und [BX] als Segmentwert nach DS geladen. Die Struktur, die BX ursprünglich auf den Stack gelegt hat, muss vor 254Fh weiter zurückverfolgt werden.

## 3. Aufrufpfad 25AEh: AX-abhängiger Pfad

25A1 push ds; 25A2 call 961Ah; 25A5 cmp ax,0006h; 25A8 jne 25D7h; 25AA call 29D2h; 25AD push cs; 25AE call 257Eh; 25B1 mov ax,[si]; 25B3 mov si,[si+2]; 25B6 call 961Ah; 25B9 xchg ax,ds:[0746h]; 25BD mov ds:[0748h],si; 25D4 call 29E4h.

Der Pfad wird nur bei AX=6 fortgesetzt. Vor 257Eh ist kein neuer BX-Wert sichtbar; BX stammt daher aus dem Eintrittszustand bzw. vorausgehenden Aufruferkontext. Nach dem Trampolin werden zwei Wörter am zurückgegebenen DS:SI gelesen. Danach setzt 961Ah DS wieder auf 0E34h; AX und SI werden in DS:[0746h] und DS:[0748h] gespeichert. Die Bedeutung von AX=6 und der globalen Wörter ist nicht belegt.

## 4. Aufrufpfad 423Bh: BX-Parameter oder Fallback

422A push cx; 422B push bx; 422C push si; 422D push di; 422E push ds; 422F call 961Ah; 4232 or bx,bx; 4234 jne 423Ah; 4236 mov bx,ds:[0609h]; 423A push cs; 423B call 257Eh; 423E mov bx,di; 4240 mov di,000Ah; 4243 call far [si].

Der Eintrittswert von BX wird gesichert. 961Ah setzt DS=0E34h, ohne BX zu verändern. Ist BX ungleich null, wird er direkt an 257Eh weitergegeben; andernfalls wird BX aus DS:[0609h] geladen. Danach wird BX durch DI ersetzt, DI=0Ah gesetzt und die Methode über [SI] aufgerufen. DS:[0609h] ist damit in diesem Pfad ein Fallback für BX; seine symbolische Bedeutung bleibt offen.

## 5. Aufrufpfad 425Ah: zweiter Dispatcher-Eintritt

424B call 29D2h; 424E call 961Ah; 4251 or bx,bx; 4253 jne 4259h; 4255 mov bx,ds:[0609h]; 4259 push cs; 425A call 257Eh; 425D mov di,000Ch; 4260 call far [si]; 4262 call 29E4h; 4265 retf.

Auch hier wird BX nur dann aus DS:[0609h] ersetzt, wenn es null ist. Nach 257Eh wird DI=0Ch gesetzt und die Methode über [SI] aufgerufen. Die Dispatch-Argumente der benachbarten Pfade unterscheiden sich: 0Ah bei 4243h, 0Ch bei 4260h.

## 6. Gemeinsame, belegte Eigenschaften

1. Das Trampolin wird stets mit einem BX-Wert aufgerufen.
2. 257Eh setzt zunächst DS=0E34h über 961Ah.
3. Danach wird aus DS:[BX] ein Segmentwert geladen.
4. Aus diesem Segment werden die Wörter bei Offset 28h und 2Ah gelesen; daraus entsteht die zurückgegebene Adresse DS:SI.
5. In drei Pfaden folgt ein indirekter Far-Aufruf über [SI] (2569h, 4243h, 4260h).
6. Im Pfad 25AEh werden stattdessen zunächst zwei Wörter aus DS:SI gelesen und global gespeichert.
7. BX ist der Selektor/Offset für den Datensatz, den das Trampolin auflöst. Ob der Datensatz ein Objekt, ein Treiberdeskriptor oder eine andere Kernelstruktur ist, ist nicht nachgewiesen.

## 7. Weitere Verwendung von Feld 28h: Routine 6F96h

41C3 push bx; 41C4 mov bx,es:[0028h]; 41C9 call 6F96h; 41CC mov es:[002Ah],ax; 41D0 pop bx.

6F96h ruft 70DCh auf, sichert DS, setzt DS=0E34h, prüft BX auf 16-Byte-Ausrichtung und einen zulässigen Bereich, liest [BX], erhöht bei nicht-null den Bytewert [BX+0Bh], stellt DS wieder her und kehrt zurück. Dies zeigt eine weitere Verwendung eines Wertes aus ES:[28h] als BX-Parameter. Danach wird AX in ES:[2Ah] gespeichert. Nicht bewiesen ist, dass dies exakt dieselbe Struktur ist, die 257Eh auflöst; Segment und Aufrufkontext unterscheiden sich.

## 8. Nächste Untersuchung 0.4.18

- Eintrittsstellen und Aufrufer der Routinen 255Eh, 422Ah und 424Bh rückwärts verfolgen.
- Die Schleife 2492h–255Dh vollständig rekonstruieren, um die Herkunft der BX-Werte für 255Eh zu bestimmen.
- DS:[0609h] über alle Schreibstellen verfolgen und mit KERNEL.OLD vergleichen.
- Felder +28h/+2Ah anhand ihrer Erzeuger und Schreiber untersuchen.
- Indirekte Methodenaufrufe mit DI=2, 0Ah und 0Ch vergleichen.

**Status:** Vier Aufrufstellen bytegenau bestätigt; BX-Herkunft in drei Pfaden teilweise eingegrenzt. Strukturtyp und Methodennamen weiterhin offen. Keine Laufzeittests; keine Änderungen an Originaldateien oder am GeoView-Plus-Zeichensatzdecoder.