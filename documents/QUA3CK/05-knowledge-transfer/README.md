# K – Knowledge Transfer

**Status:** technisch abgeschlossen; öffentliches Cloud-Deployment ausstehend  
**Stand:** 25.07.2026

## Ziel der Phase

Die K-Phase überführt die in Q, U, A³ und C erzeugten Erkenntnisse in
nachvollziehbare, bedienbare und präsentierbare Portfolio-Artefakte. Sie
verändert weder Modellklasse noch Hyperparameter und verwendet das Testjahr
nicht für eine nachträgliche Auswahl.

## Zentrale Lieferobjekte

- [`streamlit_app/app.py`](../../../streamlit_app/app.py): interaktive App
- [`models/gridcast_final_2015_2019.joblib`](../../../models/gridcast_final_2015_2019.joblib):
  final refittete Inferenzpipeline
- [`reports/k/k_deployment.json`](../../../reports/k/k_deployment.json):
  Prüfsummen, App-Daten und Smoke-Tests
- [`scripts/build_k_artifacts.py`](../../../scripts/build_k_artifacts.py):
  reproduzierbare Erzeugung der kompakten Deployment-Daten
- [`documents/handout/GridCast_Europe_Handout.pdf`](../../handout/GridCast_Europe_Handout.pdf):
  fünfseitiges Prüfungs-Handout
- [`documents/presentation/GridCast_Europe_Referat.pptx`](../../presentation/GridCast_Europe_Referat.pptx):
  Foliensatz für den 10–15-minütigen Vortrag
- [`documents/presentation/GridCast_Europe_Sprechtext.md`](../../presentation/GridCast_Europe_Sprechtext.md):
  eingebetteter und separat lesbarer Sprechtext

## App-Struktur

| Ansicht | Zweck | Datengrundlage |
|---|---|---|
| Überblick | Forschungsfrage und Kernergebnisse | C- und K-Reports |
| Historischer Backtest | Istwert, HGB und Kalender-Baseline nach Tag | echte Out-of-sample-Prognosen 2019 |
| Zukunftsszenario | typische Wetter- und Strukturannahmen variieren | finales App-Modell + Klimatologie 1980–2019 |
| Methodik | QUA³CK, Modellvergleich und Grenzen | versionierte Dokumentation |

## Saubere Trennung der beiden Prognoseebenen

### Historischer Backtest

Die App zeigt vorab berechnete Prognosen des C-Modells:

- Refit: 2015–2018,
- vollständig zurückgehaltener Test: 2019,
- 26.275 Testzeilen,
- Makro-nMAE: 2,71 %,
- Verbesserung gegenüber der Kalender-Baseline: 44,5 %.

Das auf 2015–2019 refittete App-Modell wird in dieser Ansicht nicht verwendet.
Dadurch bleiben die gezeigten 2019-Werte echte Out-of-sample-Ergebnisse.

### Konditionales Zukunftsszenario

Für ein gewähltes Land und Datum erzeugt die App ein nominales
24-Stunden-Profil:

1. Kalendermerkmale folgen dem Datum.
2. Typisches Wetter ist der Median aus 1980–2019 nach
   `Land × Monat × lokale Stunde`.
3. Eine Temperaturabweichung verändert die Wetterfeatures vor der
   ML-Inferenz.
4. Nachfrageänderung und Rechenzentrumslast werden danach als explizite
   Annahmen angewendet.

Formal:

```math
\widehat L^{scenario}_{c,t}
=
f_{ML}(C_{c,t}, W^{typ}_{c,t}+\Delta T)\cdot(1+g)
+\Delta L_{DC,c,t}
```

Die Ausgabe ist eine Was-wäre-wenn-Rechnung. Sie ist keine konkrete
Wettervorhersage und keine autonome Langfristprognose bis 2030 oder 2050.

## Explorative Wahrscheinlichkeit eines extremen Lastzustands

Die angezeigte Wahrscheinlichkeit bezieht sich ausschließlich auf die
Überschreitung einer historischen nationalen Lastschwelle:

- Schwellen: länderspezifisches 95-%- oder 99-%-Quantil aus 2015–2017,
- Unsicherheit: vollständige 24-Stunden-Residualpfade aus 2018,
- nachgelagerte Plausibilitätsprüfung: vollständige lokale Tage 2019.

Sie ist ausdrücklich **keine Blackout-, Netzüberlastungs- oder
Versorgungsausfallwahrscheinlichkeit**.

| Land | vollständige Residualtage 2018 | Q95-Schwelle | Brier-Score 2019 |
|---|---:|---:|---:|
| DE | 362 | 70.597 MW | 0,0657 |
| FR | 359 | 75.338 MW | 0,0146 |
| PL | 362 | 23.623 MW | 0,0475 |

Der Risikoindikator bleibt explorativ, weil nationale Lastquantile keine
technischen Netzgrenzen darstellen und starke Zukunftsszenarien außerhalb
des historischen Kalibrierungsbereichs liegen können.

## Modellbereitstellung

Das finale Artefakt enthält:

- länderweise Zielskalierung,
- Länder-One-Hot-Kodierung,
- Kalender-, Feiertags- und Wetterfeatures,
- das trainierte Histogram-Gradient-Boosting-Modell.

```text
Pfad: models/gridcast_final_2015_2019.joblib
Größe: 1.939.407 Byte
SHA-256: 61526739582848fbe829cdd0a1328e1e7a247dc96f31003c19e95d2071567392
```

Die Paketversionen von Scikit-learn, Pandas und Joblib sind für das
Cloud-Deployment in `requirements.txt` festgelegt. Zwischenmodelle,
Rohdaten und große Modelldatensätze bleiben ausgeschlossen.

## Verifikation

Bestanden sind:

- exakte Reproduktion des C-Makro-nMAE,
- frisches Laden des finalen Modells,
- gültige 24-Stunden-Szenarioinferenz,
- elf Modell-, Szenario-, Risiko- und App-Strukturtests,
- echter Streamlit-Serverstart und erfolgreicher Health-Check,
- prüfsummenbasierte Kontrolle aller App-Daten.

## Lokaler Start

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

## Streamlit Community Cloud

Deployment-Konfiguration:

- Repository: `Tajan95/gridcast-europe`
- Branch: `main`
- Entrypoint: `streamlit_app/app.py`
- Python: `3.12`
- Secrets: keine erforderlich

Der letzte Veröffentlichungsschritt erfolgt in Streamlit Community Cloud über
„Create app“. Die Plattform bezieht danach Code, Modell und Abhängigkeiten
direkt aus dem öffentlichen GitHub-Repository.

## Grenzen und Wartung

- Modellgültigkeit ist auf DE, FR und PL beschränkt.
- Historischer Beobachtungszeitraum der Last: 2015–2019.
- Reanalysewetter im Backtest ist keine operative Wetterprognose.
- Das final refittete App-Modell besitzt keine neue unabhängige Kennzahl.
- Neue Länder benötigen denselben Qualitäts- und Joinbarkeitscheck.
- Neue Datenstände erfordern eine erneute QUA³CK-Schleife ab U/A³.
