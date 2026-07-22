# Kandidatenkarte: Open Power System Data – Weather Data

**Status:** A – priorisierte Kernquelle  
**Rolle:** Wetterfeatures

## Anbieter und Zugriff

- Anbieter: Open Power System Data (OPSD)
- Datenseite: https://data.open-power-system-data.org/weather_data/
- Version: `2020-09-16`
- DOI: https://doi.org/10.25832/weather_data/2020-09-16
- Formate: CSV, XLSX, SQLite und ZIP-Paket
- Ursprungsdaten: NASA MERRA-2, durch Renewables.ninja länderweise aggregiert
- Attribution: OPSD nennt eine Zitierempfehlung; Lizenz-/Attributionskette vor Veröffentlichung dokumentieren

## Inhalt und Granularität

- stündliche Temperatur
- direkte horizontale Strahlung
- diffuse horizontale Strahlung
- länderweise, bevölkerungsgewichtet über MERRA-2-Gitterzellen aggregiert
- 27 auf der Datenseite auswählbare europäische Ländercodes
- Daten bis einschließlich 2019

## Beobachtungseinheit und Join

- Beobachtungseinheit: `Land × UTC-Stunde`
- Join: ISO-Ländercode plus `utc_timestamp`
- erwartete 1:1-Verknüpfung mit den ausgewählten länderweiten OPSD-Lastspalten

## Feature-Nutzung

- Temperatur zum Zielzeitpunkt
- Temperaturquadrat oder Heating-/Cooling-Degree-Näherungen
- direkte und diffuse Strahlung optional
- Szenario-`ΔT` wird vor Modellinferenz auf das Temperaturprofil angewendet

## Risiken

- MERRA-2-Reanalyse ist im Backtest tatsächlich bekanntes Wetter, keine Day-ahead-Wettervorhersage
- ein länderweiter Bevölkerungsmittelwert glättet regionale Hitze- und Kälteextreme
- Strahlung kann hilfreich sein, darf aber nicht unnötig den Scope auf Erzeugungsprognosen erweitern
- Temperatur- und Lastspalten müssen exakt derselben geografischen Ebene entsprechen

## Eignung

- Kernmodell: sehr hoch
- Backtest: sehr hoch, mit klarer Reanalyse-Kennzeichnung
- echte operative Prognose: nur als Näherung; dafür wäre ein historisches Wettervorhersage-Archiv nötig

## Nächster Verifikationstest

1. `weather_data.csv` reproduzierbar herunterladen.
2. Zeitbereich, Ländercodes, Einheiten und Missingness messen.
3. Inner Join mit allen brauchbaren OPSD-Lastländern durchführen.
4. dokumentieren, wie viele Länder-Stunden nach Join und Lags verbleiben.

## Vorläufiges Urteil

**Geeignet und verbindlich priorisiert.** Die Reanalyse-Einschränkung muss im Referat ausdrücklich genannt werden.

