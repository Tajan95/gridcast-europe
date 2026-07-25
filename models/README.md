# Modellartefakte

Die A³-Phase erzeugt lokal:

```text
models/gridcast_a3_train_2015_2017.joblib
```

Das Artefakt enthält die vollständige ausgewählte Inferenzpipeline:

- länderweise Zielskalierung,
- One-Hot-Kodierung des Landes,
- Kalender-, Feiertags- und Wetterfeatures,
- trainiertes Histogram-Gradient-Boosting-Modell.

Die Binärdatei wird gemäß `.gitignore` nicht versioniert. Reproduzierbar
versioniert werden stattdessen:

- Trainings- und Auswahlcode in `src/gridcast/modeling.py`,
- das ausgeführte A³-Notebook,
- die eingefrorene Konfiguration unter `reports/a3/a3_selection.json`,
- Validierungsmetriken als CSV.

Nach der C-Phase wird ein endgültiges App-Modell auf dem dafür festgelegten
Gesamtzeitraum erzeugt.
