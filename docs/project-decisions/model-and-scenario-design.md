# Modell-, Baseline- und Szenariodesign

**Stand:** 23.07.2026

## Baseline-Modell und Basisszenario sind verschieden

| Begriff | Zweck | Definition |
|---|---|---|
| Baseline-Modell | prüft, ob ML einen messbaren Mehrwert liefert | einfache Prognose aus Trainingsdurchschnitten |
| Basisszenario | Referenz innerhalb der Streamlit-App | typisches Wetterprofil, `ΔT = 0`, Nachfrageänderung `0 %`, zusätzliche Rechenzentrumslast `0 MW` |

Baselines werden nur für Evaluation und Vergleich berechnet. Sie sind keine Eingabevariablen der App.

## Zielmodell

Das Kernmodell ist eine überwachte Regression für die stündliche Stromlast:

```math
\widehat L_{c,t}
=
f_{ML}\!\left(
C_{c,t},
W_{c,t}
\right)
```

mit:

- $c$: Land,
- $t$: Zielstunde,
- $C_{c,t}$: Kalender-, Zyklus- und Ländermerkmale,
- $W_{c,t}$: Wettermerkmale,
- $\widehat L_{c,t}$: prognostizierte Stromlast in MW.

Das Kernmodell benötigt keine unmittelbar vorausgehenden Lastmessungen wie $L_{t-24}$ oder $L_{t-168}$. Dadurch bleibt die Zukunftsszenarioanalyse unabhängig von erfundenen zukünftigen Lag-Werten.

Ein separates lag-basiertes Day-ahead-Modell wäre methodisch möglich und häufig kurzfristig genauer. Es gehört jedoch nicht zum MVP, weil es einen anderen Anwendungsfall und eine andere Datenverfügbarkeit voraussetzt.

## Baseline-Modelle

Alle Baseline-Werte werden ausschließlich aus dem Trainingszeitraum berechnet.

### 1. Länderspezifischer Mittelwert

```math
\widehat L^{\text{mean}}_{c,t}
=
\operatorname{mean}_{i \in \text{Train},\,c_i=c}(L_i)
```

Diese minimale Baseline sagt für jede Stunde eines Landes denselben Wert voraus.

### 2. Kalender-Baseline

```math
\widehat L^{\text{calendar}}_{c,t}
=
\operatorname{mean}
\left(
L_i
\mid
c_i=c,\,
m_i=m_t,\,
d_i=d_t,\,
h_i=h_t,\,
i \in \text{Train}
\right)
```

Dabei stehen:

- $m$ für Monat oder Saison,
- $d$ für Wochentag beziehungsweise Werktagsklasse,
- $h$ für Stunde des Tages.

Die genaue Gruppierung wird anhand der Datenmenge gewählt. Bei zu kleinen Gruppen wird eine dokumentierte Rückfallhierarchie verwendet, zum Beispiel ohne Monat und anschließend nur nach Land und Stunde.

Die Kalender-Baseline ist der zentrale Vergleichsmaßstab. Sie enthält bereits typische Tages-, Wochen- und Saisonmuster. Das ML-Modell soll sie durch Wetter- und weitere Zusammenhänge schlagen.

## Training, Validierung und Test

Der Datensatz wird chronologisch geteilt:

1. **Training:** Modellparameter und Baseline-Durchschnitte werden gelernt.
2. **Validierung:** Features, Hyperparameter und Modellklasse werden gewählt.
3. **Test:** Das endgültige Modell wird einmalig auf einem vollständig späteren, unangetasteten Zeitraum bewertet.

Der konkrete Split wird nach der Datenqualitätsprüfung festgelegt. Ein mögliches Schema ist 2015–2017 Training, 2018 Validierung und 2019 Test.

### Was der Backtest simuliert

Für jede Teststunde verhält sich das Modell so, als kenne es die zugehörige Last noch nicht. Die Kalender- und historischen Wettermerkmale der Teststunde werden als Eingaben verwendet; die gemessene Last bleibt ausschließlich der spätere Vergleichswert.

Das ist keine künstliche Datenlücke und keine Imputation. Der chronologisch spätere Block prüft, ob die gelernten Beziehungen zeitlich generalisieren.

### Auswertung

Berichtet werden mindestens:

- MAE,
- RMSE,
- normalisierter MAE,
- Verbesserung gegenüber beiden Baselines,
- Fehler nach Land,
- Fehler nach Tageszeit und Saison.

Wenn das ML-Modell die Kalender-Baseline nicht schlägt, wird dies als valides negatives Ergebnis und als fehlender nachgewiesener Mehrwert dokumentiert.

## Statistisch typisches Wetterprofil

Für ein Zukunftsdatum sind Kalendermerkmale bekannt, das konkrete Wetter jedoch nicht. Die App erzeugt deshalb automatisch ein klimatologisches Standardprofil:

```math
W^{\text{typ}}_{c,t}
=
\operatorname{median}
\left(
W_i
\mid
c_i=c,\,
\operatorname{Kalendergruppe}(i)=\operatorname{Kalendergruppe}(t)
\right)
```

Als Kalendergruppe dienen beispielsweise Land × Monat × Stunde. Alternativ kann ein geglättetes Profil nach Tag des Jahres und Stunde verwendet werden. Die endgültige Methode wird nach Prüfung von Datenmenge und Wetterauflösung festgelegt.

Das typische Profil umfasst mindestens die Temperatur. Weitere Wettermerkmale wie Strahlung oder Bewölkung werden nur aufgenommen, wenn sie in ausreichender Qualität und konsistenter Granularität verfügbar sind.

