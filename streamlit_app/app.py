"""Interaktive Knowledge-Transfer-App für GridCast Europe."""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from gridcast.config import COUNTRY_REGISTRY
from gridcast.risk import (
    empirical_extreme_probabilities,
    extreme_day_probability,
)
from gridcast.scenario import predict_scenario_day, summarize_scenario


MODEL_PATH = PROJECT_ROOT / "models" / "gridcast_final_2015_2019.joblib"
BACKTEST_PATH = PROJECT_ROOT / "data" / "app" / "backtest_2019.csv.gz"
CLIMATOLOGY_PATH = (
    PROJECT_ROOT / "data" / "app" / "weather_climatology_1980_2019.csv.gz"
)
RISK_PATH = PROJECT_ROOT / "data" / "app" / "risk_calibration_2018.npz"
K_REPORT_PATH = PROJECT_ROOT / "reports" / "k_deployment.json"

COUNTRY_LABELS = {
    code: f"{spec.name} ({code})" for code, spec in COUNTRY_REGISTRY.items()
}


st.set_page_config(
    page_title="GridCast Europe",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def load_model():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            "Das finale Modell fehlt. Erwartet wird "
            "models/gridcast_final_2015_2019.joblib."
        )
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_backtest() -> pd.DataFrame:
    return pd.read_csv(
        BACKTEST_PATH,
        parse_dates=["utc_timestamp", "local_date"],
    )


@st.cache_data
def load_climatology() -> pd.DataFrame:
    return pd.read_csv(CLIMATOLOGY_PATH)


@st.cache_data
def load_risk_calibration() -> dict[str, np.ndarray]:
    with np.load(RISK_PATH) as archive:
        return {key: archive[key] for key in archive.files}


@st.cache_data
def load_k_report() -> dict:
    return json.loads(K_REPORT_PATH.read_text(encoding="utf-8"))


def format_mw(value: float) -> str:
    return f"{value:,.0f} MW".replace(",", ".")


def format_pct(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f} %".replace(".", ",")


