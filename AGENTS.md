# AGENTS.md

Dieses Repository gehört zum IU-Modul „Data Analytics und Big Data“.

## Projekt

**GridCast Europe**

Ziel ist ein vollständiges, präsentierbares Data-Science-Projekt nach dem QUA³CK-Prozessmodell mit ausführlichem Jupyter Notebook, trainiertem und evaluiertem ML-Modell, Streamlit-App und nachvollziehbarer Dokumentation.

Prüfungstermin: **28.07.2026**.

## Verbindliche Forschungsrichtung

Primärfrage:

> Wie genau lässt sich die stündliche Stromlast ausgewählter europäischer Länder anhand historischer Last-, Wetter- und Kalenderdaten für einen chronologisch späteren, vollständig zurückgehaltenen Zeitraum prognostizieren?

Erweiterung:

> Wie verändert sich ein aus historischen Mustern abgeleitetes Lastprofil für einen frei wählbaren Zukunftszeitpunkt unter klimatologischen und strukturellen Szenarioannahmen?

## Scope-Leitplanken

- Kernmodell: überwachte Regression der stündlichen Last für voraussichtlich drei europäische Länder.
- Features: Land, Kalenderzyklen, Werktag/Wochenende, Saison, Temperatur und weitere ausreichend vollständige Wettermerkmale.
- Last-Lags 24/48/168 Stunden sind nicht Bestandteil des Kernmodells und keine App-Eingaben.
- Der historische Backtest und die langfristige Szenarioanalyse sind methodisch und sprachlich zu trennen.
- Das Zukunftsszenario verwendet ein automatisch abgeleitetes statistisch typisches Wetterprofil.
- Szenarien sind konditionale Was-wäre-wenn-Rechnungen, keine behaupteten kausalen Langfristprognosen.
- Langfristiges Nachfragewachstum wird als transparente externe Annahme modelliert, nicht als sichere ML-Extrapolation.
- Rechenzentren werden nur als transparenter externer Lastaufschlag oder offizieller Szenariopfad berücksichtigt.
- Keine Aufteilung nach Wirtschaftssektoren im Pflichtumfang.
- Kein eigenes Stromnetzausbau- oder Wettervorhersagemodell.
- Keine Blackout- oder Netzausfallwahrscheinlichkeit behaupten.
- Zulässig ist nur die klar benannte „Wahrscheinlichkeit eines extremen Lastzustands“ relativ zu einer historischen Quantilschwelle.

## Methodische Leitplanken

- Chronologischer Split; kein zufälliger 70/30-Split für eine Zeitprognose.
- Testzeitraum unangetastet lassen, bis Modell und Hyperparameter feststehen.
- Baseline-Modelle als länderspezifischen Mittelwert und Kalenderdurchschnitt immer berichten.
- Alle Baselines und klimatologischen Profile leakage-frei aus den dafür vorgesehenen historischen Daten berechnen.
- Tatsächliches Reanalysewetter im Backtest ausdrücklich vom statistisch typischen Wetterprofil der Szenarioanalyse unterscheiden.
- Ein historischer Zeittrend darf explorativ analysiert, aber nicht unkritisch bis 2030 oder 2050 extrapoliert werden.
- UTC, lokale Zeit und Sommerzeit dokumentiert behandeln.
- Länder erst nach gemessener Vollständigkeit und Joinbarkeit auswählen.
- Modellgüte mit MAE, RMSE, normalisiertem MAE und Baseline-Verbesserung bewerten; R² nur ergänzend.
- „Baseline-Modell“ und „Basisszenario“ sprachlich strikt trennen.
- Eine dargestellte 24-Stunden-Tageskurve nicht mit einem 24-Stunden-Prognosehorizont verwechseln.

## Repository-Konventionen

- Deutsche Dokumentation bevorzugt.
- QUA³CK-Phasen in `documents/QUA3CK/` pflegen.
- Kandidatenkarten in `docs/data-sources/` pflegen.
- Forschungsentscheidungen in `docs/project-decisions/` dokumentieren.
- Rohdaten, externe Daten und Modelldaten in `data/raw/`, `data/external/` und `data/processed/` trennen.
- Wiederverwendbaren Code unter `src/gridcast/` ablegen; Notebooks orchestrieren, statt Logik zu duplizieren.
- Keine großen Daten, Modelle oder Secrets committen.
- Jede Wahrscheinlichkeitsaussage muss ihre Schwelle, Referenzperiode und Kalibrierungsdaten nennen.
