# GridCast Europe

**Arbeitstitel:** Machine-learning-based European electricity load forecasting and scenario analysis

Dieses Repository entsteht für das IU-Modul **Data Analytics und Big Data** und folgt dem **QUA³CK-Prozessmodell**. Der Projekt-Pivot von WasteWise auf GridCast Europe wurde am 22.07.2026 beschlossen.

## Forschungsfrage

> Wie genau lässt sich die Stromlast ausgewählter europäischer Länder 24 Stunden im Voraus anhand historischer Last-, Wetter- und Kalenderdaten prognostizieren?

Erweiterte Streamlit-Frage:

> Wie verändert sich das prognostizierte Lastprofil unter unterschiedlichen Temperatur-, Nachfrage- und Rechenzentrumsszenarien?

## Methodischer Kern

- stündliche Beobachtungseinheit `Land × UTC-Stunde`
- drei europäische Länder nach dokumentierter Vollständigkeitsprüfung
- chronologischer Split, vorläufig: Training 2015–2017, Validierung 2018, Test 2019
- Baseline-Modelle: Last vor 24 Stunden und Last vor 168 Stunden
- Vergleichsmodelle: lineare/regularisierte Regression und Gradient Boosting
- Metriken: MAE, RMSE, normalisierter MAE, ergänzend sMAPE und R²
- primäre Mindestanforderung: finales Modell schlägt auf dem unangetasteten Testzeitraum mindestens eine naive Baseline

## Berücksichtigte Faktoren

- Tages- und Wochenzyklen
- Werktage, Wochenenden und optional Feiertage
- Monate und Jahreszeiten
- tatsächliche bzw. im Backtest bekannte Temperatur
- Last vor 24, 48 und 168 Stunden
- vergangenheitsbasierte rollende Mittelwerte, Streuungen und Laständerungen
- optional direkte und diffuse Sonneneinstrahlung

## Zwei Ebenen

1. **Day-ahead-ML-Prognose:** Vorhersage der nächsten 24 Stunden aus zu diesem Zeitpunkt verfügbaren Merkmalen.
2. **Konditionale Szenarioanalyse:** erneute Prognose mit veränderter Temperatur und transparenten externen Nachfrage-/Rechenzentrumsannahmen.

Die zweite Ebene ist eine *Was-wäre-wenn*-Analyse. Sie wird nicht als autonome, kausale Lastprognose bis 2030 oder 2050 ausgegeben.

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
src/gridcast/                wiederverwendbarer Python-Code
streamlit_app/              interaktive Anwendung
tests/                      automatisierte Tests
```

Große Daten- und Modelldateien werden nicht in Git versioniert. Download und Aufbereitung sollen reproduzierbar per Code erfolgen.

## Status

Aktueller Stand: **Scope festgelegt; Datenquellen verifiziert; reproduzierbarer Datenimport und Vollständigkeitsprüfung als nächster Schritt.**