def render_overview() -> None:
    report = load_k_report()
    st.title("⚡ GridCast Europe")
    st.subheader("Stündliche Stromlast verstehen, prüfen und als Szenario erkunden")
    st.markdown(
        """
        GridCast verbindet einen **ehrlichen historischen Backtest** mit einer
        davon getrennten **konditionalen Zukunftsszenarioanalyse** für
        Deutschland, Frankreich und Polen.
        """
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Test-Makro-nMAE 2019", "2,71 %")
    col2.metric("Besser als Kalender-Baseline", "44,5 %")
    col3.metric("Nutzbare Länder-Stunden", "131.441")
    col4.metric("Kernländer", "3")

    st.markdown("### Was die App kann")
    left, right = st.columns(2)
    with left:
        st.markdown(
            """
            **Historischer Backtest**

            - Modell wurde nur auf 2015–2018 gefittet
            - 2019 blieb bis zur C-Phase vollständig zurückgehalten
            - Vergleich mit Istwert und Kalender-Baseline
            - Fehlerkennzahlen für einen wählbaren Tag
            """
        )
    with right:
        st.markdown(
            """
            **Zukunftsszenario**

            - typisches Wetterprofil aus 1980–2019
            - frei wählbare Temperaturabweichung
            - transparente Nachfrage- und Rechenzentrumsannahmen
            - kein behaupteter Wetterbericht oder Blackout-Risiko
            """
        )

    st.info(
        "Das finale App-Modell wurde nach der unabhängigen Testauswertung auf "
        "allen Daten von 2015–2019 refittet. Seine belastbare Güteaussage "
        "stammt weiterhin aus dem vorherigen C-Backtest."
    )
    with st.expander("Technischer Deployment-Status"):
        st.json(
            {
                "Modellartefakt": report["model"]["path"],
                "SHA-256": report["model"]["sha256"],
                "Smoke-Tests": report["verification"]["passed"],
                "App-Daten": report["app_assets"],
            },
            expanded=False,
        )


def render_backtest() -> None:
    st.title("Historischer Backtest 2019")
    st.caption(
        "Out-of-sample-Prognosen eines HGB-Modells, das für diesen Vergleich "
        "nur 2015–2018 gesehen hat."
    )
    data = load_backtest()

    country = st.selectbox(
        "Land",
        options=list(COUNTRY_LABELS),
        format_func=COUNTRY_LABELS.get,
        key="backtest_country",
    )
    country_data = data.loc[data["country"].eq(country)].copy()
    available_dates = sorted(country_data["local_date"].dt.date.unique())
    default_date = date(2019, 1, 15)
    if default_date not in available_dates:
        default_date = available_dates[0]
    selected_date = st.date_input(
        "Tag im unangetasteten Testjahr",
        value=default_date,
        min_value=available_dates[0],
        max_value=available_dates[-1],
        key="backtest_date",
    )

    day = country_data.loc[
        country_data["local_date"].dt.date.eq(selected_date)
    ].sort_values("utc_timestamp")
    if day.empty:
        st.warning("Für diesen Tag liegt kein vollständiger Backtest vor.")
        return

    actual = day["actual_load_mw"].to_numpy()
    hgb = day["hgb_prediction_mw"].to_numpy()
    calendar = day["calendar_prediction_mw"].to_numpy()
    mae = float(np.mean(np.abs(actual - hgb)))
    nmae = 100.0 * mae / float(np.mean(np.abs(actual)))
    baseline_mae = float(np.mean(np.abs(actual - calendar)))
    improvement = 100.0 * (baseline_mae - mae) / baseline_mae

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tages-MAE HGB", format_mw(mae))
    col2.metric("Tages-nMAE HGB", format_pct(nmae, 2))
    col3.metric("Verbesserung vs. Kalender", format_pct(improvement, 1))
    col4.metric("Beobachtete Stunden", str(len(day)))

    chart = day.set_index("utc_timestamp")[
        ["actual_load_mw", "hgb_prediction_mw", "calendar_prediction_mw"]
    ].rename(
        columns={
            "actual_load_mw": "Tatsächliche Last",
            "hgb_prediction_mw": "HGB-Prognose",
            "calendar_prediction_mw": "Kalender-Baseline",
        }
    )
    st.line_chart(chart, height=430, y_label="Last (MW)")

    if len(day) != 24:
        st.info(
            "Dieser lokale Kalendertag enthält aufgrund der Sommerzeitumstellung "
            f"{len(day)} statt 24 beobachtete Stunden."
        )

    with st.expander("Stundendaten anzeigen"):
        table = day[
            [
                "utc_timestamp",
                "local_hour",
                "temperature_c",
                "actual_load_mw",
                "hgb_prediction_mw",
                "calendar_prediction_mw",
            ]
        ].copy()
        table.columns = [
            "UTC-Zeit",
            "Lokale Stunde",
            "Temperatur (°C)",
            "Ist (MW)",
            "HGB (MW)",
            "Kalender (MW)",
        ]
        st.dataframe(table, hide_index=True, use_container_width=True)


def render_scenario() -> None:
    st.title("Konditionales Zukunftsszenario")
    st.caption(
        "Was-wäre-wenn-Rechnung mit typischem Wetter und transparenten "
        "Strukturannahmen – keine autonome Langfristprognose."
    )

    controls, explanation = st.columns([1, 1.45])
    with controls:
        country = st.selectbox(
            "Land",
            options=list(COUNTRY_LABELS),
            format_func=COUNTRY_LABELS.get,
            key="scenario_country",
        )
        target_date = st.date_input(
            "Szenariodatum",
            value=date(2030, 1, 15),
            min_value=date(2020, 1, 1),
            max_value=date(2050, 12, 31),
            key="scenario_date",
        )
        temperature_delta = st.slider(
            "Temperaturabweichung gegenüber dem typischen Profil (°C)",
            min_value=-5.0,
            max_value=5.0,
            value=0.0,
            step=0.5,
        )
        demand_change_pct = st.slider(
            "Strukturelle Nachfrageänderung (%)",
            min_value=-20,
            max_value=50,
            value=0,
            step=1,
        )
        data_centre_mw = st.slider(
            "Zusätzliche konstante Rechenzentrumslast (MW)",
            min_value=0,
            max_value=5_000,
            value=0,
            step=100,
        )
        quantile = st.select_slider(
            "Historische Extremzustandsschwelle",
            options=[0.95, 0.99],
            value=0.95,
            format_func=lambda value: f"{int(100 * value)}-%-Quantil",
        )

    with explanation:
        st.markdown(
            """
            **Rechenlogik**

            1. Kalendermerkmale folgen dem gewählten Datum.
            2. Wetter ist der historische Median für Land, Monat und Stunde.
            3. Die Temperaturabweichung wird *vor* der ML-Inferenz angewendet.
            4. Nachfrageänderung und Rechenzentrumslast werden *nach* der
               ML-Inferenz transparent addiert.
            """
        )
        st.warning(
            "Die Extremzustandswahrscheinlichkeit bezeichnet nur die "
            "Überschreitung einer historischen nationalen Lastschwelle. "
            "Sie ist keine Blackout-, Netzüberlastungs- oder "
            "Versorgungsausfallwahrscheinlichkeit."
        )

    model = load_model()
    climatology = load_climatology()
    scenario = predict_scenario_day(
        model,
        climatology,
        country=country,
        target_date=target_date,
        temperature_delta_c=temperature_delta,
        demand_change_fraction=demand_change_pct / 100.0,
        additional_data_centre_load_mw=data_centre_mw,
    )
    summary = summarize_scenario(scenario)

    risk = load_risk_calibration()
    threshold_key = f"threshold_q{int(100 * quantile)}_{country}"
    residual_key = f"residual_paths_{country}"
    threshold = float(risk[threshold_key][0])
    residual_paths = risk[residual_key]
    hourly_probability = empirical_extreme_probabilities(
        scenario["scenario_prediction_mw"],
        residual_paths.reshape(-1),
        threshold,
    )
    day_probability = extreme_day_probability(
        scenario["scenario_prediction_mw"],
        residual_paths,
        threshold,
    )
    scenario["extreme_state_probability"] = hourly_probability

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Spitze Basisszenario", format_mw(summary["base_peak_mw"]))
    col2.metric(
        "Spitze Gesamtszenario",
        format_mw(summary["scenario_peak_mw"]),
        delta=format_mw(summary["peak_delta_mw"]),
    )
    col3.metric(
        "Relative Spitzenänderung",
        format_pct(summary["peak_delta_pct"], 1),
    )
    col4.metric(
        "P(mind. eine Extremstunde)",
        format_pct(100 * day_probability, 1),
    )

    chart = scenario.set_index("local_hour")[
        ["base_prediction_mw", "weather_prediction_mw", "scenario_prediction_mw"]
    ].rename(
        columns={
            "base_prediction_mw": "Basisszenario",
            "weather_prediction_mw": "Nur Temperaturänderung",
            "scenario_prediction_mw": "Gesamtszenario",
        }
    )
    st.line_chart(chart, height=430, x_label="Lokale Stunde", y_label="Last (MW)")

    st.markdown(
        f"""
        **Schwellenreferenz:** {int(100 * quantile)}-%-Quantil der Last aus
        2015–2017 für {COUNTRY_REGISTRY[country].name} =
        **{format_mw(threshold)}**. Die Unsicherheit basiert auf vollständigen
        24-Stunden-Residualpfaden der Validierung 2018.
        """
    )

    with st.expander("Stündliche Szenariowerte anzeigen"):
        table = scenario[
            [
                "local_hour",
                "typical_temperature_c",
                "scenario_temperature_c",
                "base_prediction_mw",
                "weather_prediction_mw",
                "scenario_prediction_mw",
                "extreme_state_probability",
            ]
        ].copy()
        table["extreme_state_probability"] *= 100
        table.columns = [
            "Lokale Stunde",
            "Typische Temperatur (°C)",
            "Szenariotemperatur (°C)",
            "Basis (MW)",
            "Nur Wetter (MW)",
            "Gesamt (MW)",
            "P(Extremzustand) (%)",
        ]
        st.dataframe(table, hide_index=True, use_container_width=True)


def render_methodology() -> None:
    report = load_k_report()
    st.title("Methodik und Grenzen")
    st.markdown(
        """
        ### QUA³CK in fünf Schritten

        - **Q – Question:** Prognosefrage, Hypothesen und Erfolgsregeln vorab festgelegt.
        - **U – Understanding:** 131.441 Länder-Stunden aus Last- und Wetterdaten geprüft.
        - **A³ – Algorithms:** Baselines, Ridge und Histogram Gradient Boosting auf 2018 verglichen.
        - **C – Conclude:** eingefrorenes HGB einmalig auf 2019 getestet.
        - **K – Knowledge Transfer:** Modell, Szenariologik und Ergebnisse in dieser App bereitgestellt.
        """
    )

    st.markdown("### Belastbares Ergebnis")
    metrics = pd.DataFrame(
        [
            ["Ländermittelwert", "15,64 %", "triviale Referenz"],
            ["Kalender-Baseline", "4,88 %", "starke Referenz"],
            ["HGB + Feiertag + Wetter", "2,71 %", "final ausgewählt"],
        ],
        columns=["Modell", "Makro-nMAE 2019", "Rolle"],
    )
    st.dataframe(metrics, hide_index=True, use_container_width=True)

    st.markdown("### Grenzen")
    st.markdown(
        """
        - Gültig für DE, FR und PL sowie die OPSD-Periode 2015–2019.
        - Reanalysewetter im Backtest ist keine echte Wettervorhersage.
        - Regionale deutsche Feiertage sind nicht separat modelliert.
        - Zukunftsaufschläge sind Annahmen, keine kausal gelernten Langfristtrends.
        - Das refittete App-Modell hat keine neue unabhängige Testkennzahl.
        - Extremzustand bedeutet eine historische Quantilsüberschreitung,
          nicht einen Netzausfall.
        """
    )

    with st.expander("Reproduzierbarkeit"):
        st.json(report, expanded=False)


st.sidebar.title("GridCast Europe")
page = st.sidebar.radio(
    "Ansicht",
    [
        "Überblick",
        "Historischer Backtest",
        "Zukunftsszenario",
        "Methodik",
    ],
)
st.sidebar.markdown("---")
st.sidebar.caption("IU · Data Analytics und Big Data · Tajan Biazevic · 2026")

try:
    if page == "Überblick":
        render_overview()
    elif page == "Historischer Backtest":
        render_backtest()
    elif page == "Zukunftsszenario":
        render_scenario()
    else:
        render_methodology()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()
