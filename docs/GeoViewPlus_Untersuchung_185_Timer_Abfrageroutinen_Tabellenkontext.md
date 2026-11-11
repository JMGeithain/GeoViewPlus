# Untersuchung 185 – Referenz- und Tabellenkontext der Timer-Abfrageroutinen

**Projekt:** GeoViewPlus  
**Datei:** KERNEL.EXE aus Basebox-SVGA-Ensemble12  
**Methode:** schreibgeschützte statische Analyse des MZ-Ladebereichs und Disassemblierung der Fundstellen  
**Abgrenzung:** GeoWorks / PC/GEOS 1.x.

## 1. Ziel

Untersuchung 184 hatte die FAR-Routinen 9567h und 9570h als Leser der Timer-Ergebnisfelder 108Ch bzw. 1088h/108Ah identifiziert. Hier wurde geprüft, ob direkte Verweise auf diese Routinen existieren und ob ihr Tabellenumfeld eine Exportfunktion belegt.

## 2. Bestätigte Leseroutinen

Die beiden Routinen lauten:

    9567  push ds
    9568  call 961Ah
    956B  mov ax,ds:108Ch
    956E  pop ds
    956F  retf

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

Die Hilfsroutine 961Ah lädt DS aus dem CS-relativen Wort bei 9618h. Dieses Wort enthält 0E34h. Damit greifen beide Leser auf das Kernel-Datensegment zu und stellen anschließend das ursprüngliche DS wieder her.

## 3. Direkte Fundstellen der Routinenadressen

Die 16-Bit-Werte 9567h und 9570h wurden im gesamten MZ-Ladebereich gesucht.

- 9567h erscheint als Wort an Ladeoffset E32Ch.
- 9570h erscheint als Wort an Ladeoffset E200h.
- 958Dh erscheint unmittelbar danach an E202h.
- Weitere aufeinanderfolgende Wörter ab E204h sind 9600h, 9605h und weitere Codeadressen.

Der Bereich ab E200h ist somit ein Kandidat für eine Tabelle aus 16-Bit-Codeoffsets. Das benachbarte Vorkommen von 9570h, 958Dh, 9600h und 9605h unterstützt diese Einordnung.

**Einschränkung:** Eine direkte Instruktion, die den Tabellenanfang E200h als Basis verwendet, wurde in dieser Untersuchung nicht eindeutig nachgewiesen. Die Tabellenfunktion ist daher eine plausible strukturelle Einordnung, aber noch keine bestätigte Exporttabelle.

Das einzelne Wort 9567h bei E32Ch liegt außerhalb dieser zusammenhängenden Offsetfolge. Es könnte zu einer anderen Tabelle oder einem anderen Verweisfeld gehören. Seine genaue Rolle ist offen.

## 4. Keine direkte Aufrufstelle im Code nachgewiesen

Die Suche nach den unmittelbaren 16-Bit-Adresswerten fand die oben genannten Tabellen-/Datenvorkommen. Es wurde kein eindeutiger direkter FAR-CALL-Befehl mit eingebettetem Ziel 9567h oder 9570h gefunden.

Das ist bei einem Kernel mit indirekten Tabellenaufrufen nicht überraschend. Es beweist aber weder, dass die Routinen öffentlich exportiert sind, noch, dass sie unbenutzt wären.

## 5. Zusätzliche Entdeckung: Snapshot- und Reset-Routinen

Unmittelbar hinter den beiden Leseroutinen liegen zwei weitere FAR-Routinen:

### 5.1 Routine 9593h – Kopieren eines Datenblocks

    9593  push cx
    9594  push si
    9595  push di
    9596  push ds
    9597  call 961Ah
    959A  cli
    959B  mov si,0FCEh
    959E  mov cx,000Ah
    95A1  rep movsw
    95A3  sti
    95A4  pop ds
    95A5  pop di
    95A6  pop si
    95A7  pop cx
    95A8  retf

