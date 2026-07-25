# A³ – Algorithm Selection, Adapting Features, Adjusting Hyperparameters

**Status:** abgeschlossen  
**Stand:** 25.07.2026

## Ausführbares Hauptdokument

- [`notebooks/02_a3_model_development.ipynb`](../../../notebooks/02_a3_model_development.ipynb)

Das vollständig ausgeführte Notebook dokumentiert Baselines, Feature-Ablationen,
Ridge-Regression, Histogram Gradient Boosting, begrenzte
Hyperparameteroptimierung, Pflichtdiagnostik und das Einfrieren der
Modellkonfiguration.

## Methodische Grenze

A³ verwendet ausschließlich:

- **Training:** 2015–2017
- **Validierung:** 2018

Das Testjahr 2019 wurde weder für Featureentscheidungen noch für
Hyperparameter- oder Modellwahl verwendet. Seine einmalige Auswertung folgt
erst in der C-Phase.

## Baselines

1. **Länderspezifischer Mittelwert**
2. **Kalender-Baseline:** Land × Monat × Tagtyp × lokale Stunde

Der Tagtyp unterscheidet Werktag, Wochenende und nationalen Feiertag. Gruppen
mit weniger als drei Trainingsbeobachtungen nutzen eine dokumentierte
Rückfallhierarchie bis zum Ländermittelwert.

## Modellfamilien

### Ridge-Regression

- interpretierbarer linearer Vergleich,
- One-Hot-Kodierung des Kalendergruppenschlüssels,
- standardisierte numerische Merkmale,
- Regularisierungswerte `0.1`, `1`, `10`, `100`.

### Histogram Gradient Boosting

- nichtlineare Kalender-Wetter-Interaktionen,
- absoluter Fehler als Trainingsverlust,
- zwölf kontrollierte Hyperparameterkombinationen,
- feste Zufallsbasis `random_state=42`.

Beide Modellfamilien lernen eine mit dem länderspezifischen Trainingsmittel
skalierte Zielvariable. Vorhersagen werden anschließend wieder nach MW
zurücktransformiert.

## Feature-Ablationen

Geprüft wurden:

- Kalendermerkmale,
- nationaler Feiertagsindikator,
- Temperatur und nichtlineare Temperaturmerkmale,
- direkte und diffuse horizontale Strahlung.

Feiertags- und Wettermerkmale senkten den Validierungsfehler und wurden deshalb
für das ausgewählte Modell beibehalten. Regionale deutsche Feiertage sind noch
nicht enthalten.

## Validierungsergebnisse 2018

| Modell | Makro-nMAE | MAE | RMSE | R² |
|---|---:|---:|---:|---:|
| Ländermittelwert | 15,97 % | 7.102,5 MW | 9.173,0 MW | 0,7729 |
| Kalender-Baseline | 5,76 % | 2.489,2 MW | 3.607,4 MW | 0,9649 |
| beste Ridge-Regression | 4,98 % | 2.132,0 MW | 2.989,7 MW | 0,9759 |
| HGB Kalender + Feiertag | 4,83 % | 2.175,3 MW | 3.564,8 MW | 0,9657 |
| **HGB Kalender + Feiertag + Wetter** | **3,31 %** | **1.384,2 MW** | **1.898,0 MW** | **0,9903** |

Das ausgewählte HGB-Modell reduziert den Makro-nMAE gegenüber der
Kalender-Baseline um **42,5 %**. Das praktische 5-%-Ziel ist damit auf der
Validierung deutlich erreicht; die endgültige Aussage muss jedoch auf 2019
bestätigt werden.

### Ausgewählte HGB-Konfiguration

| Parameter | Wert |
|---|---:|
| Verlustfunktion | `absolute_error` |
| Lernrate | `0.1` |
| maximale Blattknoten | `127` |
| Iterationen | `300` |
| minimale Beobachtungen pro Blatt | `80` |
| L2-Regularisierung | `1.0` |
| Early Stopping | `False` |
| Random State | `42` |

### Fehler je Land

| Land | MAE | RMSE | nMAE | R² |
|---|---:|---:|---:|---:|
| DE | 1.714,1 MW | 2.154,8 MW | 3,01 % | 0,9523 |
| FR | 1.709,0 MW | 2.324,6 MW | 3,18 % | 0,9619 |
| PL | 730,0 MW | 873,1 MW | 3,74 % | 0,9251 |

Polen besitzt trotz des kleinsten absoluten MW-Fehlers den höchsten relativen
Fehler. Die Makroauswahl verhindert, dass dieser Befund durch die größeren
Stromsysteme verdeckt wird.

## Hypothesenstand

| Hypothese | A³-Status |
|---|---|
| H2 – Kalender-Baseline schlägt Ländermittel | auf 2018 bestätigt |
| H3 – finales ML-Modell schlägt Kalender-Baseline | bis zum Test 2019 offen |
| H4 – nichtlineares Modell schlägt Ridge | auf 2018 bestätigt |
| H5 – Wettermerkmale bringen Zusatznutzen | auf 2018 bestätigt |

## Reproduzierbare Artefakte

- [`reports/a3/a3_selection.json`](../../../reports/a3/a3_selection.json)
- [`reports/a3/validation_model_comparison.csv`](../../../reports/a3/validation_model_comparison.csv)
- [`reports/a3/validation_metrics_by_country.csv`](../../../reports/a3/validation_metrics_by_country.csv)
- [`src/gridcast/modeling.py`](../../../src/gridcast/modeling.py)

Das lokale Binärmodell `models/gridcast_a3_train_2015_2017.joblib` wird gemäß
Repository-Konvention nicht versioniert. Seine vollständige Pipeline und alle
Parameter sind per Code reproduzierbar.

## Nächster Schritt

In der C-Phase wird die eingefrorene Konfiguration auf 2015–2018 refittet und
genau einmal auf 2019 bewertet. Erst dann werden H3 und der endgültige
ML-Mehrwert entschieden.
