# Modell-, Baseline- und Szenariodesign

**Stand:** 22.07.2026

## Baseline-Modell und Basisszenario sind verschieden

| Begriff | Zweck | Definition |
|---|---|---|
| Baseline-Modell | prüft, ob ML überhaupt Mehrwert liefert | naive Prognose durch Last vor 24 h bzw. 168 h |
| Basisszenario | Referenz innerhalb der Streamlit-App | `ΔT = 0`, allgemeine Nachfrageänderung `0 %`, zusätzliche Rechenzentrumslast `0 MW` |

### Baseline-Modelle

$$
\widehat L^{(24)}_{c,t}=L_{c,t-24}
$$

$$
\widehat L^{(168)}_{c,t}=L_{c,t-168}
$$

Das finale ML-Modell wird auf denselben Teststunden gegen beide Regeln verglichen.

### Basisszenario der App

Das Basisszenario ist die unveränderte ML-Prognose für den gewählten historischen Backtest- oder Referenztag:

- Temperaturprofil unverändert (`ΔT = 0 °C`),
- keine zusätzliche strukturelle Nachfrage (`g = 0`),
- keine zusätzliche Rechenzentrumslast (`ΔL_DC = 0 MW`).

Bei einem Backtesttag stammt die Temperatur aus der Reanalyse und war historisch tatsächlich beobachtet. Für ein Zukunftsszenario wird ein ausgewiesener Referenztag bzw. ein externer Wetter-/Klimapfad benötigt; die App darf keine exakte Wettervorhersage für ein beliebiges Datum 2030 vortäuschen.

## Szenariorechnung

Zuerst wird die Temperatur innerhalb der Wetterfeatures geändert und das ML-Modell erneut ausgeführt:

$$
\widehat L^{\text{temp}}_{c,t}
=
f_{ML}(X_{c,t}\;\text{mit}\;T_{c,t}+\Delta T)
$$

Danach werden transparente externe Annahmen angewendet:

$$
\widehat L^{\text{scenario}}_{c,t}
=
\widehat L^{\text{temp}}_{c,t}\,(1+g)
+
\Delta L_{DC,c,t}
$$

mit:

- $\Delta T$: Temperaturänderung gegenüber dem Referenzprofil,
- $g$: relative strukturelle Nachfrageänderung gegenüber dem Basisszenario,
- $\Delta L_{DC,c,t}$: externer Rechenzentrumslastaufschlag in MW.

Falls ein jährlicher Wachstumssatz $r$ und ein Szenariojahr $y$ verwendet werden, wird $g$ explizit berechnet:

$$
g(y)=(1+r)^{y-y_0}-1
$$

Ein einfacher Prozentregler ist für den Pflichtumfang leichter zu verteidigen. Ein Jahresregler darf erst ergänzt werden, wenn Referenzjahr und Wachstumspfad durch eine konkrete Quelle belegt sind.

## Vier zentrale App-Ausgaben

1. prognostizierte 24-Stunden-Lastkurve,
2. direkte Überlagerung mit dem Basisszenario,
3. zusätzliche Spitzenlast in MW und Prozent,
4. Wahrscheinlichkeit eines extremen Lastzustands relativ zu einer historischen Quantilschwelle.

Für die zusätzliche Spitzenlast:

$$
\Delta L_{peak}
=
\max_t \widehat L^{\text{scenario}}_{c,t}
-
\max_t \widehat L^{\text{base}}_{c,t}
$$

$$
\Delta L_{peak,\%}
=
100\cdot
\frac{\Delta L_{peak}}
{\max_t \widehat L^{\text{base}}_{c,t}}
$$

## Interpretation

Die Szenarioregler verändern bekannte Eingaben oder addieren offengelegte externe Annahmen. Das ist methodisch eine konditionale Projektion, keine kausale Behauptung, dass genau diese Entwicklung eintreten wird.

