# Streamlit-App

Die App ist das zentrale Deployment-Artefakt der K-Phase.

## Lokal starten

Aus der Repository-Wurzel:

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

## Ansichten

1. **Überblick:** Forschungsfrage, Kernergebnisse und Deployment-Status
2. **Historischer Backtest:** 2019-Istwerte, HGB-Prognose,
   Kalender-Baseline und Tagesfehler
3. **Zukunftsszenario:** typisches Wetterprofil, Temperaturabweichung,
   Nachfrageänderung und zusätzlicher Rechenzentrumslastaufschlag
4. **Methodik:** QUA³CK-Prozess, Modellvergleich und Grenzen

Der historische Backtest verwendet ausschließlich die in der C-Phase
erzeugten Out-of-sample-Prognosen eines auf 2015–2018 refitteten Modells.
Die Zukunftsszenarien werden mit dem finalen, nach Abschluss des Tests auf
2015–2019 refitteten App-Modell berechnet.

## Wichtige Abgrenzung

Die Zukunftsansicht erzeugt eine konditionale Was-wäre-wenn-Rechnung. Das
typische Wetterprofil ist keine konkrete Wettervorhersage; Nachfrage- und
Rechenzentrumseffekte sind explizite externe Annahmen. Die angezeigte
Wahrscheinlichkeit eines extremen Lastzustands bezieht sich auf eine
historische Quantilschwelle und ist keine Blackout- oder
Netzausfallwahrscheinlichkeit.
