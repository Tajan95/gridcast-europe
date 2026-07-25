# App-Daten

Dieser Ordner enthält ausschließlich kompakte, aus den geprüften
Projektartefakten abgeleitete Deployment-Daten:

- `backtest_2019.csv.gz`: vorab berechnete Out-of-sample-Prognosen der
  C-Phase (Refit 2015–2018, Test 2019),
- `weather_climatology_1980_2019.csv.gz`: Median-Wetterprofil nach
  `Land × Monat × lokale Stunde`,
- `risk_calibration_2018.npz`: länderspezifische 24-Stunden-Residualpfade
  aus der Validierung 2018 sowie historische 95-%- und 99-%-Lastschwellen.

Die großen OPSD-Roh- und Modelldaten bleiben unter `data/raw/` beziehungsweise
`data/processed/` lokal und werden nicht versioniert.
