# GeoView Plus – Untersuchung 0.4.16
## 50 Prüfschritte: Segment-Trampolin 257Eh, Kernel-Service 961Ah und Vergleich mit KERNEL.OLD

**Geltungsbereich:** ausschließlich PC/GEOS 1.x / deutsche GeoWorks-1.2-Kerneldateien.
**Untersuchte Dateien:** KERNEL.EXE (72.736 Bytes) und KERNEL.OLD (72.688 Bytes).
**Methode:** statische Analyse der MZ-Ladebilder; Dateioffset = 0x600 + Ladebildoffset. Originaldateien unverändert; keine Laufzeittests.

## Wichtig: Korrektur zu Untersuchung 0.4.15

Die frühere Disassemblierung war an zwei Stellen falsch zugeordnet:
- 257Eh ruft **961Ah** auf, nicht 9C1Ah.
- 2FD2h ist nicht die dort beschriebene Stack-Hilfsroutine. Der Aufruf im fraglichen Ablauf ist 29D2h; die Stack-Sicherungsroutine liegt tatsächlich bei 29D2h, die Wiederherstellung bei 29E4h.

Die frühere Aussage, 257Eh rufe 9C1Ah auf, ist zurückzunehmen. Diese Untersuchung ersetzt diese Zuordnung.

## 50 Prüfschritte

### A. Adressierung und Rohdaten

1. Der MZ-Header von KERNEL.EXE ist 0x600 Bytes lang (e_cparhdr=0x60).
2. Der MZ-Header von KERNEL.OLD ist ebenfalls 0x600 Bytes lang.
3. Für die Ladebildoffsets gilt Dateioffset = 0x600 + Ladebildoffset.
4. Die Disassemblierung ab 0x2570 ergibt in KERNEL.EXE die Routine bei 0x257E.
5. Die Bytes ab 0x257E lauten E8 99 70 8E 1F 8B 36 28 00 8E 1E 2A 00 CB.
6. E8 99 70 ist ein relativer Near-CALL mit Ziel 0x961A.
7. Das Ziel ist 0x961A und nicht 0x9C1A.
8. 0x9C1A ist eine eigenständige andere Stelle im Kernel-Ladebild.
9. Die Instruktionen 0x257E bis 0x258B sind vollständig abgegrenzt.
10. Die alte Kerneldatei enthält eine entsprechende Sequenz an verschobener Adresse.

### B. Routine 961Ah in KERNEL.EXE

11. Bei 0x961A steht mov ds,word ptr cs:[9618h].
12. Bei 0x961F folgt RET.
13. Das Wort CS:9618h enthält 0x0E34.
14. Der Aufruf 961Ah setzt DS auf 0x0E34.
15. Diese kurze Routine verändert BX, SI und AX nicht.
16. Sie kehrt mit RET zurück, nicht mit RETF.
17. Bei 0x9620 liegt eine parallele Routine, die ES statt DS lädt.
18. 9620 lädt ES aus CS:[9618h] und kehrt mit RET zurück.
19. Die Routinen stellen Kernel-Datensegmentregister bereit.
20. 961Ah ist hier Segmentinitialisierung, kein Dateizugriff.

### C. Routine 257Eh im Detail

21. 257Eh ruft zuerst 961Ah auf und erhält DS=0E34h.
22. Danach führt 8E 1F die Operation mov ds,[bx] aus.
23. Der Speicheroperand [BX] wird noch mit DS=0E34h adressiert.
24. Der gelesene Wortwert wird zum neuen DS-Segmentwert.
25. Anschließend liest 8B 36 28 00 das Wort DS:[0028h] nach SI.
26. Diese Leseoperation verwendet bereits das neue DS.
27. Danach lädt 8E 1E 2A 00 DS aus DS:[002Ah].
28. Auch dieser Operand wird vor dem Wechsel mit dem aktuellen DS adressiert.
29. CB ist RETF und kehrt mit dem zuvor auf dem Stack bereitgestellten CS/IP-Paar zurück.
30. Die Routine liefert als Ergebnis die Kombination DS:SI; sie löst eine über BX referenzierte Struktur auf.

### D. Stack-Konvention und Aufrufer 25A1h

31. Bei 25A1h wird zunächst DS gesichert (push ds).
32. Der Aufrufer ruft danach 961Ah auf; DS wird auf 0E34h gesetzt.
33. Nach Prüfung AX==6 wird 29D2h aufgerufen.
34. 29D2h sichert Register und Segmentregister auf dem Stack; die Bytes beginnen 06 1E 55 57 56 52 51 53 50.
35. Der nachfolgende Aufruf push cs; call 257Eh stellt den für RETF benötigten Rückkehr-CS-Wert bereit.
36. RETF konsumiert den Near-CALL-Rücksprung-IP und den zuvor gepushten CS-Wert; der Aufruf kehrt zum folgenden Befehl im selben Code-Segment zurück.
37. Direkt danach liest mov ax,[si] das erste Wort am zurückgegebenen DS:SI.
38. mov si,[si+2] liest das zweite Wort bei DS:(SI+2) und ersetzt SI.
39. Der anschließende Aufruf 961Ah setzt DS wieder auf 0E34h, während AX und SI erhalten bleiben.
40. Danach werden AX und SI in DS:[0746h] und DS:[0748h] geschrieben.

