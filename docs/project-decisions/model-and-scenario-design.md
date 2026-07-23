# Modell-, Baseline- und Szenariodesign

**Stand:** 23.07.2026

## Baseline-Modell und Basisszenario sind verschieden

| Begriff | Zweck | Definition |
|---|---|---|
| Baseline-Modell | prüft, ob ML überhaupt Mehrwert liefert | naive Prognose durch Last vor 24 h bzw. 168 h |
| Basisszenario | Referenz innerhalb der Streamlit-App | `ΔT = 0`, allgemeine Nachfrageänderung `0 %`, zusätzliche Rechenzentrumslast `0 MW` |

### Baseline-Modelle

```math
\widehat L^{(24)}_{c,t}=L_{c,t-24}
```

```math
\widehat L^{(168)}_{c,t}=L_{c,t-168}
```

Das finale ML-Modell wird auf denselben Teststunden gegen beide Regeln verglichen.

#### Bedeutung von 24 und 168 Stunden

Für eine beispielhafte Zielstunde **Mittwoch, 15:00 Uhr** bedeutet:

- $L_{c,t-24}$: gemessene Last am Dienstag um 15:00 Uhr,
- $L_{c,t-168}$: gemessene Last am vorherigen Mittwoch um 15:00 Uhr.

Die 24-Stunden-Baseline übernimmt also schlicht den Wert derselben Stunde des Vortags; die 168-Stunden-Baseline den Wert derselben Stunde der Vorwoche. Das sind bewusst einfache **Nicht-ML-Vergleichsmodelle**. „Naiv“ bedeutet hier nicht schlecht oder unseriös, sondern: Die Regel schätzt keine Parameter und berücksichtigt keine weiteren Einflussgrößen.

Dieselben verzögerten Messwerte können zusätzlich als Eingaben des ML-Modells dienen. Dort werden sie jedoch mit Wetter-, Kalender- und weiteren Vergangenheitsmerkmalen kombiniert. Baseline-Prognose und Lag-Feature sind daher zwei verschiedene Verwendungen desselben historischen Messwerts.

### Warum gerade eine Day-ahead-Prognose?

Die 24 Stunden sind ein gewählter Prognosehorizont. Das Modell soll zu einem gedachten Erstellungszeitpunkt eine Lastkurve für den Folgetag liefern. Deshalb dürfen Lastfeatures für die Zielstunde $t$ spätestens bei $t-24$ enden. Andernfalls würden Informationen verwendet, die zum Prognosezeitpunkt noch nicht vorliegen.

Die 168-Stunden-Regel gehört nicht zum Prognosehorizont. Sie ist lediglich eine zweite saisonale Baseline: Derselbe Wochentag und dieselbe Uhrzeit der Vorwoche ähneln der Zielstunde häufig stärker als der Vortag, besonders an Wochenenden.

### Prognose, Test-Split und echte Datenlücken

Diese drei Fälle sind methodisch zu trennen:

1. **Chronologischer Test-Split:** Die Messwerte des Testjahres sind vorhanden, werden dem Training aber vorenthalten. Das Modell prognostiziert sie; anschließend werden Prognose und tatsächlich gemessene Last verglichen. Der Test-Split ist keine Datenlücke.
2. **Echte Messlücke:** Fehlen einzelne Last- oder Wetterwerte bereits im Rohdatensatz, muss die betroffene Zeile dokumentiert verworfen oder mit einem gesonderten, ausschließlich vergangenheitsbasierten Verfahren imputiert werden. Das ist Datenbereinigung, nicht das primäre Prognoseziel.
3. **Day-ahead-Prognose:** Das trainierte Modell schätzt eine noch unbekannte Zielstunde 24 Stunden im Voraus aus den zu diesem Zeitpunkt verfügbaren historischen Lastwerten sowie bekannten Kalender- und angenommenen Wetterdaten.

