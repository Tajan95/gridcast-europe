# GridCast Europe

Machine-Learning-Projekt zur stündlichen Stromlastprognose für Deutschland,
Frankreich und Polen im IU-Modul **Data Analytics und Big Data**. Das
Repository folgt dem **QUA³CK-Prozessmodell** und verbindet einen überprüfbaren
historischen Backtest mit einer klar getrennten Zukunftsszenarioanalyse.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gridcast-europe.streamlit.app/)

> **Cloud-Status (25.07.2026):** Das Deployment ist eingerichtet. Der erste
> Plattformstart endete unter der dort gewählten Python-3.14-Laufzeit mit einem
> nativen Prozessabsturz; die lokal unter Python 3.12 verifizierte App und alle
> Projektartefakte sind davon unberührt.

## Forschungsfrage

> Wie genau lässt sich die stündliche Stromlast ausgewählter europäischer
> Länder anhand historischer Last-, Wetter- und Kalenderdaten für einen
> chronologisch späteren, vollständig zurückgehaltenen Zeitraum
> prognostizieren?

Die Streamlit-Erweiterung untersucht zusätzlich, wie sich ein historisch
abgeleitetes Lastprofil unter expliziten Temperatur-, Nachfrage- und
Rechenzentrumsannahmen verändert.

## Kernergebnisse

| Ergebnis | Wert |
|---|---:|
| Nutzbare Beobachtungen | 131.441 Länder-Stunden |
| Chronologischer Split | 2015–2017 / 2018 / 2019 |
| Finales Testmodell | Histogram Gradient Boosting |
| Test-Makro-nMAE 2019 | **2,71 %** |
| Kalender-Baseline 2019 | 4,88 % |
| Verbesserung gegenüber der Kalender-Baseline | **44,5 %** |
| Länderspezifischer nMAE | DE 2,49 % · PL 2,74 % · FR 2,91 % |

Das Modell wurde ausschließlich anhand von Training und Validierung ausgewählt.
Erst danach wurde die eingefrorene Konfiguration auf 2015–2018 refittet und
einmalig auf 2019 getestet.

## Zwei bewusst getrennte Aussageebenen

1. **Historischer Backtest:** tatsächliches Reanalysewetter und gemessene Last
   aus dem unangetasteten Testjahr 2019; direkter Vergleich von HGB,
   Kalender-Baseline und Istwert.
2. **Konditionales Zukunftsszenario:** typisches Wetterprofil aus 1980–2019,
   frei gewählte Temperaturabweichung sowie transparente Nachfrage- und
   Rechenzentrumseffekte.

Die zweite Ebene ist eine Was-wäre-wenn-Rechnung, keine konkrete
Wettervorhersage oder autonome Langfristprognose. Der explorative
Extremzustandsindikator beschreibt die Überschreitung einer historischen
Lastschwelle und ausdrücklich **keine Blackout-Wahrscheinlichkeit**.

## QUA³CK-Projektverlauf

| Phase | Hauptartefakt | Inhalt |
|---|---|---|
| Q – Question | [`00_question_gridcast.ipynb`](notebooks/00_question_gridcast.ipynb) | Forschungsfrage, Hypothesen, Scope und Erfolgsregeln |
| U – Understanding | [`01_data_import_merge_eda.ipynb`](notebooks/01_data_import_merge_eda.ipynb) | Import, Datenqualität, Join, Features und EDA |
| A³ – Algorithms | [`02_a3_model_development.ipynb`](notebooks/02_a3_model_development.ipynb) | Baselines, Ablationen, Modelle und Hyperparameter |
| C – Conclude | [`03_conclude_compare.ipynb`](notebooks/03_conclude_compare.ipynb) | Refit, einmaliger Test 2019 und Schlussfolgerung |
| K – Knowledge Transfer | [`04_knowledge_transfer.md`](notebooks/04_knowledge_transfer.md) | App, Szenariologik, Risikoindikator und Bereitstellung |

Die kompakten, maschinenlesbaren Ergebnisse liegen unter
[`reports/a3/`](reports/a3/), [`reports/c/`](reports/c/) und im
[`K-Deploymentreport`](reports/k_deployment.json).

## Datenquellen

- [OPSD Time Series, Version 2020-10-06](https://doi.org/10.25832/time_series/2020-10-06):
  nationale stündliche Stromlast
- [OPSD Weather Data, Version 2020-09-16](https://doi.org/10.25832/weather_data/2020-09-16):
  MERRA-2-basierte Temperatur sowie direkte und diffuse Strahlung

Die Beobachtungseinheit ist `Land × UTC-Stunde`. Rohdaten und große
Zwischendaten werden nicht versioniert; der Download ist über
[`scripts/download_opsd_data.py`](scripts/download_opsd_data.py)
reproduzierbar.

## Streamlit-App lokal starten

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

Die App umfasst Überblick, historischen Backtest, Zukunftsszenario sowie
Methodik und Grenzen. Für die Inferenz wird ausschließlich das verifizierte
Modell
[`models/gridcast_final_2015_2019.joblib`](models/gridcast_final_2015_2019.joblib)
verwendet.

## Prüfungsartefakte

- [Fünfseitiges Handout (PDF)](documents/GridCast_Europe_Handout.pdf)
- [Editierbares Handout (DOCX)](documents/GridCast_Europe_Handout.docx)
- [Vortragsfolien (PPTX)](documents/GridCast_Europe_Referat.pptx)
- [Vortragsfolien (PDF)](documents/GridCast_Europe_Referat.pdf)
- [Sprechtext](documents/GridCast_Europe_Sprechtext.md)
- [Dokumentation der KI-Nutzung](documents/KI-Nutzung.md)

## Repository-Struktur

```text
data/app/           kompakte Deployment-Daten
documents/          Handout, Präsentation, Sprechtext und KI-Dokumentation
models/             finales verifiziertes Deployment-Modell
notebooks/          fünf QUA³CK-Hauptartefakte
reports/a3/         Validierungs- und Auswahlreports
reports/c/          Test- und Generalisierungsreports
scripts/            reproduzierbare Download- und Build-Schritte
src/gridcast/       wiederverwendbare Daten-, Modell- und Szenariologik
streamlit_app/      interaktive Anwendung
tests/              automatisierte Modell-, Risiko- und App-Tests
```

## Grenzen

- Gültigkeit nur für DE, FR und PL sowie den Lastzeitraum 2015–2019.
- Reanalysewetter im Backtest ist keine operative Wetterprognose.
- Regionale deutsche Feiertage sind nicht separat modelliert.
- Das auf 2015–2019 refittete App-Modell besitzt keine zusätzliche
  unabhängige Testkennzahl; maßgeblich bleibt der vorherige C-Backtest.
- Neue Länder oder Datenstände erfordern erneut Qualitätsprüfung, Evaluation
  und eine QUA³CK-Schleife.
