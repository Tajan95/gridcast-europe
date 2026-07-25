"""Zentrale Länder- und Spaltenkonfiguration.

Ein zusätzliches Land wird bewusst hier freigeschaltet. Der Daten- und
Feature-Code bleibt davon unberührt; vor der Freigabe sind Datenqualität,
geografische Definition und Zeitzone fachlich zu prüfen.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CountrySpec:
    """Metadaten einer nationalen OPSD-Zeitreihe."""

    code: str
    name: str
    timezone: str

    @property
    def load_column(self) -> str:
        return f"{self.code}_load_actual_entsoe_transparency"

    @property
    def temperature_column(self) -> str:
        return f"{self.code}_temperature"

    @property
    def direct_radiation_column(self) -> str:
        return f"{self.code}_radiation_direct_horizontal"

    @property
    def diffuse_radiation_column(self) -> str:
        return f"{self.code}_radiation_diffuse_horizontal"

    @property
    def weather_columns(self) -> tuple[str, str, str]:
        return (
            self.temperature_column,
            self.direct_radiation_column,
            self.diffuse_radiation_column,
        )


COUNTRY_REGISTRY: dict[str, CountrySpec] = {
    "DE": CountrySpec("DE", "Deutschland", "Europe/Berlin"),
    "FR": CountrySpec("FR", "Frankreich", "Europe/Paris"),
    "PL": CountrySpec("PL", "Polen", "Europe/Warsaw"),
}

CORE_COUNTRIES: tuple[str, ...] = ("DE", "FR", "PL")


def select_country_specs(
    country_codes: tuple[str, ...] | list[str] = CORE_COUNTRIES,
) -> dict[str, CountrySpec]:
    """Gibt die angeforderten Länderspezifikationen validiert zurück."""

    unknown = sorted(set(country_codes) - set(COUNTRY_REGISTRY))
    if unknown:
        raise KeyError(
            "Nicht konfigurierte Länder: "
            f"{unknown}. Erst nach Qualitätsprüfung in COUNTRY_REGISTRY ergänzen."
        )
    return {code: COUNTRY_REGISTRY[code] for code in country_codes}
