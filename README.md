# GridCast Europe

**Arbeitstitel:** Machine-learning-based European electricity load forecasting and scenario analysis

Dieses Repository entsteht für das IU-Modul **Data Analytics und Big Data** und folgt dem **QUA³CK-Prozessmodell**. Der Projekt-Pivot von WasteWise auf GridCast Europe wurde am 22.07.2026 beschlossen.

## Forschungsfrage

> Wie genau lässt sich die stündliche Stromlast ausgewählter europäischer Länder anhand historischer Last-, Wetter- und Kalenderdaten für einen chronologisch späteren, vollständig zurückgehaltenen Zeitraum prognostizieren?

Erweiterte Streamlit-Frage:

> Wie verändert sich ein aus historischen Mustern abgeleitetes Lastprofil für einen frei wählbaren Zukunftszeitpunkt unter klimatologischen und strukturellen Szenarioannahmen?

## Methodischer Kern

- stündliche Beobachtungseinheit `Land × UTC-Stunde`
- Kernländer: Deutschland (`DE`), Frankreich (`FR`) und Polen (`PL`)
- chronologischer Split: 2015–2017 Training, 2018 Validierung, 2019 Test
- 131.441 nutzbare Länder-Stunden nach Entfernung von 31 fehlenden Zielwerten
- Baseline-Modelle: länderspezifischer Mittelwert und Kalenderdurchschnitt
- Vergleichsmodelle: lineare/regularisierte Regression und Gradient Boosting
- Kernfeatures: Land, Kalenderzyklen und ausreichend vollständige Wettermerkmale
- Metriken: MAE, RMSE, normalisierter MAE, ergänzend sMAPE und R²
- Ziel: messbarer Mehrwert gegenüber der Kalender-Baseline auf dem unangetasteten Testzeitraum

## Berücksichtigte Faktoren

- Tages- und Wochenzyklen
- Werktage, Wochenenden und optional Feiertage
- Monate und Jahreszeiten
- Temperatur und nichtlineare Temperaturwirkungen
- direkte und diffuse horizontale Sonneneinstrahlung
- historischer Zeittrend nur explorativ
- langfristige Nachfrage- und Rechenzentrumsentwicklung als transparente Szenarioannahmen

## Zwei Ebenen

1. **Historischer Backtest:** Prognose eines chronologisch späteren, vollständig zurückgehaltenen Zeitraums und Vergleich mit den tatsächlichen Lastwerten.
2. **Konditionale Zukunftsszenarioanalyse:** frei wählbares Zukunftsdatum mit automatisch erzeugtem typischem Wetterprofil sowie Temperatur-, Nachfrage- und Rechenzentrumsszenarien.

Die zweite Ebene ist eine *Was-wäre-wenn*-Analyse. Sie wird nicht als konkrete Wettervorhersage oder autonome, kausale Lastprognose bis 2030 oder 2050 ausgegeben.

Eine angezeigte 24-Stunden-Kurve beschreibt den ausgewählten Kalendertag. Sie ist kein festgelegter operativer Prognosehorizont.

## QUA³CK-Notebooks und reproduzierbare Datenphase

- [Q-Notebook: Fragestellung und Experimentdesign](notebooks/00_question_gridcast.ipynb)
- [QUA³CK: Q – Question](documents/QUA3CK/01-question/README.md)
- [Ausführbares Import-/Merge-/EDA-Notebook](notebooks/01_data_import_merge_eda.ipynb)
- [QUA³CK: U – Understanding the Data](documents/QUA3CK/02-understanding-the-data/README.md)
- [A³-Notebook: Baselines, Modelle und Hyperparameter](notebooks/02_a3_model_development.ipynb)
- [QUA³CK: A³ – Model Development](documents/QUA3CK/03-a3-model-development/README.md)
- [A³-Auswahlreport](reports/a3/a3_selection.json)
- [C-Notebook: Refit, Test 2019 und Schlussfolgerung](notebooks/03_conclude_compare.ipynb)
- [QUA³CK: C – Conclude & Compare](documents/QUA3CK/04-conclude-and-compare/README.md)
- [C-Abschlussreport](reports/c/c_conclusion.json)
- [QUA³CK: K – Knowledge Transfer](documents/QUA3CK/05-knowledge-transfer/README.md)
- [Streamlit-App](streamlit_app/app.py)
- [K-Deploymentreport](reports/k/k_deployment.json)
- Fünfseitiges Handout:
  [PDF](documents/handout/GridCast_Europe_Handout.pdf) |
  [DOCX](documents/handout/GridCast_Europe_Handout.docx)
