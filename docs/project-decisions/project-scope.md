# Project Scope und Forschungsfragen

**Stand:** 23.07.2026  
**Status:** beschlossen

## Hauptfrage

> Wie genau lässt sich die Stromlast ausgewählter europäischer Länder 24 Stunden im Voraus anhand historischer Last-, Wetter- und Kalenderdaten prognostizieren?

### Warum 24 Stunden?

Der Prognosehorizont von 24 Stunden ist eine **bewusste Scope-Entscheidung**, keine vom Datensatz vorgegebene Naturkonstante. Er bildet eine Day-ahead-Prognose ab: Für alle 24 Stunden des nächsten Tages wird eine Lastkurve erstellt.

Dieser Horizont ist für das Projekt sinnvoll, weil:

- Kalendermerkmale der Zielstunden bereits bekannt sind,
- ein Wetterprofil für den Folgetag grundsätzlich als Vorhersage verfügbar sein kann,
- Lastmessungen bis einschließlich 24 Stunden vor jeder Zielstunde sicher als Eingaben vorliegen,
- das Ergebnis als zusammenhängende Tageskurve gut evaluierbar und in Streamlit darstellbar ist.

Auch ein Horizont von einer Stunde, sieben Tagen oder einem Monat wäre grundsätzlich möglich. Dann müssten jedoch Features, Datenverfügbarkeit, Evaluation und App-Logik entsprechend neu entworfen werden. Insbesondere wären bei längeren Horizonten die Last-Lags nahe der Zielzeit noch nicht bekannt.

Für eine Zielstunde `t` lässt sich die derzeit vorgesehene Modelllogik kompakt so zusammenfassen:

> **Prognostizierte Last = Modell(Kalendermerkmale, Wettermerkmale, historische Lastmerkmale)**

Die Kalender- und Wettermerkmale beschreiben die Zielstunde `t`. Bei einer Day-ahead-Prognose enden historische Lastmerkmale mindestens 24 Stunden vor dieser Zielstunde.

`lag_24h`, `lag_48h` und `lag_168h` sind dabei **historische Messwerte als Features**. Sie sind nicht selbst „die 24-Stunden-Vorhersage“. Die gleich benannten naiven Baselines verwenden jeweils nur einen solchen Messwert als vollständige Vergleichsprognose.

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

## Datumswahl in der App

Die App unterscheidet zwei Modi:

1. **Historischer Backtest:** Auswahl eines Datums aus dem Testzeitraum. Das Modell verwendet nur Informationen, die 24 Stunden vorher verfügbar gewesen wären. Anschließend werden Prognose und tatsächlich gemessene Last verglichen.
2. **Szenarioanalyse:** Auswahl eines dokumentierten historischen Referenztages oder eines extern vorgegebenen Wetter-/Klimaprofils. Temperatur, Nachfrage und Rechenzentrumslast werden transparent verändert.

Ein beliebiges fernes Zukunftsdatum kann nicht allein aus seiner Kalenderangabe seriös vorhergesagt werden. Dafür fehlen insbesondere das konkrete Wetterprofil und die unmittelbar vorausgehenden realen Lastmessungen. Die App darf deshalb keine scheinpräzise Prognose für beispielsweise den 17. August 2042 erzeugen, wenn diese Eingangsdaten nicht durch ein externes Szenario bereitgestellt werden.

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
