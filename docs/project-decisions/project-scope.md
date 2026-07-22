# Project Scope und Forschungsfragen

**Stand:** 22.07.2026  
**Status:** beschlossen

## Hauptfrage

> Wie genau lässt sich die Stromlast ausgewählter europäischer Länder 24 Stunden im Voraus anhand historischer Last-, Wetter- und Kalenderdaten prognostizieren?

Für Land \(c\), Zielstunde \(t\) und Day-ahead-Horizont gilt:

\[
\widehat L_{c,t}
=
f\!\left(
\text{Kalender}_{c,t},
\text{Wetter}_{c,t},
L_{c,t-24},
L_{c,t-48},
L_{c,t-168},
\text{rollende Historie}_{c,<t}
\right)
\]

Die Formulierung `t` statt `t+24` macht deutlich: Die Features beschreiben die Zielstunde, historische Lastmerkmale enden jedoch mindestens 24 Stunden davor.

## Erweiterte Streamlit-Frage

> Wie verändert sich das prognostizierte Lastprofil unter unterschiedlichen Temperatur-, Nachfrage- und Rechenzentrumsszenarien?

## Pflichtumfang

| Bestandteil | Festlegung |
|---|---|
| Raum | voraussichtlich drei europäische Länder; Auswahl erst nach Qualitätsprüfung |
| Zeitauflösung | stündlich |
| Prognosehorizont | 24 Stunden im Voraus |
| Daten-Split | vorläufig 2015–2017 Training, 2018 Validierung, 2019 Test |
| Zielvariable | tatsächliche Stromlast in MW |
| Baselines | Last vor 24 h und vor 168 h |
| ML-Modelle | lineares/regularisiertes Modell und Gradient Boosting |
| Hauptmetriken | MAE, RMSE, normalisierter MAE, Baseline-Verbesserung |
| App | Prognosekurve, Szenariovergleich, Spitzenlastdifferenz, Extremzustandswahrscheinlichkeit |

## Pflichtfeatures

### Kalender und Zyklen

- Stunde des Tages, zyklisch kodiert
- Wochentag, zyklisch kodiert
- Werktag oder Wochenende
- Monat oder Jahreszeit
- optional länderspezifischer Feiertag

### Wetter

- Temperatur der Zielstunde
- nichtlineare Temperaturwirkung, z. B. Temperaturquadrat oder Heiz-/Kühlgrad-Näherungen
- optional direkte und diffuse horizontale Strahlung

### Historische Last

- `lag_24h`
- `lag_48h`
- `lag_168h`
- rollender Mittelwert und rollende Streuung, strikt aus verfügbarer Vergangenheit
- kurzfristige Veränderung, z. B. `lag_24h - lag_48h`

## Zweite Prognose-Ebene

Die Hauptprognose beweist zeitliche Generalisierung durch ein vollständig zurückgehaltenes zukünftiges Testjahr. Zusätzlich ermöglicht die App eine konditionale Szenarioanalyse außerhalb der historischen Referenzbedingungen.

Diese Ebene beantwortet:

> Wie würde sich das vom ML-Modell gelernte Lastprofil unter explizit gesetzten Zukunftsannahmen verändern?

Sie beantwortet nicht:

> Wie wird Europas gesamtes Energiesystem im Jahr 2050 mit Sicherheit aussehen?

## Außerhalb des Scopes

- sektorale Zerlegung der nationalen Stromlast
- eigenes Modell des europäischen Netzausbaus
- Lastflussrechnung, regionale Leitungsengpässe oder Netztopologie
- absolute Blackout- oder Netzausfallwahrscheinlichkeit
- gemeinsame kausale Prognose von Klima, Elektrifizierung, Rechenzentren und Netzausbau
- Deep Learning als Pflichtbestandteil

## Optional nach funktionierendem Kern

- benannte RCP-/Klimaszenarien aus CORDEX
- offizielle langfristige Nachfragepfade aus ENTSO-E TYNDP
- IEA-Rechenzentrumsszenarien als transparenter externer Kontext
- Feiertagsfeatures
- länderspezifische Modelle zusätzlich zu einem gemeinsamen Modell

## Definition of Done

Das Projekt ist prüfungsbereit, wenn:

1. Datenimport und Aufbereitung reproduzierbar sind,
2. mindestens drei Länder ausreichend vollständige, joinbare Daten besitzen,
3. alle Features zum Prognosezeitpunkt verfügbar oder als Backtest-Näherung gekennzeichnet sind,
4. zwei naive Baselines und mindestens zwei ML-Modellklassen verglichen wurden,
5. das finale Modell auf dem unangetasteten Testzeitraum mindestens eine naive Baseline schlägt,
6. Fehler nach Land und Tageszeit erklärt werden,
7. die Streamlit-App Ergebnisse und Grenzen korrekt kommuniziert.