Die Routine kopiert zehn WORDs (20 Bytes) aus dem Kernel-Datensegment ab DS:0FCEh nach ES:DI. Die Kopie erfolgt bei gesperrten Interrupts. Sie verändert die Quelle nicht.

### 5.2 Routine 95A9h – Snapshot mit anschließendem Löschen

    95A9  push cx
    95AA  push si
    95AB  push di
    95AC  push es
    95AD  mov si,ds
    95AF  mov es,si
    95B1  mov si,0FE2h
    95B4  mov di,0FCEh
    95B7  mov cx,0009h
    95BA  rep movsw
    95BC  mov di,0FE2h
    95BF  xor ax,ax
    95C1  mov cx,0009h
    95C4  rep stosw
    95C6  mov bx,0FF8h
    95C9  cmp word ptr ds:0FF6h,ax
    95CD  jne 95D6
    95CF  mov bx,[bx+6]
    95D2  or bx,bx
    95D4  je 95D9
    95D6  inc ax
    95D7  jmp 95CF
    95D9  mov ds:0FE0h,ax
    95DC  pop es
    95DD  pop di
    95DE  pop si
    95DF  pop cx
    95E0  ret

Die Routine kopiert neun WORDs (18 Bytes) aus DS:0FE2h nach DS:0FCEh, löscht anschließend die neun ursprünglichen WORDs ab 0FE2h und wartet in einer Schleife auf einen Zustand, der von 0FF6h und einer verketteten Struktur ab 0FF8h abhängt. Danach speichert sie den Schleifenzähler in 0FE0h.

Die Routine umfasst damit nicht nur die beiden Timer-Wörter 0FE2h/0FE4h, sondern auch die folgenden WORD-Felder bis einschließlich 0FF2h. Das ist ein wichtiger Hinweis auf einen zusammenhängenden Neun-WORD-Datenbereich ab 0FE2h. Die genaue Semantik der einzelnen Felder bleibt offen.

## 6. Bedeutung für die Exportfrage

Die Snapshot-Routinen sind ebenfalls mit RETF bzw. in der zweiten Routine mit RET abgeschlossen; daraus allein folgt keine öffentliche Exportierung. Für die beiden Zeitwert-Leser 9567h und 9570h gilt weiterhin:
- FAR-Aufrufkonvention ist direkt belegt.
- DS wird über 961Ah auf 0E34h gesetzt.
- Rückgaberegister AX bzw. AX:BX sind direkt belegt.
- Ein öffentlicher Kernel-Exportname oder eine eindeutige Exportnummer ist noch nicht gefunden.

Der Tabellenkandidat ab E200h muss in einer Folgestudie mit seinen tatsächlichen Zugriffen und seiner Einbindung in den Kernel-Dispatcher verknüpft werden.

## 7. Ergebnis

1. Die Leseroutinen 9567h und 9570h sind als FAR-Routinen bestätigt.
2. 9570h ist als Wort in einem möglichen Offsettabellenbereich ab E200h eingetragen; 9567h erscheint als isolierter Wortwert bei E32Ch.
3. Eine bestätigte öffentliche Exportzuordnung liegt noch nicht vor.
4. Die Routine 95A9h kopiert neun WORDs aus dem Bereich 0FE2h–0FF2h in einen Snapshotbereich ab 0FCEh und löscht anschließend die Originalfelder.
5. 0FF6h und die verkettete Struktur ab 0FF8h beeinflussen die anschließende Warteschleife.

## 8. Nächster Schritt

Als nächstes wird die Neun-WORD-Struktur 0FE2h–0FF2h mit allen Schreib-/Lesezugriffen untersucht. Zusätzlich ist der Zugriffspfad auf den Offsettabellenkandidaten E200h zu suchen. Erst dann lässt sich entscheiden, ob die Tabelle Kernel-Exports, Dispatch-Einträge oder eine andere interne Offsetliste enthält.

Es wurden keine Originaldateien verändert und keine Laufzeittests durchgeführt.
