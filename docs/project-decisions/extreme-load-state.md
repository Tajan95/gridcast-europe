# Wahrscheinlichkeit eines extremen Lastzustands

**Stand:** 22.07.2026  
**Status:** methodisch festgelegt; Parameter nach Dateninspektion zu bestätigen

## Benennung und Grenze

Die Kennzahl heißt:

> **Wahrscheinlichkeit eines extremen Lastzustands**

Sie ist ausdrücklich **keine Blackout-, Netzausfall- oder Netzüberlastungswahrscheinlichkeit**. Eine außergewöhnlich hohe nationale Last kann durch verfügbare Erzeugung, Importe, Speicher und Netzmaßnahmen beherrscht werden; umgekehrt können lokale Probleme auch unterhalb der nationalen Quantilschwelle auftreten.

## Historische Schwelle

Für Land $c$ wird aus den Trainingsdaten eine Schwelle gebildet:

$$
q_{c,\alpha}
=
Q_{\alpha}\!\left(L_{c,t}:t\in\text{Training}\right)
$$

Als App-Auswahl sind $\alpha=0{,}95$ und optional $0{,}99$ vorgesehen. Die finale Auswertung muss Land, Quantil und Referenzperiode anzeigen.

## Empirische Fehlerverteilung

Auf dem Validierungszeitraum entstehen out-of-sample Residuen:

$$
e_i=L_i-\widehat L_i
$$

Der Testzeitraum bleibt dabei unangetastet. Für den MVP werden länderspezifisch gepoolte Validierungsresiduen verwendet; bei genügend Daten kann später nach Prognosestunde oder Jahreszeit kalibriert werden.

## Stündliche Wahrscheinlichkeit

Für eine Szenarioprognose $\widehat L^{scenario}_{c,t}$ wird empirisch geschätzt:

$$
\widehat P_{c,t}
=
\frac{1}{B}
\sum_{i=1}^{B}
\mathbf{1}\!\left[
\widehat L^{scenario}_{c,t}+e_i>q_{c,\alpha}
\right]
$$

Das Ergebnis ist der Anteil historischer Validierungsfehler, unter denen die prognostizierte Last die Schwelle überschreiten würde.

## Tageswahrscheinlichkeit

Stundenfehler sind zeitlich abhängig. Für die Wahrscheinlichkeit, dass an mindestens einer der 24 Stunden ein Extremzustand auftritt, werden deshalb vollständige 24-Stunden-Residualblöcke $\mathbf e_b$ statt unabhängig gezogener Einzelresiduen verwendet:

$$
\widehat P_{day}
=
\frac{1}{B}
\sum_{b=1}^{B}
\mathbf{1}\!\left[
\max_{h=1,\dots,24}
(\widehat L^{scenario}_{c,h}+e_{b,h})
>q_{c,\alpha}
\right]
$$

Die erste Codefassung liegt in [`src/gridcast/risk.py`](../../src/gridcast/risk.py). Sie berechnet Quantilschwelle, stündliche empirische Wahrscheinlichkeiten und die Tageswahrscheinlichkeit aus Residualpfaden.

## Kalibrierungs- und Evaluationsplan

1. Quantilschwelle nur aus dem Training bestimmen.
2. Fehlerverteilung bzw. 24-h-Residualblöcke aus der Validierung ableiten.
3. Modell und Wahrscheinlichkeitsverfahren einfrieren.
4. Im Testjahr prüfen, wie häufig Ereignisse mit prognostizierten Wahrscheinlichkeiten tatsächlich eintreten.
5. Bei zu wenigen Extremereignissen die Kennzahl als explorativen Risikoindikator kennzeichnen.

## Grenzen

- empirische Residuen bilden nur historisch beobachtete Modellfehler ab,
- ein starkes Zukunftsszenario kann außerhalb des Kalibrierungsbereichs liegen,
- die Quantilschwelle beschreibt außergewöhnliche Last, keine technische Netzgrenze,
- bei kleinen Stichproben ist insbesondere das 99-%-Quantil instabil.

