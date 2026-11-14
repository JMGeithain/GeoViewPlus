# GeoViewPlus 0.5 – Alpha47

## Untersuchung 232: Rekursive Kontrollfluss- und Erreichbarkeitsanalyse

Alpha47 verfolgt Code-Ressourcen rekursiv ab 343 eindeutigen Startadressen: 321 aus Typ-0x22-Programmsegmentverweisen, 7 eindeutige Typ-0x24-Programmpointer und 16 Exportadressen.

Ergebnis: 1.206 Basic-Block-Starts, 11.246 dekodierte Instruktionsadressen, 2.374 Kontrollflusskanten und 21 überlappende Dekodierungen. 48 von 66 MOV-SI-Kandidaten werden erreicht; 18 bleiben im aktuellen Modell unerreicht. **Unerreicht bedeutet nicht nachgewiesen toter Code.** Indirekte Dispatch-Mechanismen und nicht aufgelöste Fixup-Formen bleiben offen.

Bericht: [Untersuchung 232 – Alpha47](../../docs/GeoViewPlus_Untersuchung_232_Alpha47_ControlFlow.md). Analyseprogramm und Tests: [analysis/alpha47](README.md).

Voraussetzungen: Python 3.10+, GNU objdump (i8086), GEOWORKS.zip.