### E. Vergleich, Aufrufer und Grenzen

41. KERNEL.OLD enthält die entsprechende Segment-Laderoutine bei 9630h statt 961Ah.
42. Das zugehörige Segmentwort steht in KERNEL.OLD bei CS:962Eh und enthält 0x0E35.
43. Die passende Trampolinsequenz liegt in KERNEL.OLD bei 2588h statt 257Eh.
44. Die ältere Sequenz ruft 9630h auf und verwendet ebenfalls [BX], DS:[0028h], DS:[002Ah] und RETF.
45. Die Verschiebung der Routineadressen ist konsistent mit den unterschiedlichen Kernel-Builds; die Logik ist gleich.
46. In KERNEL.EXE wurden vier Near-CALL-Stellen auf 257Eh gefunden: 2563h, 25AEh, 423Bh und 425Ah.
47. Die Aufrufer 423Bh und 425Ah rufen 257Eh nach einer Initialisierung über 961Ah auf und verwenden anschließend einen indirekten Far-Aufruf über [SI].
48. Der Aufrufer 2563h verwendet nach 257Eh ebenfalls call far [si]; dies stützt die Interpretation, dass DS:SI einen Dispatch-Eintrag oder eine Methodenadresse bereitstellt.
49. Die genaue Struktur hinter [BX], die Bedeutung der Felder +28h/+2Ah und die Semantik der beiden Wörter an DS:SI sind durch diese Bytes allein nicht abschließend identifiziert.
50. Belastbar ist die Beschreibung von 257Eh als generischer Segment-/Offset-Auflöser für einen über BX referenzierten Kernel-Datensatz; DOS-Dateiöffner oder DOS-Treiber-Lader wäre unbelegt.

## Zusätzliche Rohdaten: Aufrufer 2563h

```asm
255E  call 29D2h
2561  push bx
2562  push cs
2563  call 257Eh
2566  mov di,0002h
2569  call far [si]
256B  pop bx
256C  call 961Ah
256F  dec word ptr ds:[0605h]
2573  mov ds,[bx]
2575  and byte ptr ds:[0003h],0DFh
257A  call 29E4h
257D  ret
```

## Zusätzliche Rohdaten: Aufrufer 423Bh / 425Ah

```asm
422A  push cx
422B  push bx
422C  push si
422D  push di
422E  push ds
422F  call 961Ah
4232  or bx,bx
4234  jne 423Ah
4236  mov bx,word ptr ds:[0609h]
423A  push cs
423B  call 257Eh
423E  mov bx,di
4240  mov di,000Ah
4243  call far [si]
```

```asm
424B  call 29D2h
424E  call 961Ah
4251  or bx,bx
4253  jne 4259h
4255  mov bx,word ptr ds:[0609h]
4259  push cs
425A  call 257Eh
425D  mov di,000Ch
4260  call far [si]
4262  call 29E4h
```

## Schlussfolgerung

Der neue Befund trennt drei Ebenen:
1. 961Ah stellt das Kernel-Datensegment DS bereit.
2. 257Eh löst anhand von BX einen Datensatz auf und liefert eine neue Adresse DS:SI.
3. Die Aufrufer verwenden diese Adresse anschließend für indirekte Far-Aufrufe oder lesen daraus zwei Wörter.

Damit ist der Zusammenhang zum Dispatch-/Methodenaufruf deutlich besser belegt als die frühere DOS-Dateiöffner-Hypothese. Die konkrete Objekt- oder Treiberstruktur muss als nächstes über die Herkunft von BX und die Erzeugung des Datensatzes untersucht werden.

## Nächste Untersuchung 0.4.17

- Alle vier Aufrufer von 257Eh einzeln rückwärts verfolgen.
- Herkunft und Lebensdauer von BX vor jedem Aufruf dokumentieren.
- DS:[BX] und die Felder +28h/+2Ah anhand der Erzeugerstellen identifizieren.
- Die indirekten Ziele call far [si] an 2569h, 4243h und 4260h vergleichen.
- Dieselben Pfade in KERNEL.OLD an den verschobenen Adressen verifizieren.

**Status:** 50 Prüfschritte statisch bearbeitet. Keine Laufzeittests. Keine Änderungen an Originaldateien oder am GeoView-Plus-Zeichensatzdecoder.
