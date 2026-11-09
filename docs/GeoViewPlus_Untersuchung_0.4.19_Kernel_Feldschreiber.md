# GeoView Plus – Untersuchung 0.4.19
## Schreibstellen der Kernel-Felder 0607h, 0609h, 060Fh, 0611h und 0613h

**Geltungsbereich:** ausschließlich PC/GEOS 1.x / deutsche GeoWorks-1.2-Kerneldateien.  
**Quellen:** KERNEL.EXE (72.736 Bytes) und KERNEL.OLD (72.688 Bytes).  
**Methode:** statische Disassemblierung des MZ-Ladebildes mit Headerlänge 0x600 Bytes. Adressen sind Ladebildoffsets. Originaldateien unverändert; keine Laufzeittests.

## 1. Ergebnisübersicht

| Feld in KERNEL.EXE | Nachgewiesene Zugriffe | Aussage |
|---|---|---|
| DS:[0607h] | Lesen bei 24F8h, 252Eh; Schreiben bei 242Eh | Kopf einer verketteten Segmentliste |
| DS:[0609h] | Lesen bei 2593h, 4236h, 4255h | Keine sichere Schreibstelle in den geprüften Codepfaden |
| DS:[060Fh] | Lesen bei 2590h; Schreiben bei FFFAh | Ergebniswert einer Initialisierungs-/Prüfroutine |
| DS:[0611h] | Lesen bei 2597h; keine sichere Schreibstelle gefunden | Herkunft offen |
| DS:[0613h] | Lesen bei 259Bh; Schreiben bei 10BD5h | Übergabewert im DOS-Treiber-Setup-Pfad |

## 2. DS:[0607h]: Listen-Kopf

Bei 241Eh–2445h wird ein Segment aus ES aus der verketteten Liste entfernt. Der Code liest den Kopf DS:[0607h] bei 2426h. Wenn der Kopf dem zu entfernenden Segment entspricht, wird DS:[0607h] mit ES:[0044h] (dem Nachfolger) überschrieben (242Eh). Andernfalls wird die Kette über ES:[0044h] durchlaufen und der Vorgängerlink aktualisiert (243Fh).

Die Routinen 24F4h und 252Ah lesen denselben Kopf und folgen den Nachfolgern über ES:[0044h]. Damit ist die Rolle von DS:[0607h] als Listen-Kopf direkt durch Lese- und Schreibzugriffe belegt.

## 3. DS:[0609h]: kein gefundener Code-Schreiber

Die sicheren Code-Lesezugriffe sind 2593h (Ausgabe in BX), 4236h und 4255h (Fallback-Lesen in BX vor dem Trampolin 257Eh).

Ein vermeintlicher Treffer bei E99Bh ist kein belastbarer Codezugriff: Der Bereich liegt im MZ-Ladebild zwischen Daten-/Tabelleninhalten; die Disassemblierung dort ist nicht durch eine bestätigte Codegrenze abgesichert. Das Byte-Muster 11 06 09 06 kann daher nicht als Schreibinstruktion gewertet werden.

**Schluss:** Im untersuchten statischen Code ist keine sichere Schreibstelle für DS:[0609h] nachgewiesen. Initialisierung, indirekte Schreibzugriffe, Segmentalias oder dynamische Übergabe sind damit nicht ausgeschlossen.

## 4. DS:[060Fh]: Ergebnis aus Routine FFD0h–FFFFh

Die Routine im Bereich FFD0h prüft mehrere Bedingungen und springt bei Fehlerpfaden zu 0000:0399. Im Abschlusszweig wird bei FFFAh BX nach DS:[060Fh] geschrieben. Unmittelbar danach folgt ein Aufruf bei 101CCh und die Rückkehr.

Der direkte Schreibzugriff ist gesichert; welche Ressource BX repräsentiert, bleibt offen.

## 5. DS:[0611h]: bislang nur Auslesung

Die Statusabfrage 258Ch liest DS:[0611h] nach CX. In der geprüften Disassemblierung wurde keine sichere absolute Schreibinstruktion auf dieses Feld gefunden. Der aktuelle Befund ist daher nur eine Registerausgabe.

## 6. DS:[0613h]: DOS-Treiber-Setup

Im Setup-Pfad bei 10BC0h–10C06h wird zunächst ES aus AX gesetzt. Bei 10BD5h wird BX nach DS:[0613h] geschrieben. Danach wird DS gesichert und 0000:257Eh aufgerufen; aus dem zurückgegebenen DS:SI werden zwei Wörter gelesen und als Far-Pointer bei DS:[05B8h]/DS:[05BAh] abgelegt.

Damit ist DS:[0613h ein Wert, der im DOS-Treiber-Setup-Pfad vor dem Trampolinaufruf gespeichert wird. Seine semantische Bedeutung ist nicht belegt; insbesondere darf daraus nicht geschlossen werden, dass es ein Treiberindex oder eine Dateinummer ist.

## 7. Vergleich mit KERNEL.OLD

KERNEL.OLD enthält eine strukturell entsprechende Statusabfrage bei 2596h, aber mit verschobenen Feldern: AX=DS:[0605h], BX=DS:[05FFh], CX=DS:[0607h], DX=DS:[0609h].

Diese Verschiebung bestätigt eine verwandte Datenstruktur, aber keine identische Feldsemantik. Die Schreibstellen müssen deshalb in KERNEL.OLD unabhängig rekonstruiert werden.

## 8. Nächste Schritte 0.4.20

1. Den Aufrufer der Routine FFD0h–FFFFh rückwärts verfolgen und BX-Herkunft bestimmen.
2. Den Initialisierungspfad von 10BD5h rekonstruieren.
3. Indirekte und segmentalias-basierte Schreibwege auf DS:[0609h] und DS:[0611h] prüfen.
4. Die entsprechenden Felder und Schreibstellen in KERNEL.OLD getrennt erfassen.
5. Erst danach die vier Statuswörter semantisch benennen.

**Status:** DS:[0607h] als Listen-Kopf und seine Schreibstelle nachgewiesen. DS:[060Fh] und DS:[0613h] besitzen je eine direkte Schreibstelle. Für DS:[0609h] und DS:[0611h] wurde bislang kein sicherer Code-Schreiber gefunden. Keine Laufzeittests; keine Änderungen an Originaldateien oder Zeichensatzdecoder.