- Vortragsfolien:
  [PPTX](documents/presentation/GridCast_Europe_Referat.pptx) |
  [PDF](documents/presentation/GridCast_Europe_Referat.pdf) |
  [Sprechtext](documents/presentation/GridCast_Europe_Sprechtext.md)
- [Länder-Scope und modulare Erweiterbarkeit](docs/project-decisions/country-scope-and-extensibility.md)
- [Reproduzierbarer OPSD-Download](scripts/download_opsd_data.py)

Die Rohdaten werden lokal unter `data/raw/` abgelegt und nicht versioniert.

## Zentrale Dokumente

- [Project Scope und Forschungsfragen](docs/project-decisions/project-scope.md)
- [Modell-, Baseline- und Szenariodesign](docs/project-decisions/model-and-scenario-design.md)
- [Wahrscheinlichkeit eines extremen Lastzustands](docs/project-decisions/extreme-load-state.md)
- [Katalog der Datenquellen-Kandidaten](docs/data-sources/README.md)
- [QUA³CK-Arbeitsstruktur](documents/QUA3CK/README.md)
- [Dokumentation der KI-Nutzung](documents/ki-nutzungs.md)

## Repository-Struktur

```text
data/                       lokale Roh-, externe und Modelldaten
docs/data-sources/          standardisierte Kandidatenkarten
docs/project-decisions/     Scope, Gleichungen und methodische Entscheidungen
documents/QUA3CK/           Prüfungsdokumentation entlang der fünf Phasen
models/                     gespeicherte Modellartefakte und Metadaten
notebooks/                  Analyse- und Modellierungsnotebooks
reports/                    Abbildungen und Präsentationsartefakte
scripts/                    reproduzierbare Downloads und Hilfsschritte
src/gridcast/               wiederverwendbarer Python-Code
streamlit_app/              interaktive Anwendung
tests/                      automatisierte Tests
```

Rohdaten, große Modelldatensätze und Zwischenmodelle werden nicht in Git
versioniert. Als enge Ausnahme liegt das rund 1,9 MB große, verifizierte
Deployment-Modell unter
[`models/gridcast_final_2015_2019.joblib`](models/gridcast_final_2015_2019.joblib).
Download und Aufbereitung der Ausgangsdaten bleiben reproduzierbar per Code.

## Streamlit-App lokal starten

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

Die App enthält:

- Überblick mit Forschungsfrage und Kernergebnissen,
- historischen Out-of-sample-Backtest für wählbare Tage aus 2019,
- konditionale Zukunftsszenarien mit typischem Wetter,
- Temperatur-, Nachfrage- und Rechenzentrumseinstellungen,
- transparent begrenzten Extremzustandsindikator,
- Methodik- und Grenzendarstellung.

Für Streamlit Community Cloud:

- Repository: `Tajan95/gridcast-europe`
- Branch: `main`
- Entrypoint: `streamlit_app/app.py`
- Python: `3.12`
- Secrets: keine

## Status

Aktueller Stand: **Alle fünf QUA³CK-Phasen sind abgeschlossen. Auf dem
unangetasteten Testjahr 2019 erreicht das ausgewählte
Histogram-Gradient-Boosting-Modell nach Refit auf 2015–2018 einen Makro-nMAE
von 2,71 % und verbessert die Kalender-Baseline um 44,5 %. Das finale
App-Modell wurde mit unveränderter Konfiguration auf 2015–2019 trainiert,
versioniert und in die getestete Streamlit-Anwendung integriert. Handout und
Vortragsfolien liegen im Repository. Ausstehend ist nur die einmalige
Aktivierung in Streamlit Community Cloud.**
