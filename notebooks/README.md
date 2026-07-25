# Notebooks

Verbindliche Reihenfolge:

1. [`00_question_gridcast.ipynb`](00_question_gridcast.ipynb)  
   Q-Phase: Forschungsfragen, Hypothesen und Experimentdesign
2. [`01_data_import_merge_eda.ipynb`](01_data_import_merge_eda.ipynb)  
   U-Phase: Import, Qualitätsprüfung, Join, Feature Engineering und EDA
3. [`02_a3_model_development.ipynb`](02_a3_model_development.ipynb)  
   A³-Phase: Baselines, Feature-Ablationen, Modell- und Hyperparameterwahl
4. [`03_conclude_compare.ipynb`](03_conclude_compare.ipynb)  
   C-Phase: Refit, einmalige Testauswertung 2019 und Schlussfolgerung
Die K-Phase benötigt kein zusätzliches Pflichtnotebook. Sie überführt die
geprüften Notebook-Ergebnisse in `streamlit_app/`, kompakte Deployment-Daten,
das finale Modell, Handout und Präsentation. Ihr reproduzierbarer
Erzeugungsschritt liegt unter `scripts/build_k_artifacts.py`.

Wiederverwendbare Funktionen liegen unter `src/gridcast/`. Die Notebooks
orchestrieren diese Bausteine und speichern Erklärungen, Tabellen und
Diagramme als nachvollziehbaren Ergebnisbericht.
