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

Das A³-Zwischenmodell wird gemäß `.gitignore` nicht versioniert. Reproduzierbar
versioniert werden stattdessen:

- Trainings- und Auswahlcode in `src/gridcast/modeling.py`,
- das ausgeführte A³-Notebook,
- die eingefrorene Konfiguration unter `reports/a3/a3_selection.json`,
- Validierungsmetriken als CSV.

Die C-Phase refittet die eingefrorene Konfiguration zunächst auf 2015–2018 und
bewertet sie auf dem unangetasteten Testjahr 2019. Erst nach Abschluss dieser
Auswertung entsteht lokal das endgültige App-Modell:

```text
models/gridcast_final_2015_2019.joblib
```

Es verwendet dieselbe HGB-Konfiguration und lernt aus allen 131.441 nutzbaren
Länder-Stunden von 2015–2019. Das Artefakt wurde nach dem Speichern erfolgreich
neu geladen und für Vorhersagen verwendet.

Da 2019 im finalen Fit enthalten ist, besitzt dieses App-Modell keine neue
unabhängige Testkennzahl. Die unverfälschte Generalisierungsaussage stammt aus
der vorherigen C-Auswertung mit Refit 2015–2018 und Test 2019.

Für das öffentliche Streamlit-Deployment wird ausschließlich dieses finale,
verifizierte App-Modell versioniert. Mit **1.939.407 Byte** liegt es deutlich
unterhalb der GitHub-Dateigrenze. Seine Integrität ist über folgende Prüfsumme
kontrollierbar:

```text
SHA-256
61526739582848fbe829cdd0a1328e1e7a247dc96f31003c19e95d2071567392
```

`joblib`-Dateien dürfen nur aus vertrauenswürdigen Quellen geladen werden, da
das Format beim Deserialisieren Python-Code ausführen kann. Die App lädt
ausschließlich das in diesem Repository veröffentlichte und per SHA-256
dokumentierte Artefakt.

Zusätzlich reproduzierbar versioniert werden:

- das ausgeführte C-Notebook,
- die unveränderte A³-Spezifikation,
- die C-Metriken und Metadaten unter `reports/c/`,
- die vollständige Modellpipeline in `src/gridcast/modeling.py`.