Eine längere Wetterhistorie kann die Schätzung dieses Standardprofils stabilisieren. Sie ist optional und methodisch von einem längeren Lastdatensatz zu trennen.

## Basisszenario der App

Für ein gewähltes Land und Zukunftsdatum erzeugt die App zunächst:

```math
\widehat L^{\text{base}}_{c,t}
=
f_{ML}
\left(
C_{c,t},
W^{\text{typ}}_{c,t}
\right)
```

Das Basisszenario steht für:

- Kalendermerkmale des gewählten Datums,
- statistisch typisches Wetter,
- Temperaturabweichung `0 °C`,
- keine zusätzliche strukturelle Nachfrage,
- keine zusätzliche Rechenzentrumslast.

Es bildet damit das Lastprofil unter historisch gelernten Beziehungen und neutralen Szenarioannahmen ab. Es ist keine konkrete Wetter- oder Energiesystemvorhersage für das gewählte Zukunftsjahr.

## Szenariorechnung

Zuerst wird das Wetterprofil verändert und das ML-Modell erneut ausgeführt:

```math
\widehat L^{\text{weather}}_{c,t}
=
f_{ML}
\left(
C_{c,t},
W^{\text{typ}}_{c,t}
\text{ mit } T_{c,t}+\Delta T
\right)
```

Danach werden transparente externe Annahmen angewendet:

```math
\widehat L^{\text{scenario}}_{c,t}
=
\widehat L^{\text{weather}}_{c,t}(1+g)
+
\Delta L_{DC,c,t}
```

mit:

- $\Delta T$: Temperaturänderung gegenüber dem typischen Wetterprofil,
- $g$: relative strukturelle Nachfrageänderung gegenüber dem Basisszenario,
- $\Delta L_{DC,c,t}$: externer Rechenzentrumslastaufschlag in MW.

Falls ein jährlicher Wachstumssatz $r$ und ein Szenariojahr $y$ verwendet werden, wird die Nachfrageänderung explizit berechnet:

```math
g(y)=(1+r)^{y-y_0}-1
```

Ein direkter Prozentregler bleibt für den Pflichtumfang leichter zu erklären. Ein Jahres- oder Wachstumspfad wird nur ergänzt, wenn Referenzjahr und Annahme eindeutig dokumentiert beziehungsweise durch eine Quelle belegt sind.

## Rolle historischer Langzeittrends

Ein historisches Zeitmerkmal kann in der Analyse verwendet werden, um zu prüfen, ob im beobachteten Zeitraum ein systematischer Trend vorhanden ist.

Dabei gelten drei Grenzen:

1. Ein kurzer Beobachtungszeitraum erlaubt keine stabile Aussage über mehrere Jahrzehnte.
2. Strukturbrüche durch Energiekrisen, Elektrifizierung, Effizienz, Demografie oder geänderte Messmethoden können einen einfachen Trend verzerren.
3. Baumbasierte Modelle wie Gradient Boosting extrapolieren außerhalb des beobachteten Wertebereichs nur eingeschränkt.

Deshalb wird ein historischer Trend:

- explorativ analysiert,
- optional in einem Modellvergleich mit und ohne Zeitmerkmal getestet,
- nicht automatisch bis 2030 oder 2050 fortgeschrieben.

Längere Lastdatensätze können als deskriptiver Kontext oder zur Kalibrierung externer Szenarien dienen. Sie werden nur in das Kerntraining integriert, wenn Definitionen und Messmethoden mit den übrigen Daten vergleichbar sind.

## Zwei App-Modi

### 1. Historischer Backtest

- Auswahl eines Tages aus dem Testzeitraum,
- Prognose aus Kalender- und tatsächlichen historischen Wettermerkmalen,
- Vergleich mit der gemessenen Last,
- Anzeige der Baselines und Fehlerkennzahlen.

### 2. Zukunftsszenario

- Auswahl von Land und Zukunftsdatum,
- automatische Ableitung der Kalendermerkmale,
- automatisches typisches Wetterprofil,
- Regler für Temperaturabweichung, Nachfrageänderung und Rechenzentrumslast,
- Vergleich von Basisszenario und verändertem Szenario.

Eine dargestellte Tageskurve umfasst 24 Stunden des gewählten Tages. Dies ist eine Darstellungsentscheidung und kein operativer 24-Stunden-Prognosehorizont.

## Zentrale App-Ausgaben

1. prognostizierte 24-Stunden-Lastkurve des ausgewählten Tages,
2. direkte Überlagerung mit dem Basisszenario,
3. zusätzliche Spitzenlast in MW und Prozent,
4. Wahrscheinlichkeit eines extremen Lastzustands relativ zu einer historischen Quantilschwelle.

Für die zusätzliche Spitzenlast:

```math
\Delta L_{peak}
=
\max_t \widehat L^{\text{scenario}}_{c,t}
-
\max_t \widehat L^{\text{base}}_{c,t}
```

```math
\Delta L_{peak,\%}
=
100\cdot
\frac{\Delta L_{peak}}
{\max_t \widehat L^{\text{base}}_{c,t}}
```

Die Extremzustandswahrscheinlichkeit bezieht sich ausschließlich auf eine historisch definierte Lastschwelle. Sie ist keine Blackout- oder Netzausfallwahrscheinlichkeit.

## Interpretation

Die App erzeugt eine **konditionale Projektion**:

> Wie sähe das gelernte Lastprofil aus, wenn für das gewählte Datum das typische Wetter beziehungsweise die eingestellten Abweichungen und strukturellen Zusatzannahmen gelten?

Sie behauptet nicht, das konkrete Wetter, den Strukturwandel oder die tatsächliche Stromlast eines fernen Zukunftsjahres autonom vorherzusagen.
