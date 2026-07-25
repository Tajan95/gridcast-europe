# C – Conclude & Compare

**Status:** abgeschlossen  
**Stand:** 25.07.2026

## Ausführbares Hauptdokument

- [`notebooks/03_conclude_compare.ipynb`](../../../notebooks/03_conclude_compare.ipynb)

Das vollständig ausgeführte Notebook übernimmt die in A³ eingefrorene
HGB-Konfiguration, refittet Modell und Baselines auf 2015–2018 und bewertet
sie auf dem zuvor vollständig zurückgehaltenen Jahr 2019. Anschließend wird
dieselbe Konfiguration als App-Modell auf 2015–2019 trainiert.

## Methodische Testöffnung

Vor der C-Phase standen fest:

- Modellfamilie: Histogram Gradient Boosting,
- Featuregruppe: Kalender, nationale Feiertage und Wetter,
- länderweise Zielskalierung,
- sämtliche Hyperparameter,
- Makro-nMAE als Primärmetrik,
- Kalender-Baseline als Referenz für H3,
- mindestens 5 % relative Fehlerreduktion als praktisches Ziel.

Die Spezifikation stammt unverändert aus
[`reports/a3/a3_selection.json`](../../../reports/a3/a3_selection.json).
Ihr SHA-256-Fingerabdruck wird im C-Report gespeichert. Das Testjahr wurde
weder für eine erneute Auswahl noch für ein nachträgliches Tuning verwendet.

## Testaufbau

| Block | Zeitraum | Verwendung |
|---|---|---|
| Refit | 2015–2018 | Baselines, Zielskalierung und HGB-Modell lernen |
| Test | 2019 | einmalige abschließende Out-of-sample-Bewertung |

Der historische Backtest verwendet das beobachtete OPSD-Reanalysewetter von
2019. Das ist keine reale Wettervorhersage.

## Endgültige Testergebnisse 2019

| Modell | Makro-nMAE | MAE | RMSE | R² | Verbesserung gegenüber Kalender |
|---|---:|---:|---:|---:|---:|
| Ländermittelwert | 15,64 % | 6.862,2 MW | 8.861,0 MW | 0,7807 | −220,8 % |
| Kalender-Baseline | 4,88 % | 2.125,4 MW | 3.118,7 MW | 0,9728 | Referenz |
| **HGB Kalender + Feiertag + Wetter** | **2,71 %** | **1.157,8 MW** | **1.663,4 MW** | **0,9923** | **+44,5 %** |

Das ausgewählte Modell senkt den primären Fehler gegenüber der
Kalender-Baseline um **44,5 %**. Damit sind sowohl der grundsätzliche
ML-Mehrwert als auch der vorab definierte praktische Zielwert von mindestens
5 % bestätigt.

### HGB-Testgüte je Land

| Land | MAE | RMSE | nMAE | sMAPE | R² |
|---|---:|---:|---:|---:|---:|
| DE | 1.396,6 MW | 1.920,3 MW | 2,49 % | 2,57 % | 0,9623 |
| FR | 1.553,7 MW | 2.042,1 MW | 2,91 % | 2,88 % | 0,9672 |
| PL | 523,3 MW | 666,0 MW | 2,71 % | 2,79 % | 0,9551 |

Frankreich besitzt 2019 den höchsten relativen HGB-Fehler. Der Unterschied
zwischen den Ländern bleibt durch die Makroauswertung sichtbar.

## Validierung und Test

| Modell | Makro-nMAE 2018 | Makro-nMAE 2019 |
|---|---:|---:|
| Ländermittelwert | 15,97 % | 15,64 % |
| Kalender-Baseline | 5,76 % | 4,88 % |
| HGB Kalender + Feiertag + Wetter | 3,31 % | 2,71 % |

Die Modellrangfolge bleibt stabil. Das zusätzliche Trainingsjahr geht im
vorliegenden Experiment mit einem niedrigeren Testfehler einher. Daraus folgt
jedoch kein allgemeines Gesetz, dass jedes weitere Jahr den Fehler monoton
senken muss: Refit-Fenster und Schwierigkeit des Zieljahres ändern sich
gleichzeitig.

