# Kandidatenkarte: IEA – Energy and AI

**Status:** B/C – optionaler Szenariotreiber und Kontext  
**Rolle:** Rechenzentrumslast als transparenter externer Faktor

## Anbieter und Zugriff

- Anbieter: International Energy Agency (IEA)
- Bericht: https://www.iea.org/reports/energy-and-ai
- relevante Seite: https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai
- Zugriff: öffentlich lesbarer Bericht; Wiederverwendungsrechte für einzelne Daten/Diagramme separat prüfen

## Relevante Aussagen

- globale Rechenzentrumsnachfrage 2024: ungefähr 415 TWh
- IEA-Basisszenario 2030: ungefähr 945 TWh global
- Europa: bis 2030 mehr als 45 TWh bzw. rund 70 % mehr als 2024
- alternative Fälle: Lift-Off, High Efficiency und Headwinds
- deutliche Unsicherheit; ausdrücklich szenariobasierter Ansatz

## Mögliche Nutzung

- Größenordnung und Unsicherheit eines Rechenzentrumssliders begründen
- mehrere qualitative Presets statt eines scheinpräzisen Einzelwertes anbieten
- europäischen Zusatzverbrauch in eine durchschnittliche Leistung umrechnen:

\[
\Delta MW_{avg}=\frac{\Delta TWh\cdot10^6}{8760}
\]

45 TWh/Jahr entsprechen rechnerisch etwa 5,14 GW durchschnittlicher zusätzlicher europäischer Leistung. Dieser europäische Wert darf ohne weitere Quelle nicht gleichmäßig oder willkürlich auf einzelne Länder verteilt werden.

## Beobachtungseinheit und Join

- überwiegend Region × Jahr × Szenario, nicht Land × Stunde
- kein direkter Join mit dem OPSD-Kerndatensatz
- Nutzung nur als externer, offengelegter Szenarioparameter

## Risiken

- regionale Projektion ist zu grob für länderspezifische MW-Aufschläge
- Rechenzentren sind räumlich stark konzentriert
- jährliche Energie (TWh) ist nicht identisch mit stündlicher Last (MW)
- Lastprofil, Auslastung, Effizienz und Standortverteilung fehlen für eine präzise Länderrechnung
- IEA-Projektion nicht als vom eigenen ML-Modell gelernter Trend darstellen

## Eignung

- Kernmodell: ungeeignet
- allgemeiner oder europäischer Szenariokontext: hoch
- länderspezifischer Default-Aufschlag: nur mit weiterer Quelle

## Nächster Verifikationstest

1. prüfen, welche zugänglichen Tabellen hinter den Berichtsgrafiken stehen.
2. entscheiden, ob die App einen rein manuellen MW-Regler oder belegte Szenariopresets nutzt.
3. bei Länderwerten eine zusätzliche nationale Quelle verlangen.

## Vorläufiges Urteil

**Nützlich zur Begründung eines Szenarioreglers, nicht als Trainingsdatensatz.**

