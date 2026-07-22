# AGENTS.md

Dieses Repository gehört zum IU-Modul „Data Analytics und Big Data“.

## Projekt

**GridCast Europe**

Ziel ist ein vollständiges, präsentierbares Data-Science-Projekt nach dem QUA³CK-Prozessmodell mit ausführlichem Jupyter Notebook, trainiertem und evaluiertem ML-Modell, Streamlit-App und nachvollziehbarer Dokumentation.

Prüfungstermin: **28.07.2026**.

## Verbindliche Forschungsrichtung

Primärfrage:

> Wie genau lässt sich die Stromlast ausgewählter europäischer Länder 24 Stunden im Voraus anhand historischer Last-, Wetter- und Kalenderdaten prognostizieren?

Erweiterung:

> Wie verändert sich das prognostizierte Lastprofil unter unterschiedlichen Temperatur-, Nachfrage- und Rechenzentrumsszenarien?

## Scope-Leitplanken

- Kernmodell: Day-ahead-Lastprognose für voraussichtlich drei europäische Länder.
- Features: Kalenderzyklen, Werktag/Wochenende, Saison, Temperatur, Last-Lags 24/48/168 Stunden, vergangenheitsbasierte rollende Statistiken und kurzfristige Laständerungen.
- Szenarien sind konditionale Was-wäre-wenn-Rechnungen, keine behaupteten kausalen Langfristprognosen.
- Rechenzentren werden nur als transparenter externer Lastaufschlag oder offizieller Szenariopfad berücksichtigt.
- Keine Aufteilung nach Wirtschaftssektoren im Pflichtumfang.
- Kein eigenes Stromnetzausbaumodell.
- Keine Blackout- oder Netzausfallwahrscheinlichkeit behaupten.
- Zulässig ist nur die klar benannte „Wahrscheinlichkeit eines extremen Lastzustands“ relativ zu einer historischen Quantilschwelle.

## Methodische Leitplanken

- Chronologischer Split; kein zufälliger 70/30-Split für eine Zeitprognose.
- Testjahr unangetastet lassen, bis Modell und Hyperparameter feststehen.
- Baseline-Modelle `load(t-24)` und `load(t-168)` immer berichten.
- Tatsächliches Reanalysewetter im Backtest ausdrücklich von einer realen Wettervorhersage unterscheiden.
- Keine Features verwenden, die zum Prognosezeitpunkt unbekannt wären.
- Rollende Features müssen strikt vor dem Zielzeitpunkt enden.
- UTC, lokale Zeit und Sommerzeit dokumentiert behandeln.
- Länder erst nach gemessener Vollständigkeit und Joinbarkeit auswählen.
- Modellgüte mit MAE, RMSE, normalisiertem MAE und Baseline-Verbesserung bewerten; R² nur ergänzend.
- „Baseline-Modell“ und „Basisszenario“ sprachlich strikt trennen.

## Repository-Konventionen

- Deutsche Dokumentation bevorzugt.
- QUA³CK-Phasen in `documents/QUA3CK/` pflegen.
- Kandidatenkarten in `docs/data-sources/` pflegen.
- Forschungsentscheidungen in `docs/project-decisions/` dokumentieren.
- Rohdaten, externe Daten und Modelldaten in `data/raw/`, `data/external/` und `data/processed/` trennen.
- Wiederverwendbaren Code unter `src/gridcast/` ablegen; Notebooks orchestrieren, statt Logik zu duplizieren.
- Keine großen Daten, Modelle oder Secrets committen.
- Jede Wahrscheinlichkeitsaussage muss ihre Schwelle, Referenzperiode und Kalibrierungsdaten nennen.

