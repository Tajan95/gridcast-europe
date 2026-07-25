# Q – Question

**Status:** abgeschlossen  
**Stand:** 25.07.2026

## Ausführbares Hauptdokument

- [`notebooks/00_question_gridcast.ipynb`](../../../notebooks/00_question_gridcast.ipynb)

Das Notebook dokumentiert Forschungsfragen, Zielgruppen, Hypothesen,
Entscheidungsregeln, Erfolgsmetriken, Daten- und Evaluationsplan, Leakage-Schutz,
App-Konzept sowie Risiken und Grenzen.

## Transparenz zum Projekt-Pivot

Das ursprüngliche Q-Dokument gehörte zur verworfenen WasteWise-Idee. Der
Projekt-Pivot zu GridCast Europe wurde am 22.07.2026 beschlossen. Das
GridCast-Q-Notebook wurde am 25.07.2026 nachgezogen, nachdem die neue
Forschungsrichtung bereits im Repository festgelegt und die Datenpipeline
geprüft worden war.

Das Notebook kennzeichnet diese Reihenfolge ausdrücklich:

- Die WasteWise-Idee wird nicht als GridCast-Vorarbeit ausgegeben.
- Gründe und Zeitpunkt des Pivots bleiben nachvollziehbar.
- Ergebnisse der U-Phase erscheinen nur als nachgelagerte Rückmeldung.
- Hypothesen werden nicht passend zu späteren Modellresultaten umformuliert.
- Das Testjahr 2019 bleibt bis zur C-Phase unangetastet.

## Forschungsfragen

Primärfrage:

> Wie genau lässt sich die stündliche Stromlast ausgewählter europäischer
> Länder anhand historischer Last-, Wetter- und Kalenderdaten für einen
> chronologisch späteren, vollständig zurückgehaltenen Zeitraum
> prognostizieren?

Erweiterte Streamlit-Frage:

> Wie verändert sich ein aus historischen Mustern abgeleitetes Lastprofil für
> einen frei wählbaren Zukunftszeitpunkt unter klimatologischen und
> strukturellen Szenarioannahmen?

## Hypothesen

| ID | Kurzfassung | Prüfphase |
|---|---|---|
| H1 | Last und Wetter sind für mindestens drei Länder stündlich 1:1 joinbar. | U |
| H2 | Die Kalender-Baseline ist genauer als der länderspezifische Mittelwert. | A³/C |
| H3 | Das finale ML-Modell ist genauer als die Kalender-Baseline. | C |
| H4 | Gradient Boosting bildet nichtlineare Zusammenhänge besser ab als regularisierte lineare Regression. | A³ |
| H5 | Wetterfeatures verbessern ein vergleichbares Kalender-Länder-Modell. | A³ |

Alle Hypothesen sind ergebnisoffen. Ein negatives Ergebnis wird nicht
nachträglich umgedeutet.

## Primäres Erfolgskriterium

Die zentrale Auswahl- und Vergleichsmetrik ist der länderweise normalisierte
und anschließend gleichgewichtet gemittelte MAE (**Makro-nMAE**).

- formaler ML-Mehrwert: Makro-nMAE unter der Kalender-Baseline,
- praktisches Ziel: mindestens 5 % relative Verbesserung,
- zusätzliche Pflichtkennzahlen: MAE, RMSE sowie Fehler nach Land, Tageszeit
  und Saison,
- ergänzende Kennzahlen: sMAPE und R².

Das 5-%-Ziel ist ein praktischer Zielwert. Bereits jede positive Verbesserung
belegt formal einen zusätzlichen ML-Mehrwert; bleibt sie aus, wird H3
verworfen.

## Verbindlicher Evaluationsplan

- Training: 2015–2017
- Validierung: 2018
- Test: 2019

Preprocessing, Baselines und Modelle werden nur auf dem Training fitten.
Features, Modellklasse und Hyperparameter werden ausschließlich anhand von 2018
gewählt. Die eingefrorene Konfiguration wird in der C-Phase genau einmal auf
2019 bewertet.

## Verbindliche Grundlagen

- [Project Scope und Forschungsfragen](../../../docs/project-decisions/project-scope.md)
- [Modell- und Szenariodesign](../../../docs/project-decisions/model-and-scenario-design.md)
- [Extremzustandskennzahl](../../../docs/project-decisions/extreme-load-state.md)
- [Länder-Scope und Erweiterbarkeit](../../../docs/project-decisions/country-scope-and-extensibility.md)

## Abschluss

Die Q-Phase ist abgeschlossen. Die U-Phase hat H1 bestätigt. Als nächster
Schritt folgen in A³ beide Baselines, mindestens zwei Regressionsmodelle,
Feature-Ablationen und die ausschließlich auf 2018 gestützte Modellwahl.
