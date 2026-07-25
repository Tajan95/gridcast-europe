# C-Testreports

Diese Dateien wurden durch
[`notebooks/03_conclude_compare.ipynb`](../../notebooks/03_conclude_compare.ipynb)
erzeugt.

- `c_conclusion.json`: eingefrorene Spezifikation, Testmetriken,
  Hypothesenentscheidung und Metadaten des finalen App-Modells
- `test_model_comparison.csv`: endgültiger Vergleich der beiden Baselines und
  des ausgewählten HGB-Modells auf 2019
- `test_metrics_by_country.csv`: Pflichtmetriken je Land und Testmodell
- `validation_test_generalization.csv`: Vergleich der Ergebnisse 2018 und 2019
- `test_diagnostics_by_hour.csv`: HGB-Fehler nach Land und lokaler Stunde
- `test_diagnostics_by_season.csv`: HGB-Fehler nach Land und Saison
- `test_diagnostics_by_month.csv`: HGB-Fehler nach Land und Monat

Die Modellkonfiguration wurde vor Öffnung des Testjahres in A³ festgelegt.
2019 wurde nicht für erneute Feature-, Modell- oder Hyperparameterentscheidungen
verwendet.
