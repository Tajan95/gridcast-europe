# U – Understanding the Data

**Status:** Datenimport, Qualitätsprüfung, Zusammenführung und erste EDA
abgeschlossen  
**Stand:** 25.07.2026

## Ziel der Phase

Die Datenphase prüft, ob die ausgewählten Quellen die Forschungsfrage
methodisch tragen. Untersucht werden Schema, Einheiten, zeitliche und
geografische Abdeckung, Missingness, Schlüsselqualität, Ausreißer,
Verteilungen, Zusammenhänge und Leakage-Risiken.

Ausführbare Hauptanalyse:

- [`notebooks/01_data_import_merge_eda.ipynb`](../../../notebooks/01_data_import_merge_eda.ipynb)

Wiederverwendbare Datenlogik:

- [`src/gridcast/config.py`](../../../src/gridcast/config.py)
- [`src/gridcast/data.py`](../../../src/gridcast/data.py)
- [`scripts/download_opsd_data.py`](../../../scripts/download_opsd_data.py)

## Verwendete Datenquellen

### OPSD Time Series

- Version: `2020-10-06`
- Datei: `time_series_60min_singleindex.csv`
- Rohumfang: 50.401 Datenzeilen und 300 Spalten
- Zeitbereich: 31.12.2014 23:00 UTC bis 30.09.2020 23:00 UTC
- Rolle: tatsächliche nationale Stromlast in MW
- DOI: https://doi.org/10.25832/time_series/2020-10-06

### OPSD Weather Data

- Version: `2020-09-16`
- Datei: `weather_data.csv`
- Rohumfang: 350.640 Datenzeilen und 85 Spalten
- Zeitbereich: 01.01.1980 00:00 UTC bis 31.12.2019 23:00 UTC
- Rolle: Temperatur sowie direkte und diffuse horizontale Strahlung
- Ursprung: NASA MERRA-2, durch Renewables.ninja länderweise aggregiert
- DOI: https://doi.org/10.25832/weather_data/2020-09-16

Die Rohdateien werden nicht in Git versioniert. Download und Aufbereitung sind
per Skript und Notebook reproduzierbar.

## Beobachtungseinheit und Join

Die gemeinsame Beobachtungseinheit lautet:

> `Land × UTC-Stunde`

Verknüpft wird auf:

- ISO-Ländercode
- `utc_timestamp`

Der Join wird programmatisch als 1:1-Beziehung validiert. UTC bleibt der
eindeutige technische Schlüssel. Lokale Kalenderfeatures werden anschließend
mit der jeweiligen IANA-Zeitzone abgeleitet.

## Auswahl der Kernländer

Verbindlich ausgewählt wurden:

- Deutschland (`DE`)
- Frankreich (`FR`)
- Polen (`PL`)

Die Auswahl basiert auf national eindeutig zuordenbaren Lastspalten, sehr hoher
Vollständigkeit, vollständigen Wetterfeatures und einem beherrschbaren
Prüfungsumfang.

| Land | Mögliche Stunden | Fehlende Lastwerte | Nutzbare Stunden | Vollständigkeit |
|---|---:|---:|---:|---:|
| DE | 43.824 | 0 | 43.824 | 100,000 % |
| FR | 43.824 | 30 | 43.794 | 99,932 % |
| PL | 43.824 | 1 | 43.823 | 99,998 % |
| **Gesamt** | **131.472** | **31** | **131.441** | **99,976 %** |

Die modulare Erweiterungsentscheidung ist dokumentiert unter:

- [`docs/project-decisions/country-scope-and-extensibility.md`](../../../docs/project-decisions/country-scope-and-extensibility.md)

## Zeitachsenqualität

Für beide Quellen gilt:

- monoton aufsteigende UTC-Zeitstempel,
- keine doppelten Zeitstempel,
- keine fehlenden UTC-Stunden innerhalb der jeweiligen Indexspanne.

Die Lastwerte selbst enthalten 31 fehlende Zielwerte. Die Wetterfeatures sind
im gemeinsamen Modellfenster vollständig.

## Bereinigung

Die 31 fehlenden Lastwerte werden entfernt und nicht imputiert.

Begründung:

- Die Stromlast ist die Zielvariable.
- Imputierte Zielwerte wären keine realen Beobachtungen.
- Sie könnten Training oder Evaluation künstlich verzerren.
- Der Datenverlust beträgt nur rund 0,024 %.

