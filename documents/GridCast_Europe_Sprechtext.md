# GridCast Europe - Sprechtext

Tajan Biazevic | Matrikelnummer 10234562 | Prüfungsdauer: 10-15 Minuten

## Folie 1

Zeit: ca. 45 Sekunden.

Ich untersuche, wie gut sich stündliche Stromlast in Deutschland, Frankreich und Polen mit Wetter- und Kalenderdaten prognostizieren lässt.

Der Vortrag folgt den fünf QUA3CK-Phasen und endet mit einer einsatzfähigen Streamlit-Anwendung.

## Folie 2

Zeit: ca. 75 Sekunden.

Der Wechsel von WasteWise zu GridCast ist transparent dokumentiert. Entscheidend ist: Forschungsfrage, Länder-Scope, Baselines, primäre Metrik und Zeit-Split wurden vor der finalen Auswertung festgelegt.

Makro-nMAE gewichtet die drei Länder gleich. Die praktische Zielmarke lag bei mindestens fünf Prozent Verbesserung gegenüber der Kalender-Baseline.

Quelle: notebooks/00_question_gridcast.ipynb.

## Folie 3

Zeit: ca. 75 Sekunden.

OPSD-Last- und Wetterdaten wurden in UTC vereinheitlicht und mit lokalen Kalendermerkmalen ergänzt.

Von 131.472 möglichen Länder-Stunden bleiben 131.441. Es gibt keine doppelten Schlüssel und vollständige Wetterfeatures im Modellzeitraum.

Die EDA zeigt klare Tages- und Saisonprofile. Temperatur ist besonders für Frankreich wichtig und wirkt nichtlinear.

Quelle: notebooks/01_data_import_merge_eda.ipynb; Open Power System Data Time Series und Weather Data Packages.

## Folie 4

Zeit: ca. 90 Sekunden.

A³ trennt drei Entscheidungen: Algorithmus, Attribute und Hyperparameter-Ausprägung.

Die Kalender-Baseline erreicht 5,76 Prozent. Ridge kommt auf 4,98 Prozent. Das beste HGB mit Feiertag und Wetter erreicht 3,31 Prozent und verbessert die Kalender-Baseline um 42,5 Prozent.

Die Gewinnerkonfiguration wurde danach eingefroren. 2019 spielte bei dieser Entscheidung keine Rolle.

Quelle: notebooks/02_a3_model_development.ipynb und reports/a3/a3_selection.json.

## Folie 5

Zeit: ca. 75 Sekunden.

Für C wurde exakt die eingefrorene Konfiguration auf 2015 bis 2018 refittet. Danach wurde 2019 genau einmal geöffnet.

Das HGB erreicht 2,71 Prozent Makro-nMAE. Die Kalender-Baseline liegt bei 4,88 Prozent. Das entspricht 44,5 Prozent Verbesserung.

Damit sind die Generalisierungshypothese und das praktische Fünf-Prozent-Ziel klar bestätigt.

Quelle: notebooks/03_conclude_compare.ipynb und reports/c/c_conclusion.json.

## Folie 6

Zeit: ca. 75 Sekunden.

Alle drei Länder liegen unter drei Prozent nMAE. Frankreich ist relativ am schwierigsten; besonders März und Frühling fallen auf.

Der Fehler sinkt von 3,31 Prozent auf der Validierung auf 2,71 Prozent im Test. Das ist ein positiver empirischer Befund, aber kein Beweis, dass jedes weitere Jahr automatisch hilft.

Reanalysewetter ist im Backtest bekannt. Für einen echten operativen Einsatz wären Wetterprognosen und laufendes Monitoring nötig.

Quelle: reports/c/test_metrics_by_country.csv und reports/c/validation_test_generalization.csv.

## Folie 7

Zeit: ca. 75 Sekunden.

Die K-Phase überführt das Projekt in eine Streamlit-Anwendung mit vier klar getrennten Ansichten.

Methodisch wichtig: Der historische Backtest zeigt vorab berechnete C-Prognosen. Das später auf 2015 bis 2019 refittete App-Modell wird nicht verwendet, um 2019 rückwirkend besser aussehen zu lassen.

Die Übersicht nutzt eine interaktive Europakarte. Im Backtest sind Istwert, HGB und die gestrichelte Kalender-Baseline mit exakten Hoverwerten vergleichbar. Die Zukunftsansicht bietet sieben Presets und trennt direkte ML-Eingaben, Strukturannahmen und Auswertung sichtbar voneinander.

Quelle: streamlit_app/app.py und notebooks/04_knowledge_transfer.md.

## Folie 8

Zeit: ca. 90 Sekunden.

Für ein gewähltes Datum werden Kalenderfeatures und ein typisches Wetterprofil aus der Klimatologie 1980 bis 2019 erzeugt. Temperaturabweichung sowie direkte und diffuse Sonneneinstrahlung verändern die Feature-Matrix vor einer erneuten ML-Inferenz.

Nachfrageänderung und zusätzliche Rechenzentrumslast werden danach als explizite Strukturannahmen angewendet.

Das Beispielszenario erhöht die modellierte Spitzenlast um 10,24 Prozent. Es ist keine konkrete Prognose für 2030.

Die sieben Presets sind illustrative Einstiegspunkte. Ein eigener Wetterinputs-Tab stellt das typische und das tatsächlich an das HGB übergebene Temperatur- und Strahlungsprofil gegenüber. Zusätzlich zeigt die App Tagesenergie, Spitzenzeit und Stunden oberhalb der historischen Quantilschwelle; alle Annahmen bleiben manuell veränderbar.

Der Risikoindikator bezeichnet nur die Wahrscheinlichkeit einer historischen nationalen Quantilsüberschreitung, ausdrücklich nicht die Wahrscheinlichkeit eines Blackouts.

Quelle: src/gridcast/scenario.py, src/gridcast/risk.py und reports/k_deployment.json.

## Folie 9

Zeit: ca. 60 Sekunden.

Das finale Joblib-Artefakt ist rund 1,9 Megabyte groß, hat eine feste Prüfsumme und liegt im Repository.

Zwölf Funktionstests bestehen. Zusätzlich laufen alle vier App-Ansichten und die Wetter-Preset-Neuberechnung ohne Ausnahme.

Das Community-Cloud-Deployment läuft stabil unter Python 3.12.13. Durch die Trennung von App- und Entwicklungsabhängigkeiten sank die Cloud-Umgebung von 129 auf 41 Pakete; der frühere native Absturz unter Python 3.14.6 tritt damit nicht mehr auf.

Quelle: reports/k_deployment.json und notebooks/04_knowledge_transfer.md.

## Folie 10

Zeit: ca. 45 Sekunden.

Die Forschungsfrage kann positiv beantwortet werden: Das eingefrorene Modell generalisiert auf 2019 und schlägt die Kalender-Baseline deutlich.

Gleichzeitig begrenzt die Anwendung ihre Aussage: Historischer Backtest und Zukunftsszenario bleiben getrennt, und der Risikoindikator wird nicht als Blackout-Prognose ausgegeben.

Damit sind alle fünf QUA3CK-Phasen mit Code, Notebooks, Reports, Modell, App, Handout und Präsentation abgeschlossen.
