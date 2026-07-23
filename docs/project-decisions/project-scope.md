# Project Scope und Forschungsfragen

**Stand:** 23.07.2026  
**Status:** beschlossen

## Hauptfrage

> Wie genau lässt sich die stündliche Stromlast ausgewählter europäischer Länder anhand historischer Last-, Wetter- und Kalenderdaten für einen chronologisch späteren, vollständig zurückgehaltenen Zeitraum prognostizieren?

Das Projekt untersucht damit primär die **zeitliche Generalisierung** eines überwachten Regressionsmodells. Ein fester operativer Prognosehorizont von 24 Stunden ist nicht Bestandteil des Pflichtumfangs.

## Erweiterte Streamlit-Frage

> Wie verändert sich ein aus historischen Mustern abgeleitetes Lastprofil für einen frei wählbaren Zukunftszeitpunkt unter klimatologischen und strukturellen Szenarioannahmen?

Die App verbindet zwei methodisch getrennte Ebenen:

1. einen überprüfbaren historischen Backtest und
2. eine konditionale Zukunftsszenarioanalyse.

## Gemeinsames Modellverständnis

Das ML-Modell lernt Zusammenhänge zwischen Stromlast und:

- Land,
- Uhrzeit und Tageszyklus,
- Wochentag, Werktag und Wochenende,
- Monat und Jahreszeit,
- Temperatur und weiteren verfügbaren Wettermerkmalen,
- optional einem historischen Zeitmerkmal zur explorativen Trendanalyse.

Die Kernlogik lautet:

> **Prognostizierte Last = ML-Modell(Land, Kalendermerkmale, Wettermerkmale)**

Unmittelbar vorausgehende Lastmessungen wie `lag_24h`, `lag_48h` oder `lag_168h` sind für das Kernmodell nicht erforderlich. Sie gehören zu einem anderen Anwendungsfall: der operativen Kurzfrist- beziehungsweise Day-ahead-Prognose. Ein solches Modell kann später optional als Genauigkeitserweiterung untersucht werden, ist aber nicht Teil des MVP.

## Historischer Backtest

Für Training und Bewertung werden die Daten chronologisch geteilt, vorläufig beispielsweise:

- 2015–2017: Training,
- 2018: Validierung,
- 2019: unangetasteter Test.

Der konkrete Zeitraum wird erst nach der Datenqualitätsprüfung festgelegt.

Der Testzeitraum liegt innerhalb des vorhandenen historischen Datensatzes, wird dem Training jedoch vollständig vorenthalten. Das Modell erzeugt Prognosen aus den dortigen Kalender- und Wettermerkmalen; anschließend werden diese mit der tatsächlich gemessenen Last verglichen.

Der Testzeitraum ist keine Messlücke. Einzelne künstlich entfernte Werte innerhalb des Trainingszeitraums würden primär ein Imputationsverfahren prüfen und gehören nicht zur eigentlichen Forschungsfrage.

## Zukunftsszenario außerhalb der historischen Daten

Für ein frei gewähltes Zukunftsdatum sind die Kalendermerkmale automatisch bekannt. Das konkrete Wetter und die strukturelle Entwicklung der Stromnachfrage sind dagegen unbekannt.

Die App setzt deshalb standardmäßig ein **statistisch typisches Wetterprofil** ein, das aus historischen Wetterdaten für Land, Jahreszeit beziehungsweise Monat und Tageszeit abgeleitet wird. Dieses Profil kann durch Szenarioregler verändert werden.

Die Ausgabe ist entsprechend zu kennzeichnen:

> **Prognose unter klimatologischen und strukturellen Szenarioannahmen – keine konkrete Wettervorhersage für das gewählte Zukunftsjahr.**

Eine weit außerhalb der Trainingsdaten liegende Ausgabe ist damit keine rekursive Aneinanderreihung kurzfristiger Vorhersagen. Sie ist eine konditionale Projektion unter explizit gewählten Eingaben.

## Pflichtumfang

| Bestandteil | Festlegung |
|---|---|
| Raum | voraussichtlich drei europäische Länder; Auswahl nach Qualitätsprüfung |
| Zeitauflösung | stündlich |
| Evaluation | chronologischer Train-/Validierungs-/Test-Split |
| Zielvariable | tatsächliche Stromlast in MW |
| Baselines | länderspezifischer Mittelwert und Kalenderdurchschnitt |
| ML-Modelle | lineares/regularisiertes Modell und Gradient Boosting |
| Hauptmetriken | MAE, RMSE, normalisierter MAE, Baseline-Verbesserung |
| App-Modus 1 | historischer Backtest mit Prognose und tatsächlicher Last |
| App-Modus 2 | Zukunftsszenario mit typischem Wetterprofil und Szenarioreglern |
| App-Ausgaben | Lastkurve, Szenariovergleich, Spitzenlastdifferenz, Extremzustandswahrscheinlichkeit |

## Pflichtfeatures

### Kalender und Zyklen

- Stunde des Tages, zyklisch kodiert
- Wochentag, zyklisch kodiert
- Werktag oder Wochenende
- Monat oder Jahreszeit
- optional länderspezifischer Feiertag

### Wetter

