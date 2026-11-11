# Untersuchung 181 – Timer-Interrupt und Wartezeitmessung im GeoWorks-1.x-Kernel

**Projekt:** GeoViewPlus  
**Untersuchungsgegenstand:** KERNEL.EXE aus Basebox-SVGA-Ensemble12  
**Methode:** schreibgeschützte statische Analyse und 8086-Disassemblierung  
**Abgrenzung:** GeoWorks / PC/GEOS 1.x; keine Übertragung von PC/GEOS 2.x.

## 1. Ziel

Untersuchung 180 hatte zwei Fragen offen gelassen:
- Welche Funktion hat das Wortfeld 0FFEh?
- Warum werden 0FE2h und 0FE4h gemeinsam erhöht, ausgelesen und zurückgesetzt?

Die Kontrollflussanalyse der Routinen 1144Ch bis 115C9h liefert dazu einen zusammenhängenden Ablauf.

## 2. Installation eines temporären INT-8-Handlers

Die Routine ab 11458h liest zunächst den bisherigen Interruptvektor aus der Interrupttabelle:
- Vektoroffset aus 0000:0020h wird in DS:1084h gesichert.
- Vektorsegment aus 0000:0022h wird in DS:1086h gesichert.

Anschließend setzt sie den Vektor 0000:0020h auf Offset 1B72h und das aktuelle CS-Segment. Der Interruptvektor bei 0000:0020h gehört zu INT 8, dem BIOS-Timerinterrupt.

Nach dem folgenden Ablauf wird der Vektor wieder auf 9E5Bh:0000h gesetzt und die vorherigen Daten werden an anderer Stelle behandelt. Der alte Vektor wird in dieser Routine nicht direkt aus DS:1084h/1086h zurückgeschrieben; daher wird hier nur die beobachtete Vektorinstallation und -wiederherstellung dokumentiert, nicht eine weitergehende Deutung.

## 3. Interrupt-Handler bei 114A2h

Der Handler enthält:

```asm
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
```

Damit ist direkt belegt:
- Der Handler arbeitet mit dem Kernel-Datensegment 0E34h.
- Das Byte 1097h wird bei jedem Eintritt dekrementiert.
- Wenn das Byte null erreicht, wird das WORD-Feld 0FFEh auf 1 gesetzt.
- Der Handler beendet sich mit IRET.

**Schlussfolgerung:** 0FFEh fungiert in diesem Ablauf als durch den Timer-Interrupt gesetztes Ereignis-/Fertigflag. Das ist durch die Schreibstelle und die dazugehörige Warteschleife belegt.

## 4. Initialisierung und Warten

Die Routine ab 1144Ch ruft zunächst 115CAh auf, um Datum und Uhrzeit über DOS-INT-21h (AH=2Ah und AH=2Ch) in Kernel-Datenfeldern abzuspeichern. Danach ruft sie 11458h auf, installiert also den temporären INT-8-Handler. Anschließend setzt sie DS:10A2h auf 1.

Die Routine 11458h ruft 114BCh auf. Diese programmiert den PIT-Kanal 0 über die Ports 43h und 40h neu und setzt DS:1097h zunächst auf 4. Sie setzt 0FFEh auf 0 und wartet anschließend auf den Ablauf der Timerinterrupts. Der Handler reduziert 1097h bei jedem Interrupt; die Wartefolge prüft den Zählerstand und wartet danach auf das Ereignisflag 0FFEh.

Die zentrale Initialisierung ist:

```asm
114DD  mov bx,0FFEh
114E0  mov word ptr ds:0FFEh,0
114E6  cli
114E7  mov byte ptr ds:1097h,4
114EC  mov al,36h
114EE  out 43h,al
114F0  mov al,0AEh
114F2  out 40h,al
114F4  mov al,4Dh
114F6  out 40h,al
114F8  sti
```

Die konkrete PIT-Zeitdauer und die vollständige Hardwarewirkung sind hier nicht weiter nachgerechnet. Sicher ist die programmierte Folge von Steuer- und Zählerbytes sowie der zugehörige Interrupt-Zählmechanismus.