Potenzielle IQR-Ausreißer werden nicht automatisch entfernt. Ein statistisch
extremer Lastwert kann eine reale Kälte- oder Spitzenlastsituation darstellen.
Negative oder physikalisch unmögliche Lastwerte wurden nicht gefunden.

## Erzeugte Features

### Kalender und Lokalzeit

- lokale Stunde
- lokaler Wochentag
- Wochenende
- Monat
- Jahreszeit
- lokaler Tag des Jahres
- UTC-Offset zur Prüfung der Sommerzeit
- zyklische Sinus-/Kosinus-Kodierungen

### Wetter

- Temperatur in °C
- Temperaturquadrat
- Heating Degrees unter 15 °C
- Cooling Degrees über 22 °C
- direkte horizontale Strahlung in W/m²
- diffuse horizontale Strahlung in W/m²

Feiertage bleiben eine optionale spätere Erweiterung.

## Explorative Hauptbefunde

- Alle drei Länder zeigen ausgeprägte Tages- und Wochenzyklen.
- Wochenenden besitzen eine deutlich geringere mittlere Last.
- Frankreich zeigt die stärkste saisonale und negative lineare
  Temperatur-Last-Beziehung.
- Der Temperaturzusammenhang ist teilweise nichtlinear; Temperaturquadrat sowie
  Heiz- und Kühlgrad-Näherungen sind daher sachlich begründet.
- Die absoluten Lastniveaus unterscheiden sich stark zwischen den Ländern;
  Fehler müssen deshalb zusätzlich normalisiert und je Land berichtet werden.
- Jahresmittel von 2015–2019 zeigen kurzfristige Veränderungen, bilden aber
  keine belastbare automatische Extrapolation bis 2030 oder 2050.

## Chronologischer Split

- Training: 2015–2017
- Validierung: 2018
- Test: 2019

Nutzbare Zeilen:

| Land | Training | Validierung | Test | Gesamt |
|---|---:|---:|---:|---:|
| DE | 26.304 | 8.760 | 8.760 | 43.824 |
| FR | 26.290 | 8.749 | 8.755 | 43.794 |
| PL | 26.303 | 8.760 | 8.760 | 43.823 |

Der Testblock bleibt unangetastet, bis Features, Modellklasse und
Hyperparameter anhand von Training und Validierung feststehen.

## Typisches Wetterprofil für Szenarien

Aus der gesamten Wetterhistorie 1980–2019 wird der Median je:

> `Land × lokaler Monat × lokale Stunde`

gebildet. Daraus entstehen 864 Profilzeilen:

> `3 Länder × 12 Monate × 24 Stunden`

Dieses Profil dient ausschließlich der späteren Zukunftsszenarioebene. Im
historischen Backtest wird das tatsächlich beobachtete Reanalysewetter genutzt.

## Leakage-Schutz

- kein zufälliger 70/30-Split,
- keine Lastwerte aus 2019 im Training,
- keine TSO-Lastprognose als Eingabefeature,
- keine vorausgehenden Last-Lags im Kernmodell,
- Baselines und spätere Preprocessing-Schritte nur auf Trainingsdaten fitten,
- typisches Wetterprofil nicht mit tatsächlichem Testwetter verwechseln.

## Grenzen

- Nationale Wetterwerte sind bevölkerungsgewichtete Flächenaggregate und
  glätten regionale Extreme.
- Reanalysewetter ist im Backtest bekanntes Wetter, keine historische
  Day-ahead-Wettervorhersage.
- Drei Länder erlauben keine vollständige Repräsentation Europas.
- Der kurze Lastzeitraum trägt keine sichere jahrzehntelange Trendprognose.
- Feiertagseffekte sind noch nicht explizit kodiert.

## Nächster Schritt

In der A³-Phase werden:

1. länderspezifischer Mittelwert und Kalenderdurchschnitt als Baselines gebaut,
2. mindestens zwei Regressionsmodelle verglichen,
3. alle anpassbaren Schritte ausschließlich auf 2015–2017 gelernt,
4. Modell und Hyperparameter auf 2018 ausgewählt,
5. das endgültige Ergebnis einmalig auf 2019 bewertet.
