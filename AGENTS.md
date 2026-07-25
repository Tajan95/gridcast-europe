# AGENTS.md

Dieses Repository gehört zum IU-Modul „Data Analytics und Big Data“.

## Projekt

**GridCast Europe**

Ziel ist ein vollständiges, präsentierbares Data-Science-Projekt nach dem
QUA³CK-Prozessmodell mit ausführlichen Jupyter Notebooks, trainiertem und
evaluiertem ML-Modell, Streamlit-App und nachvollziehbarer Dokumentation.

Prüfungstermin: **28.07.2026**.

## Verbindliche Forschungsrichtung

Primärfrage:

> Wie genau lässt sich die stündliche Stromlast ausgewählter europäischer
> Länder anhand historischer Last-, Wetter- und Kalenderdaten für einen
> chronologisch späteren, vollständig zurückgehaltenen Zeitraum
> prognostizieren?

Erweiterung:

> Wie verändert sich ein aus historischen Mustern abgeleitetes Lastprofil für
> einen frei wählbaren Zukunftszeitpunkt unter klimatologischen und
> strukturellen Szenarioannahmen?

## Scope-Leitplanken

- Kernmodell: überwachte Regression für Deutschland (`DE`), Frankreich
  (`FR`) und Polen (`PL`).
- Last-Lags 24/48/168 Stunden sind keine App-Eingaben.
- Historischer Backtest und Zukunftsszenario sind methodisch zu trennen.
- Das Zukunftsszenario verwendet ein statistisch typisches Wetterprofil.
- Szenarien sind konditionale Was-wäre-wenn-Rechnungen.
- Nachfragewachstum und Rechenzentren sind transparente externe Annahmen.
- Keine Blackout- oder Netzausfallwahrscheinlichkeit behaupten.
- Zulässig ist nur die klar benannte Wahrscheinlichkeit eines extremen
  Lastzustands relativ zu einer historischen Quantilschwelle.

## Methodische Leitplanken

- Chronologischer Split; kein zufälliger 70/30-Split.
- Baselines und Profile leakage-frei berechnen.
- Testjahr nicht für Auswahl oder Tuning verwenden.
- Reanalysewetter und typisches Szenariowetter klar unterscheiden.
- UTC, lokale Zeit und Sommerzeit dokumentieren.
- Primärmetrik: länderweise gleichgewichteter Makro-nMAE.
- „Baseline-Modell“ und „Basisszenario“ sprachlich trennen.

## Repository-Konventionen

- Deutsche Dokumentation bevorzugt.
- QUA³CK-Phasen unter `documents/QUA3CK/` pflegen.
- Wiederverwendbaren Code unter `src/gridcast/` ablegen.
- Rohdaten, Modelldatensätze, Zwischenmodelle und Secrets nicht committen.
- Ausschließlich das verifizierte finale Deployment-Artefakt
  `models/gridcast_final_2015_2019.joblib` darf versioniert werden.
- Jede Wahrscheinlichkeitsaussage nennt Schwelle, Referenzperiode und
  Kalibrierungsdaten.
