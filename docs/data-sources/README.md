# Datenquellen-Katalog

Dieser Ordner enthält standardisierte Kandidatenkarten. Sie dokumentieren die Machbarkeit, ersetzen aber nicht die reproduzierbare Dateninspektion im Notebook.

## Bewertungsstatus

- **A – Kernquelle:** für Zielvariable oder Pflichtfeatures priorisiert
- **B – optionale Erweiterung:** fachlich nützlich, aber für den Pflichtumfang nicht erforderlich
- **C – Kontext/Abgrenzung:** unterstützt Interpretation oder Grenzen, nicht das Kerntraining
- **Offen:** zentrale technische oder lizenzrechtliche Punkte müssen noch verifiziert werden

## Aktueller Katalog

| Quelle | Rolle | Status | Einsatz |
|---|---|---:|---|
| [OPSD Time Series](opsd-time-series.md) | tatsächliche Last und Lags | A | Kernmodell |
| [OPSD Weather Data](opsd-weather-data.md) | Temperatur und Strahlung | A | Kernmodell |
| [Copernicus CORDEX](copernicus-cordex.md) | Klimaprojektionen | B | spätere Klimaszenarien |
| [ENTSO-E/ENTSOG TYNDP 2024](entsoe-tyndp-2024.md) | offizielle Nachfragepfade | B | langfristige Szenariowerte |
| [IEA Energy and AI](iea-energy-and-ai.md) | Rechenzentrumsszenarien | B/C | externer Szenariokontext |
| [ENTSO-E ERAA 2025](entsoe-eraa-2025.md) | Adequacy-Metriken LOLE/ENS | C | Abgrenzung von Blackout-Aussagen |

## Pflichtfelder jeder Karte

1. Anbieter, URL, Zugriff und Lizenz/Attribution
2. Rolle im Projekt
3. Beobachtungseinheit und Granularität
4. räumliche und zeitliche Abdeckung
5. Zielvariable bzw. mögliche Features
6. Join-Schlüssel
7. geschätztes oder gemessenes Volumen
8. Datenqualitäts-, Leakage- und Definitionsrisiken
9. Eignung für Kernmodell und Szenarioebene
10. nächster konkreter Verifikationstest
11. vorläufiges Urteil

Die tatsächlichen Dateien gehören später nach `data/raw/` oder `data/external/`; bereinigte Modelldaten nach `data/processed/`.

