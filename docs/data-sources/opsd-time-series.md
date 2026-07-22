# Kandidatenkarte: Open Power System Data – Time Series

**Status:** A – priorisierte Kernquelle  
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

## Erwartetes Volumen

- ein vollständiges Land über fünf Jahre: ungefähr 43.800 Stunden
- drei vollständige Länder: ungefähr 131.400 Länder-Stunden vor Missingness und Lag-Verlusten
- diese Werte sind rechnerische Größenordnungen, keine bereits gemessenen Zeilenzahlen

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

## Nächster Verifikationstest

1. `time_series_60min_singleindex.csv` reproduzierbar herunterladen.
2. Für alle länderweiten Lastspalten Zeitraum, Missingness und längste zusammenhängende Sequenz messen.
3. Drei Länder nur nach gemeinsamer Wetterabdeckung auswählen.
4. Prüfen, ob 2015–2019 vollständig genug für den geplanten Split sind.

## Vorläufiges Urteil

**Geeignet und verbindlich priorisiert.** Die konkrete Länderauswahl bleibt datenabhängig.