## 5. 0FE2h und 0FE4h: gemeinsamer Zähler während der Wartephase

Die Schleife ab 1159Fh prüft das WORD an der durch BX adressierten Stelle 0FFEh:

```asm
1159F  cmp word ptr [bx],0
115A2  jne 115B2
115A4  int 28h
115A6  inc word ptr ds:0FE2h
115AA  jne 1159F
115AC  inc word ptr ds:0FE4h
115B0  jmp 1159F
```

Solange 0FFEh null ist, führt der Kernel INT 28h aus und erhöht den Zähler 0FE2h. Bei Überlauf erhöht er 0FE4h. Die beiden WORD-Felder bilden damit in dieser Schleife gemeinsam einen 32-Bit-Zähler.

Nach Ende der Wartephase wird der niedrige WORD-Wert aus 0FE2h mit 30 multipliziert. Das 32-Bit-Ergebnis aus DX:AX wird in DS:108Ah und DS:1088h gespeichert. Anschließend werden beide Zähler gelöscht:

```asm
115B2  mov ax,ds:0FE2h
115B5  mov cx,30
115B8  mul cx
115BA  mov word ptr ds:108Ah,dx
115BE  mov ds:1088h,ax
115C1  xor ax,ax
115C3  mov ds:0FE4h,ax
115C6  mov ds:0FE2h,ax
115C9  ret
```

**Schlussfolgerung:** 0FE2h/0FE4h sind in dieser Routine ein gemeinsamer 32-Bit-Schleifenzähler. Die Multiplikation mit 30 und die Speicherung in 1088h/108Ah sind belegt. Die Bedeutung der resultierenden Einheit ist noch nicht sicher bestimmt.

## 6. Zweite Verwendung des Zählerpaars

Auch die Routine ab 11511h prüft das durch BX adressierte Flag und erhöht bei Null dieselben Felder 0FE2h/0FE4h. Danach übernimmt sie beide WORD-Werte mit XCHG in DX:AX, verschiebt das Registerpaar vier Bits nach links und dividiert durch 0B01h. Das Ergebnis wird in DS:108Ch gespeichert.

Damit ist die gemeinsame Behandlung des Feldpaares unabhängig von der zuvor beschriebenen Schleife erneut belegt. Die konkrete Maßeinheit der Berechnung bleibt ohne weitere Analyse offen.

## 7. Ergebnis

| Feld | jetzt belegte Funktion | Beweisstärke |
|---|---|---|
| 0FFEh | Timer-Handler setzt bei Ablauf auf 1; Warteschleife prüft auf ungleich null | direkt belegt |
| 1097h | Bytezähler, der im INT-8-Handler heruntergezählt wird | direkt belegt |
| 0FE2h/0FE4h | gemeinsamer 32-Bit-Zähler für Schleifendurchläufe während der Wartephase | direkt belegt |
| 1088h/108Ah | Ziel der Multiplikation von 0FE2h mit 30 | direkt belegt |
| 108Ch | Ziel einer zweiten Berechnung aus dem 0FE2h/0FE4h-Paar | direkt belegt |
| 0FF6h | bleibt außerhalb dieses konkreten Timerablaufs; Funktion weiterhin offen | nicht geklärt |

## 8. Grenzen

Die Analyse zeigt Instruktions- und Kontrollflussbeziehungen. Sie beweist nicht die beabsichtigte semantische Bezeichnung der Zähler, die Einheit der berechneten Werte oder das gesamte Zusammenspiel mit anderen Kernelmodulen. Insbesondere werden die DOS-Zeitfelder aus 115CAh separat gespeichert; daraus folgt nicht automatisch, dass 0FE2h/0FE4h eine bestimmte reale Zeiteinheit darstellen.

Es wurden keine Dateien verändert und keine Laufzeittests durchgeführt.

## 9. Nächster Schritt

Als nächstes sollte die Datenflusskette der Zielwerte 1088h, 108Ah und 108Ch untersucht werden. Ihre späteren Leser und Verwendungen können zeigen, ob der Kernel die berechneten Werte als Wartezeit, Verzögerung, Zeitmessung oder für eine andere interne Funktion nutzt.
