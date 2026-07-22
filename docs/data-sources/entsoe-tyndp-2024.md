# Kandidatenkarte: ENTSO-E/ENTSOG – TYNDP 2024 Scenarios

**Status:** B – optionale Erweiterung  
**Rolle:** offizielle langfristige Nachfrage- und Energiesystempfade

## Anbieter und Zugriff

- Anbieter: ENTSO-E und ENTSOG
- Downloadseite: https://2024.entsos-tyndp-scenarios.eu/download/
- Zugriff: kostenlose öffentliche Downloads
- Lizenz: Creative Commons Attribution 4.0; Attribution „TYNDP 2024 Scenarios“

## Inhalt

Die Plattform bietet unter anderem:

- Nachfrage-Szenarien
- Demand Profiles
- Versorgungs- und Modellierungsinputs
- Referenznetz und Investitionskandidaten
- Szenarioergebnisse für 2030, 2035, 2040 und 2050, abhängig vom Paket
- mehrere Klimajahre für bestimmte Modellierungsergebnisse

## Mögliche Nutzung

- strukturellen Nachfragepfad \(g(y)\) für Länder oder Szenarien ableiten
- App-Szenarien mit offiziellen statt frei erfundenen Wachstumsannahmen vorbelegen
- langfristige Einordnung der eigenen kurzfristigen ML-Prognose

## Beobachtungseinheit und Join

- variiert je Download: Land/Zone × Szenario × Zieljahr, teilweise stündliche Nachfrageprofile
- Join mit GridCast erfordert Mapping von TYNDP-Zonen zu OPSD-Ländercodes sowie Einheitenprüfung

## Risiken

- Szenariodaten sind keine gemessenen Labels und gehören nicht in das Training des historischen Day-ahead-Modells
- viele Dateien und Modellierungsebenen erhöhen den Scope schnell
- 2024-Szenarien sind extern modellierte Zukunftsannahmen, keine von GridCast selbst gelernten Trends
- Nachfragepfade, Referenzjahr und Klimaannahmen müssen exakt aus der gewählten Datei zitiert werden

## Eignung

- Kernmodell: nicht notwendig
- strukturierter Zukunftsregler: hoch
- Netzausbau- oder Blackoutmodell: trotz verfügbarer Netzdaten außerhalb des Scopes

## Nächster Verifikationstest

1. finalen Demand-Scenario-Download öffnen und Schema dokumentieren.
2. prüfen, ob Deutschland, Frankreich und weitere OPSD-Kandidaten auf konsistenter Ebene enthalten sind.
3. jährliche Nachfrageänderung relativ zu einem klaren Referenzjahr berechnen.
4. nur einen transparenten Pfad in die App übernehmen, falls Aufwand gering bleibt.

## Vorläufiges Urteil

**Gute offizielle Szenarioquelle, aber erst nach dem ML-Kern.**

