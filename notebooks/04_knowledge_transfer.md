# K – Knowledge Transfer

**Stand:** 26.07.2026

**Status:** Projektartefakte abgeschlossen; Cloud-Deployment stabil aktiv

## Ziel der Phase

Die K-Phase überführt die geprüften Ergebnisse aus Q, U, A³ und C in eine
bedienbare App sowie präsentations- und reproduzierbare Artefakte. Modellklasse,
Featuregruppe und Hyperparameter werden dabei nicht nachträglich verändert.

## Lieferobjekte

- [`streamlit_app/app.py`](../streamlit_app/app.py): interaktive Anwendung
- [`models/gridcast_final_2015_2019.joblib`](../models/gridcast_final_2015_2019.joblib):
  final refittete Inferenzpipeline
- [`reports/k_deployment.json`](../reports/k_deployment.json):
  Modellprüfsumme, App-Daten und Smoke-Tests
- [`scripts/build_k_artifacts.py`](../scripts/build_k_artifacts.py):
  reproduzierbare Erzeugung der Deployment-Daten
- [`documents/GridCast_Europe_Handout.pdf`](../documents/GridCast_Europe_Handout.pdf):
  fünfseitiges Prüfungs-Handout
- [`documents/GridCast_Europe_Referat.pptx`](../documents/GridCast_Europe_Referat.pptx):
  Folien für den 10- bis 15-minütigen Vortrag
- [`documents/GridCast_Europe_Sprechtext.md`](../documents/GridCast_Europe_Sprechtext.md):
  separat lesbarer und in den Folien eingebetteter Sprechtext

## App-Struktur

| Ansicht | Zweck | Datengrundlage |
|---|---|---|
| Überblick | Kernergebnisse und interaktive Europakarte für DE/FR/PL | C-Backtest 2019 und K-Reports |
| Historischer Backtest | Istwert, HGB und gestrichelte Kalender-Baseline mit Hoverwerten | echte Out-of-sample-Prognosen 2019 |
| Zukunftsszenario | Wetter-Cockpit, sieben Presets, Strukturannahmen und Zukunftsvergleichswerte | finales App-Modell, Klimatologie und Risikokalibrierung |
| Methodik | QUA³CK, Modellvergleich, Grenzen und technischer Status | versionierte Projektartefakte |

## Historischer Backtest und App-Modell

Die Backtest-Ansicht verwendet ausschließlich Prognosen des in C bewerteten
Modells:

- Refit: 2015–2018,
- vollständig zurückgehaltener Test: 2019,
- 26.275 Testzeilen,
- Makro-nMAE: 2,71 %,
- Verbesserung gegenüber der Kalender-Baseline: 44,5 %.

Das finale App-Modell wurde erst nach dieser Auswertung mit unveränderter
Konfiguration auf allen 131.441 Länder-Stunden von 2015–2019 trainiert. Es wird
nicht verwendet, um den historischen Backtest rückwirkend zu verbessern.

## Konditionales Zukunftsszenario

Für Land und Datum erzeugt die App ein nominales 24-Stunden-Profil:

1. Kalendermerkmale folgen dem gewählten Datum.
2. Typisches Wetter ist der Median aus 1980–2019 nach
   `Land × Monat × lokale Stunde`.
3. Temperaturabweichung sowie Faktoren für direkte und diffuse Strahlung
   verändern die Wetterfeatures vor einer erneuten ML-Inferenz.
4. Nachfrageänderung und Rechenzentrumslast werden danach als explizite
   Annahmen angewendet.

```math
\widehat L^{scenario}_{c,t}
=
f_{ML}\left(
C_{c,t},
T^{typ}_{c,t}+\Delta T,
r_{dir}R^{typ}_{dir,c,t},
r_{dif}R^{typ}_{dif,c,t}
\right)\cdot(1+g)
+\Delta L_{DC,c,t}
```

Das Ergebnis ist eine Was-wäre-wenn-Rechnung. Es ist weder eine konkrete
Wettervorhersage noch eine autonome Lastprognose bis 2030 oder 2050.

Die direkten ML-Eingaben sind in der App sichtbar von nachgelagerten
Strukturannahmen und dem reinen Auswertungsparameter getrennt. Ein eigener
Tab stellt das typische und das tatsächlich an das HGB übergebene Temperatur-
und Strahlungsprofil gegenüber.

Die App bietet sieben illustrative Einstiegspunkte:

- historische Referenz,
- kalter Wintertag,
- sonniger Tag,
- bewölkter Tag,
- Elektrifizierung,
- Rechenzentrumsboom,
- kombinierter Stresstest.

Jedes Preset setzt ausschließlich sichtbare Startwerte; alle Annahmen bleiben
manuell veränderbar. Angezeigt werden Szenario-Lastspitze, Tagesenergie,
Spitzenzeit und Stunden oberhalb der gewählten historischen Quantilschwelle.
Das 99-%-Quantil ist der bewusst konservativere Standard.