## Hypothesenabschluss

| Hypothese | Entscheidender Befund | Status |
|---|---|---|
| H1 – Daten-Eignung | 131.441 nutzbare Länder-Stunden und vollständige Wetterfeatures | in U bestätigt |
| H2 – Kalenderstruktur | Kalender-Baseline verbessert Test-Makro-nMAE um 68,8 % gegenüber dem Ländermittel | bestätigt |
| H3 – ML-Mehrwert | HGB verbessert Test-Makro-nMAE um 44,5 % gegenüber der Kalender-Baseline | bestätigt |
| H4 – Nichtlinearität | HGB schlägt Ridge auf der Validierung 2018 | in A³ bestätigt |
| H5 – Wettermehrwert | Wetter-Ablation senkt den Validierungsfehler | in A³ bestätigt |

## Qualitative Modellwahl

| Kriterium | Kalender-Baseline | Ridge | ausgewähltes HGB |
|---|---|---|---|
| Interpretierbarkeit | hoch | mittel bis hoch | mittel |
| Wetterreaktion | nein | ja | ja |
| Nichtlineare Interaktionen | nein | nein | ja |
| Wartungsaufwand | gering | gering | moderat |
| CPU-Eignung | sehr gut | sehr gut | sehr gut |
| Rolle | starke Referenz | linearer A³-Vergleich | finales Modell |

Der geringeren unmittelbaren Interpretierbarkeit des HGB steht ein deutlich
niedrigerer Fehler gegenüber. Der Refit auf 105.166 Länder-Stunden benötigt in
der geprüften Umgebung rund 4,2 Sekunden; die Vorhersage aller 26.275
Testzeilen rund 0,07 Sekunden. Eine GPU ist nicht erforderlich.

## Finales App-Modell

Nach Abschluss der unabhängigen Testbewertung wurde dieselbe Konfiguration auf
allen **131.441** nutzbaren Länder-Stunden von 2015–2019 trainiert:

```text
models/gridcast_final_2015_2019.joblib
```

Das lokale Artefakt wurde nach dem Speichern in einem frischen Ladevorgang
verifiziert. Es wird nicht versioniert, ist aber durch Code, Auswahlreport und
C-Notebook reproduzierbar. Da 2019 im finalen Fit enthalten ist, besitzt dieses
App-Modell keine zusätzliche unabhängige Testkennzahl. Maßgeblich bleibt die
zuvor dokumentierte C-Auswertung.

## Grenzen

- beobachtetes Reanalysewetter ist keine zukünftige Wettervorhersage,
- regionale deutsche Feiertage sind nicht separat modelliert,
- März und Frühling 2019 zeigen insbesondere für Frankreich erhöhte Fehler,
- langfristige Nachfrageänderungen werden als transparente Szenarioannahmen
  behandelt und nicht als durch den Backtest bewiesene Kausalprognosen,
- das Ergebnis gilt für DE, FR und PL sowie die OPSD-Periode 2015–2019.

## Reproduzierbare Artefakte

- [`reports/c/c_conclusion.json`](../../../reports/c/c_conclusion.json)
- [`reports/c/test_model_comparison.csv`](../../../reports/c/test_model_comparison.csv)
- [`reports/c/test_metrics_by_country.csv`](../../../reports/c/test_metrics_by_country.csv)
- [`reports/c/validation_test_generalization.csv`](../../../reports/c/validation_test_generalization.csv)
- [`reports/c/test_diagnostics_by_hour.csv`](../../../reports/c/test_diagnostics_by_hour.csv)
- [`reports/c/test_diagnostics_by_season.csv`](../../../reports/c/test_diagnostics_by_season.csv)
- [`reports/c/test_diagnostics_by_month.csv`](../../../reports/c/test_diagnostics_by_month.csv)

## Nächster Schritt

Die K-Phase integriert das finale Modell in die Streamlit-App, implementiert
die getrennte Szenariologik und bereitet Handout sowie Präsentation vor.
