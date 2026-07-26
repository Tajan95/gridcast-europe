# Dokumentation der KI-Nutzung

**Stand:** 26.07.2026
**Projekt:** GridCast Europe  
**Modul:** Data Analytics und Big Data

## Zweck und System

Generative KI wurde als dialogischer Arbeits-, Recherche-, Erklärungs-,
Programmier- und Redaktionsassistent eingesetzt. Verwendet wurden ChatGPT und
Codex von OpenAI. KI-Ausgaben wurden nicht ungeprüft als fachlich korrekt
vorausgesetzt.

## Tatsächliche Nutzung

| Bereich | Unterstützung durch KI | Menschliche Prüfung und Entscheidung |
|---|---|---|
| Themenfindung und Scope | Vergleich möglicher Fragestellungen; Formulierung von Forschungsfrage und Hypothesen | Auswahl von GridCast, Ländern, Pflichtumfang und Erfolgsziel |
| Datenquellen und Datenphase | Recherche öffentlicher Quellen; Entwurf von Import-, Join-, Qualitäts- und EDA-Schritten | Prüfung der realen OPSD-Daten, Variablen, Lücken und Visualisierungen |
| Modellierung | Vorschläge für chronologischen Split, Baselines, Features, Modelle, Hyperparameter und Metriken | Ausführung der Experimente; Einfrieren der Gewinnerkonfiguration vor dem Test |
| Evaluation | Berechnungsvorschläge, Diagnosen nach Land und Zeit sowie Interpretation der Ergebnisse | einmalige Öffnung des Testjahres; Plausibilitätsprüfung und fachliches Fazit |
| App und Szenarien | Entwurf der Streamlit-Struktur, Szenariorechnung und Extremzustandskennzahl | Abgrenzung von Backtest, Szenario und Blackout-Aussagen; Bedien- und Ergebnisprüfung |
| Code und Tests | Implementierungshilfe, Fehlersuche, Refactoring und Testentwürfe | lokale Ausführung, Kontrolle der Artefakte und Freigabe der Änderungen |
| Wissenstransfer | sprachliche und visuelle Überarbeitung von README, Handout, Folien und Sprechtext | Auswahl der Aussagen, Nachvollziehen der Methodik und Vorbereitung des Referats |

## Verantwortungsabgrenzung

Beim Studierenden verbleiben insbesondere:

- Auswahl und Eingrenzung der Fragestellung,
- Prüfung der Datenquellen und ihrer Eignung,
- Ausführung und Kontrolle der Analysen,
- Bewertung und Interpretation der Ergebnisse,
- Entscheidung über Modelle, Features und Darstellungen,
- Quellenprüfung und Kennzeichnung fremder Inhalte,
- Fähigkeit, Vorgehen, Code, Grenzen und Ergebnisse selbst zu erklären.

## Qualitätssicherung

KI-gestützte Ergebnisse wurden je nach Inhalt kontrolliert durch:

- Abgleich mit Primärquellen und offizieller Dokumentation,
- reproduzierbare Datenimporte und gespeicherte Reports,
- Ausführung automatisierter Tests,
- Plausibilitätskontrolle von Formeln, Daten und Kennzahlen,
- Vergleich mehrerer Modelle mit zwei Baselines,
- chronologische Trennung von Training, Validierung und Test,
- manuelle Prüfung von Notebook-, App-, Handout- und Foliendarstellung.

## Änderungsprotokoll

| Datum | Ergänzung |
|---|---|
| 23.07.2026 | Datei angelegt und bisherige Nutzung dokumentiert |
| 25.07.2026 | Tatsächliche Nutzung in U-, A³-, C- und K-Phase ergänzt; Planungsabschnitt abgeschlossen |
| 26.07.2026 | App-Feinschliff, gekoppelten Zukunftspfad, Artefaktabgleich sowie abschließende Konsistenz- und Präzisionsprüfung dokumentiert |
