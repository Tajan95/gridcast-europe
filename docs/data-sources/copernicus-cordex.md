# Kandidatenkarte: Copernicus CDS – CORDEX

**Status:** B – optionale Erweiterung  
**Rolle:** externe Klimaprojektionen für benannte Temperaturszenarien

## Anbieter und Zugriff

- Anbieter: Copernicus Climate Change Service / Climate Data Store
- Datenseite: https://cds.climate.copernicus.eu/datasets/projections-cordex-domains-single-levels
- Zugriff: Webformular und CDS API; Registrierung erforderlich
- Format: NetCDF4
- Nutzung: weitgehend auch kommerziell möglich; modellspezifische Ausnahmen und CORDEX-Lizenz beachten

## Inhalt und Granularität

- regionale Klimamodell-Ensembles
- historische, Evaluations- und RCP-Szenarioexperimente
- RCP 2.6, 4.5 und 8.5
- europäische Domäne mit bis zu 0,11° × 0,11°
- RCP-Abdeckung typischerweise etwa 2006–2100/2101
- zeitliche Auflösungen je nach Variable: 3-stündlich, 6-stündlich, täglich, monatlich oder saisonal
- relevantes Merkmal: 2-m-Temperatur

## Beobachtungseinheit und notwendige Aufbereitung

- ursprüngliche Einheit: `Modell × Ensemble × Rasterzelle × Zeitpunkt`
- für GridCast erforderlich: räumliche Aggregation auf Land und zeitliche Anpassung an das verwendete Lastprofil
- kein einfacher CSV-Join

## Mögliche Nutzung

- landesspezifisches `ΔT` gegenüber einer Referenzperiode ableiten
- Klimapfad als optionalen App-Regler verwenden
- Modellensembles zur Darstellung von Szenariospannen nutzen

## Risiken

- hoher Download-, NetCDF- und Geodatenaufwand
- Projektionen sind Szenarien mit Modell- und natürlicher Unsicherheit, keine exakten Wettervorhersagen
- CMIP5/RCP-Pfade müssen fachlich korrekt benannt und dürfen nicht mit SSPs vermischt werden
- räumliche Aggregationsgewichte und Referenzperiode müssen dokumentiert werden
- für das Kernmodell nicht erforderlich

## Eignung

- Kernmodell: niedrig
- optionale zweite Ebene: hoch, aber aufwendig
- Prüfungstermin in sechs Tagen: nur nach vollständig funktionierendem Kern aufnehmen

## Nächster Verifikationstest

1. Für genau ein Land, eine Variable und ein RCP-Szenario einen kleinen API-Download testen.
2. monatliche oder saisonale 2-m-Temperatur auf Landesmittel aggregieren.
3. `ΔT` gegenüber einer klaren Referenzperiode berechnen.
4. Aufwand gegen einen einfachen manuellen `ΔT`-Regler abwägen.

## Vorläufiges Urteil

**Fachlich geeignet, aber kein Pflichtbestandteil.** Zunächst nur Kandidatenstatus.

