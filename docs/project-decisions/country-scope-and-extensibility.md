# Länder-Scope und Erweiterbarkeit

**Stand:** 25.07.2026  
**Status:** beschlossen

## Entscheidung

Der verbindliche Prüfungs-Scope umfasst:

- Deutschland (`DE`)
- Frankreich (`FR`)
- Polen (`PL`)

Diese Auswahl ist keine technische Begrenzung. Die Datenpipeline ist
konfigurationsgetrieben aufgebaut, sodass weitere Länder später ergänzt werden
können, ohne Import, Long-Format-Transformation, Join oder Feature Engineering
neu zu schreiben.

## Warum nicht sofort alle 27 Länder?

Die reine Verarbeitung wächst ungefähr linear:

- mehr einzulesende Spalten,
- mehr Länder-Stunden,
- längere Trainingszeit,
- mehr Modellvorhersagen.

Der fachliche Aufwand wächst jedoch teilweise stärker als linear:

1. **Geografische Vergleichbarkeit:** Nationale Lastreihen müssen von
   Regelzonen, Gebotszonen und Teilnetzen unterschieden werden.
2. **Datenqualität:** Missingness, Lückenintervalle und mögliche
   Definitionswechsel müssen je Land geprüft werden.
3. **Zeitzonen und Sommerzeit:** Kalenderfeatures benötigen die korrekte
   länderspezifische Lokalzeit.
4. **Feiertage:** Eine spätere Feiertagslogik ist landesspezifisch.
5. **Plausibilitätsprüfung:** Statistische Extremwerte können reale nationale
   Besonderheiten oder Messfehler sein.
6. **Modellinterpretation:** Fehler müssen mindestens nach Land, Tageszeit und
   Saison erklärt werden.
7. **Modellkomplexität:** Mit heterogeneren Ländern werden Länderinteraktionen
   und gegebenenfalls länderspezifische Modelle relevanter.

Bei 27 Ländern würden nicht nur neunmal so viele Zeilen wie bei drei Ländern
entstehen. Es müssten auch 27 eigenständige Qualitätssicherungen und
Ergebnisinterpretationen prüfungsfest dokumentiert werden.

## Warum DE, FR und PL?

Im gemeinsamen Fenster 2015–2019 ergeben sich:

| Land | Mögliche Stunden | Fehlende Lastwerte | Vollständigkeit |
|---|---:|---:|---:|
| Deutschland | 43.824 | 0 | 100,000 % |
| Frankreich | 43.824 | 30 | 99,932 % |
| Polen | 43.824 | 1 | 99,998 % |

Die Kombination bietet:

- 131.441 nutzbare Länder-Stunden,
- vollständige Wetterfeatures,
- einen gemeinsamen mitteleuropäischen Sommerzeitrhythmus,
- drei unterschiedlich große und strukturierte Stromsysteme,
- einen beherrschbaren Umfang für Modellvergleich und Fehleranalyse.

## Technische Erweiterungslogik

Die zentrale Länderdefinition liegt in `src/gridcast/config.py`. Ein Land wird
erst nach fachlicher Prüfung in `COUNTRY_REGISTRY` aufgenommen. Danach nutzt die
Pipeline denselben Code für:

- selektiven Spaltenimport,
- Umformung in `Land × UTC-Stunde`,
- Last-/Wetter-Join,
- länderspezifische Lokalzeit,
- Kalender- und Temperaturfeatures,
- chronologischen Split,
- Qualitätskennzahlen,
- klimatologische Monats-Stunden-Profile.

Die Erweiterung bleibt damit modular, aber bewusst nicht unkontrolliert.

## Europa-Karte in Streamlit

Eine anklickbare Europa-Karte ist nicht an ein Modell mit allen 27 Ländern
gebunden. Sie kann alle bereits freigegebenen Länder anzeigen; nicht
modellierte Länder bleiben visuell deaktiviert oder erhalten einen klaren
Hinweis.

Für den MVP genügt daher eine Karte beziehungsweise Auswahl mit DE, FR und PL.
Weitere Länder können nach demselben Freigabeprozess ergänzt werden, falls nach
dem funktionierenden Kern noch Zeit bleibt.

## Erweiterungskriterium

Ein zusätzliches Land wird nur aktiviert, wenn:

1. eine eindeutige nationale Lastreihe existiert,
2. Last und Wetter 2015–2019 auf UTC-Stundenebene 1:1 joinbar sind,
3. die Zielvariable hinreichend vollständig ist,
4. keine ungeklärten Niveau- oder Definitionsbrüche bestehen,
5. Zeitzone und gegebenenfalls Feiertagslogik dokumentiert sind,
6. das Modell für dieses Land separat evaluiert und interpretiert wird.