Das absichtliche Entfernen einzelner Werte „zwischendrin“ würde primär die Qualität einer **Imputation** prüfen. Für die Bewertung einer Zukunftsprognose wäre dieses Vorgehen irreführend, weil zufällig umgebende spätere Werte verfügbar sein könnten. Deshalb bleibt der Testzeitraum als vollständiger, chronologisch späterer Block zurückgehalten.

### Welche Eingaben benötigt eine Vorhersage?

Für eine Zielstunde genügen Datum und Uhrzeit allein nicht. Das Modell benötigt:

- bekannte Kalendermerkmale der Zielstunde,
- ein Wetterprofil der Zielstunde, im Backtest aus Reanalysedaten und im Einsatz aus einer Wettervorhersage,
- reale historische Lastmessungen, die zum Erstellungszeitpunkt bereits vorliegen, insbesondere $t-24$, $t-48$ und $t-168$.

Dadurch kann die App beliebige **geeignete Backtesttage** aus dem zurückgehaltenen Testzeitraum abfragen. Eine reale operative Prognose kann sie für die nächsten 24 Stunden erzeugen, sobald aktuelle Last- und Wettervorhersagedaten angebunden sind. Für ein beliebiges fernes Zukunftsdatum wäre dagegen ein externes Wetter-/Klimaprofil und ein ausdrücklich definiertes Referenzlastprofil nötig.

Eine Prognose für weit entfernte Jahre entsteht nicht durch rekursives Wiederholen der 24-Stunden-Prognose. Die langfristige Ebene bleibt eine ausgewiesene Szenarioanalyse auf Basis eines Referenzprofils und expliziter externer Annahmen.

### Basisszenario der App

Das Basisszenario ist die unveränderte ML-Prognose für den gewählten historischen Backtest- oder Referenztag:

- Temperaturprofil unverändert (`ΔT = 0 °C`),
- keine zusätzliche strukturelle Nachfrage (`g = 0`),
- keine zusätzliche Rechenzentrumslast (`ΔL_DC = 0 MW`).

Bei einem Backtesttag stammt die Temperatur aus der Reanalyse und war historisch tatsächlich beobachtet. Für ein Zukunftsszenario wird ein ausgewiesener Referenztag bzw. ein externer Wetter-/Klimapfad benötigt; die App darf keine exakte Wettervorhersage für ein beliebiges Datum 2030 vortäuschen.

## Szenariorechnung

Zuerst wird die Temperatur innerhalb der Wetterfeatures geändert und das ML-Modell erneut ausgeführt:

```math
\widehat L^{\text{temp}}_{c,t}
=
f_{ML}(X_{c,t}\;\text{mit}\;T_{c,t}+\Delta T)
```

Danach werden transparente externe Annahmen angewendet:

```math
\widehat L^{\text{scenario}}_{c,t}
=
\widehat L^{\text{temp}}_{c,t}\,(1+g)
+
\Delta L_{DC,c,t}
```

mit:

- $\Delta T$: Temperaturänderung gegenüber dem Referenzprofil,
- $g$: relative strukturelle Nachfrageänderung gegenüber dem Basisszenario,
- $\Delta L_{DC,c,t}$: externer Rechenzentrumslastaufschlag in MW.

Falls ein jährlicher Wachstumssatz $r$ und ein Szenariojahr $y$ verwendet werden, wird $g$ explizit berechnet:

```math
g(y)=(1+r)^{y-y_0}-1
```

Ein einfacher Prozentregler ist für den Pflichtumfang leichter zu verteidigen. Ein Jahresregler darf erst ergänzt werden, wenn Referenzjahr und Wachstumspfad durch eine konkrete Quelle belegt sind.

## Vier zentrale App-Ausgaben

1. prognostizierte 24-Stunden-Lastkurve,
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

## Interpretation

Die Szenarioregler verändern bekannte Eingaben oder addieren offengelegte externe Annahmen. Das ist methodisch eine konditionale Projektion, keine kausale Behauptung, dass genau diese Entwicklung eintreten wird.