Zusätzlich koppelt ein Annahmenjahr von 2020 bis 2050 die fünf sichtbaren
Wetter- und Strukturregler. Der linear interpolierte Endpunkt 2050 setzt
\(+1{,}5\,^\circ\mathrm{C}\), \(+35\,\%\) Nachfrage,
\(+2.000\,\mathrm{MW}\) Rechenzentrumslast und jeweils \(102\,\%\) der
typischen direkten und diffusen Strahlung. Das Szenariodatum bleibt getrennt,
damit Kalender- und Wochentagseffekte den Pfadvergleich nicht verfälschen.
Die europaweit einheitlichen Werte sind an EEA, ENTSO-E/ENTSOG TYNDP 2024,
IEA *Energy and AI* sowie Segado-Moreno et al. (2026,
DOI `10.1016/j.rse.2025.115122`) angelehnt. Sie sind transparente
Stressannahmen und keine länderscharfe Prognose.

## Wahrscheinlichkeit eines extremen Lastzustands

Die Kennzahl beschreibt ausschließlich die Überschreitung einer historischen
nationalen Lastschwelle. Sie ist **keine Blackout-, Netzüberlastungs- oder
Versorgungsausfallwahrscheinlichkeit**.

Für Land \(c\) wird aus den Trainingsdaten 2015–2017 die Schwelle

```math
q_{c,\alpha}
=
Q_{\alpha}(L_{c,t}:t\in\mathrm{Training})
```

mit \(\alpha=0{,}95\) oder \(0{,}99\) gebildet. Stündliche
Überschreitungswahrscheinlichkeiten werden empirisch aus
Validierungsresiduen 2018 geschätzt:

```math
\widehat P_{c,t}
=
\frac{1}{B}
\sum_{i=1}^{B}
\mathbf{1}
\left[
\widehat L^{scenario}_{c,t}+e_i>q_{c,\alpha}
\right]
```

Für die Tageswahrscheinlichkeit bleiben die zeitlichen Abhängigkeiten
erhalten. Deshalb werden vollständige 24-Stunden-Residualpfade
\(\mathbf e_b\) verwendet:

```math
\widehat P_{day}
=
\frac{1}{B}
\sum_{b=1}^{B}
\mathbf{1}
\left[
\max_{h=1,\dots,24}
(\widehat L^{scenario}_{c,h}+e_{b,h})
>q_{c,\alpha}
\right]
```

| Land | Residualtage 2018 | Q95-Schwelle | Brier-Score 2019 |
|---|---:|---:|---:|
| DE | 362 | 70.597 MW | 0,0657 |
| FR | 359 | 75.338 MW | 0,0146 |
| PL | 362 | 23.623 MW | 0,0475 |

Der Indikator bleibt explorativ: nationale Quantile sind keine technischen
Netzgrenzen, das 99-%-Quantil enthält wenige Ereignisse und starke
Zukunftsszenarien können außerhalb des historischen Kalibrierungsbereichs
liegen.

## Deployment-Daten und Modellintegrität

| Datei | Inhalt |
|---|---|
| `data/app/backtest_2019.csv.gz` | vorab berechnete Out-of-sample-Prognosen |
| `data/app/weather_climatology_1980_2019.csv.gz` | Median-Wetterprofile |
| `data/app/risk_calibration_2018.npz` | Residualpfade und Quantilschwellen |

Das finale Joblib-Artefakt enthält Zielskalierung, Länder-One-Hot-Kodierung,
Kalender-, Feiertags- und Wetterfeatures sowie das trainierte HGB-Modell.

```text
Pfad: models/gridcast_final_2015_2019.joblib
Größe: 1.939.407 Byte
SHA-256: 61526739582848fbe829cdd0a1328e1e7a247dc96f31003c19e95d2071567392
```

Joblib-Dateien dürfen nur aus vertrauenswürdigen Quellen geladen werden. Die
App verwendet ausschließlich das versionierte und über die Prüfsumme
dokumentierte Artefakt.

## Verifikation

Bestanden sind:

- exakte Reproduktion des C-Makro-nMAE,
- frisches Laden des finalen Modells,
- gültige 24-Stunden-Szenarioinferenz,
- zwölf Modell-, Szenario-, Risiko- und App-Strukturtests,
- lokaler Streamlit-Serverstart mit erfolgreichem Health-Check,
- fehlerfreie Ausführung aller vier App-Ansichten,
- Wetter-Preset-Interaktion mit neuer HGB-Inferenz und Neuberechnung aller
  Szenariokennzahlen,
- prüfsummenbasierte Kontrolle aller App-Daten.

## Bereitstellung

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

Das Community-Cloud-Deployment ist unter
[gridcast-europe.streamlit.app](https://gridcast-europe.streamlit.app/)
stabil aktiv. Die Laufzeit wurde ausdrücklich auf Python 3.12.13 festgelegt;
gleichzeitig wurde die Cloud-`requirements.txt` auf sieben direkte
App-Abhängigkeiten reduziert. Dadurch sank die aufgelöste Umgebung von 129 auf
41 Pakete und die App startet ohne den zuvor unter Python 3.14.6 beobachteten
nativen Prozessabsturz. Notebook- und Entwicklungswerkzeuge bleiben getrennt
in `requirements-dev.txt`.

## Grenzen und Wartung

- Modellgültigkeit nur für DE, FR und PL.
- Beobachtungszeitraum der Last: 2015–2019.
- Reanalysewetter ist keine operative Wetterprognose.
- Das final refittete App-Modell besitzt keine neue unabhängige Kennzahl.
- Neue Länder erfordern denselben Qualitäts-, Join- und Evaluationsprozess.
- Neue Datenstände erfordern eine erneute QUA³CK-Schleife ab U/A³.
