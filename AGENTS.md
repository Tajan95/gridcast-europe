# AGENTS.md

Dieses Repository enthält die Prüfungsleistung **GridCast Europe** für das
IU-Modul „Data Analytics und Big Data“ (Prüfungstermin: 28.07.2026).

## Verbindlicher Scope

- Regression der stündlichen Stromlast für Deutschland, Frankreich und Polen.
- Chronologischer Split: 2015–2017 Training, 2018 Validierung, 2019 Test.
- Testjahr nicht für Auswahl oder Tuning verwenden.
- Primärmetrik: länderweise gleichgewichteter Makro-nMAE.
- Historischen Backtest und konditionales Zukunftsszenario strikt trennen.
- Szenarien nutzen typisches Wetter und explizite Strukturannahmen.
- Keine Blackout-, Netzüberlastungs- oder Netzausfallwahrscheinlichkeit
  behaupten.

## Arbeitskonventionen

- Deutsche Dokumentation bevorzugt.
- Notebooks sind die QUA³CK-Hauptdokumentation; `README.md` ist der zentrale
  Einstieg.
- Wiederverwendbaren Code unter `src/gridcast/` ablegen.
- Rohdaten, Modelldatensätze, Zwischenmodelle und Secrets nicht committen.
- Ausschließlich `models/gridcast_final_2015_2019.joblib` darf als finales
  Deployment-Modell versioniert werden.
- Jede Aussage zum Extremzustandsindikator nennt Schwelle, Referenzperiode und
  Kalibrierungsdaten.
