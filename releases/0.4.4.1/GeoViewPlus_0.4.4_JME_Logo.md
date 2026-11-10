# GeoViewPlus 0.4.4 – Über-Dialog, Layoutkorrektur

## Korrektur nach Windows-Sichtprüfung
- Dialogtext verwendet echte Zeilenumbrüche statt sichtbarer `\\n`-Zeichen.
- Text wird bei 510 Pixeln umgebrochen; das Dialogfenster bleibt dadurch deutlich schmaler.
- JME-Logo auf maximal 104 × 104 Pixel verkleinert.
- Copyright-Zeile lautet jetzt: „Möllerjaner © 2026 Johannes Möller“.
- Das Logo bleibt als PyInstaller-Paketressource eingebunden.

## Prüfung
Python-Syntax und Regressionstests werden lokal ausgeführt. Die tatsächliche
Fensterdarstellung muss nach dem EXE-Neubau erneut unter Windows kontrolliert
werden.