- Temperatur
- nichtlineare Temperaturwirkung, zum Beispiel Temperaturquadrat oder Heiz-/Kühlgrad-Näherungen
- optional direkte und diffuse horizontale Strahlung oder Bewölkung

### Räumliche und strukturelle Merkmale

- Land
- optional ein historisches Zeitmerkmal ausschließlich zur explorativen Trendanalyse

## Baseline-Konzept

Baselines sind einfache Nicht-ML-Vergleichsverfahren und keine App-Eingaben.

1. **Länderspezifischer Mittelwert:** Für jede Stunde wird die mittlere Trainingslast des Landes vorhergesagt.
2. **Kalender-Baseline:** Für jede Stunde wird ein ausschließlich aus den Trainingsdaten berechneter Durchschnitt für vergleichbare Kalenderbedingungen verwendet, zum Beispiel Land × Monat × Wochentagsklasse × Stunde.

Die Kalender-Baseline ist der wichtigere Vergleichsmaßstab, weil sie Tages-, Wochen- und Saisonmuster bereits ohne ML abbildet. Das ML-Modell soll durch Wetter- und weitere Zusammenhänge einen zusätzlichen, messbaren Nutzen erreichen.

## Langfristige Trends und zusätzliche Datensätze

Ein historischer Nachfrage- oder Zeittrend darf explorativ analysiert und visualisiert werden. Er wird jedoch nicht automatisch als sichere Entwicklung bis 2030 oder 2050 extrapoliert.

Für den Pflichtumfang gilt:

- Das ML-Modell lernt Tages-, Wochen-, Saison- und Wetterzusammenhänge.
- Langfristiges Nachfragewachstum wird als transparente Szenarioannahme ergänzt.
- Rechenzentren werden als eigener additiver Faktor modelliert.
- Ein historischer Trend wird als deskriptiver Befund, nicht als garantierter Zukunftspfad behandelt.

Ein längerer Wetterdatensatz kann zur stabileren Schätzung klimatologischer Standardprofile sinnvoll sein. Ein zusätzlicher, weit zurückreichender Lastdatensatz wird nur aufgenommen, wenn Definition, räumliche Abdeckung und Messmethodik mit den Kerndaten hinreichend vergleichbar sind. Er ist keine Voraussetzung für den MVP.

## Basisszenario der App

Das Basisszenario ist die unveränderte ML-Prognose unter den Standardannahmen:

- statistisch typisches Wetterprofil,
- Temperaturabweichung `0 °C`,
- allgemeine Nachfrageänderung `0 %`,
- zusätzliche Rechenzentrumslast `0 MW`.

Davon ausgehend verändern Slider die Temperaturannahme, die allgemeine Nachfrage und die zusätzliche Rechenzentrumslast transparent.

## Zwei App-Modi

1. **Historischer Backtest:** Auswahl eines Datums aus dem Testzeitraum. Prognose und tatsächlich gemessene Last werden direkt verglichen.
2. **Zukunftsszenario:** Auswahl von Land und Zukunftsdatum. Die App erzeugt Kalendermerkmale und ein typisches Wetterprofil automatisch; Szenarioregler verändern Temperatur, Nachfrage und Rechenzentrumslast.

Eine dargestellte 24-Stunden-Lastkurve bezeichnet dabei den Umfang der Visualisierung für einen ausgewählten Tag, nicht einen festgelegten Prognosehorizont von 24 Stunden.

## Außerhalb des Scopes

- eigenständiges Wettervorhersagemodell
- operative Day-ahead-Anbindung an aktuelle Last- und Wetterfeeds
- rekursive Lastprognose von Tag zu Tag bis zu einem fernen Zukunftsjahr
- sektorale Zerlegung der nationalen Stromlast
- eigenes Modell des europäischen Netzausbaus
- Lastflussrechnung, regionale Leitungsengpässe oder Netztopologie
- absolute Blackout- oder Netzausfallwahrscheinlichkeit
- gemeinsame kausale Prognose von Klima, Elektrifizierung, Rechenzentren und Netzausbau
- Deep Learning als Pflichtbestandteil

## Optional nach funktionierendem Kern

- längere Wetterhistorie für klimatologische Referenzprofile
- benannte RCP-/Klimaszenarien aus CORDEX
- offizielle langfristige Nachfragepfade aus ENTSO-E TYNDP
- IEA-Rechenzentrumsszenarien als transparenter externer Kontext
- Feiertagsfeatures
- länderspezifische Modelle zusätzlich zu einem gemeinsamen Modell
- separates lag-basiertes Day-ahead-Modell als Vergleichserweiterung

## Definition of Done

Das Projekt ist prüfungsbereit, wenn:

1. Datenimport und Aufbereitung reproduzierbar sind,
2. mindestens drei Länder ausreichend vollständige, joinbare Daten besitzen,
3. alle Modellfeatures und Szenarioannahmen nachvollziehbar dokumentiert sind,
4. zwei Baselines und mindestens zwei ML-Modellklassen verglichen wurden,
5. der Mehrwert gegenüber der Kalender-Baseline auf dem unangetasteten Testzeitraum quantifiziert wird,
6. Fehler nach Land und Tageszeit erklärt werden,
7. die Streamlit-App Backtest und Zukunftsszenario klar trennt,
8. langfristige Ausgaben ausdrücklich als konditionale Szenarioprojektionen kommuniziert werden.
