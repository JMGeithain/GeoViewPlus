# GeoViewPlus 0.4.1 – Korrektur der GeoWorks-1.x-Dateityp-Anzeige

## Anlass
Der Nutzer hat klargestellt, dass `UHR.GEO` keine von GeoWorks gelieferte Anwendung ist,
sondern eine Drittanbieter-Anwendung von Thomas Wachsmann. Nach seiner Angabe stammt
die Information aus *Das große Buch von GeoWorks*. Die Entwicklung erfolgte damals
ohne SDK-Hilfe durch Rückwärtsanalyse.

## Befund
GeoViewPlus erkannte die GeoWorks-1.x-Signatur `C7 45 CF 53` korrekt, zeigte aber
bei einer nicht standardisierten/Null-Dateitypkennung `0` den irreführenden Text
`Unknown / Non-GEOS`.

## Änderung in 0.4.1
Bei gültigem GeoWorks-1.x-Header und Typkennung 0 wird jetzt angezeigt:
`GeoWorks 1.x GEO-Datei (Drittanbieter / Typkennung 0)`

Das vermeidet die falsche Aussage „Non-GEOS“. Die Anzeige behauptet bewusst nicht,
dass jede Datei mit Typkennung 0 eine Anwendung ist. Die konkrete Einordnung von
`UHR.GEO` als Drittanbieter-Programm stammt aus der Nutzerinformation und der
genannten Buchquelle; die Binärdatei selbst wurde in diesem Arbeitsschritt nicht
untersucht.

## Abgrenzung
- Keine Änderungen am 1.x-Headerlayout oder an Originaldateien.
- Keine Vermischung mit GEOS 2.x.
- Die Heuristik `try_extract_icon()` bleibt eine Byte-Muster-Heuristik und ist
  weiterhin keine nachgewiesene Extraktion echter GEO-Programm-Icons.
