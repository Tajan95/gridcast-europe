# Kandidatenkarte: Open Power System Data – Time Series

**Status:** A – verifizierte Kernquelle  
**Rolle:** Zielvariable und historische Lastfeatures

## Anbieter und Zugriff

- Anbieter: Open Power System Data (OPSD)
- Datenseite: https://data.open-power-system-data.org/time_series/
- Version: `2020-10-06` (auf der Plattform als letzte Paketversion ausgewiesen)
- DOI: https://doi.org/10.25832/time_series/2020-10-06
- Formate: CSV, XLSX, SQLite und ZIP-Paket
- Attribution: OPSD nennt eine konkrete Zitierempfehlung; genaue Lizenzbedingungen der Primärquellen vor Veröffentlichung nochmals prüfen

## Inhalt und Granularität

- Last, Wind, Solar und Preise
- stündliche Auflösung; teilweise zusätzliche 15-Minuten-Dateien
- aggregiert nach Land, Regelzone oder Gebotszone
- Paketumfang: 32 europäische Länder
- Hauptzeitraum der ENTSO-E-basierten Paketversion: 2015 bis Mitte 2020

## Relevante Variablen

- `utc_timestamp`
- länderspezifische `*_load_actual_entsoe_transparency` als Ziel
- veröffentlichte Day-ahead-TSO-Prognosen nur als optionaler externer Benchmark, nicht als Eingabefeature des eigenen Modells

## Beobachtungseinheit und Join

- Beobachtungseinheit: `Land × UTC-Stunde`
- Join mit OPSD Weather Data: ISO-Ländercode plus `utc_timestamp`

## Gemessenes Volumen

- Modellfenster 2015–2019: 43.824 mögliche Stunden je Land
- drei Kernländer: 131.472 mögliche Länder-Stunden
- 31 fehlende Lastwerte: DE 0, FR 30, PL 1
- nach Zielbereinigung: 131.441 nutzbare Länder-Stunden

## Risiken

- Variablen und Vollständigkeit unterscheiden sich je Land
- Vermischung von Land, Regelzone und Gebotszone vermeiden
- Sommerzeit und lokale Kalenderfeatures aus UTC sauber ableiten
- veröffentlichte TSO-Prognosen würden bei Nutzung als Feature die Eigenleistung des Modells verwischen
- 2020 enthält COVID-Strukturbrüche und ist wegen Wetterabdeckung nicht als normaler Pflicht-Testzeitraum vorgesehen

## Eignung

- Kernmodell: sehr hoch
- Zeitprognose: sehr hoch
- langfristige Szenarioanalyse: nur als historisches Referenzprofil

## Abgeschlossene Verifikation

1. `time_series_60min_singleindex.csv` selektiv und reproduzierbar eingelesen.
2. UTC-Zeitachse ist sortiert, duplikatfrei und stündlich lückenlos.
3. Nationale Zielspalten für DE, FR und PL eindeutig ausgewählt.
4. Gemeinsame Wetterabdeckung 2015–2019 bestätigt.
5. Fehlende Zielwerte werden ohne Imputation entfernt.

## Urteil

**Geeignet und als Kernquelle bestätigt.** Verbindliche Kernländer sind DE, FR und PL.

