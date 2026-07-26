"""Interaktive Knowledge-Transfer-App für GridCast Europe."""

from __future__ import annotations

from datetime import date
from importlib import invalidate_caches, reload
import json
from pathlib import Path
import sys

import altair as alt
import joblib
import numpy as np
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from gridcast.config import COUNTRY_REGISTRY
from gridcast.formatting import format_energy_mwh, format_power_mw
from gridcast.risk import (
    empirical_extreme_probabilities,
    extreme_day_probability,
)
from gridcast import scenario as scenario_logic


MODEL_PATH = PROJECT_ROOT / "models" / "gridcast_final_2015_2019.joblib"
BACKTEST_PATH = PROJECT_ROOT / "data" / "app" / "backtest_2019.csv.gz"
CLIMATOLOGY_PATH = (
    PROJECT_ROOT / "data" / "app" / "weather_climatology_1980_2019.csv.gz"
)
RISK_PATH = PROJECT_ROOT / "data" / "app" / "risk_calibration_2018.npz"
K_REPORT_PATH = PROJECT_ROOT / "reports" / "k_deployment.json"
EXPECTED_SCENARIO_API_VERSION = 2

COUNTRY_LABELS = {
    code: f"{spec.name} ({code})" for code, spec in COUNTRY_REGISTRY.items()
}
COUNTRY_SHORT_LABELS = {
    code: f"{code} · {spec.name}" for code, spec in COUNTRY_REGISTRY.items()
}
COUNTRY_NUMERIC_IDS = {"DE": "276", "FR": "250", "PL": "616"}
EUROPE_TOPOJSON_URL = (
    "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
)

NAVIGATION = [
    "🏠 Überblick",
    "🧪 Historischer Backtest",
    "🔭 Zukunftsszenario",
    "📐 Methodik",
]

SCENARIO_PRESETS = {
    "Historische Referenz": {
        "icon": "◉",
        "button_label": "Referenz",
        "temperature_delta": 0.0,
        "direct_radiation_pct": 100,
        "diffuse_radiation_pct": 100,
        "demand_change": 0,
        "data_centre_mw": 0,
        "description": "Typisches historisches Wetter, ohne Strukturaufschlag.",
    },
    "Kalter Wintertag": {
        "icon": "❄",
        "button_label": "Kalter Tag",
        "temperature_delta": -4.0,
        "direct_radiation_pct": 100,
        "diffuse_radiation_pct": 100,
        "demand_change": 0,
        "data_centre_mw": 0,
        "description": "Deutlich kälter als das typische Monatsprofil.",
    },
    "Sonniger Tag": {
        "icon": "☀",
        "button_label": "Sonniger Tag",
        "temperature_delta": 2.0,
        "direct_radiation_pct": 160,
        "diffuse_radiation_pct": 70,
        "demand_change": 0,
        "data_centre_mw": 0,
        "description": (
            "Mehr direkte und weniger diffuse Strahlung als im typischen "
            "Monatsprofil."
        ),
    },
    "Bewölkter Tag": {
        "icon": "☁",
        "button_label": "Bewölkter Tag",
        "temperature_delta": -1.0,
        "direct_radiation_pct": 35,
        "diffuse_radiation_pct": 140,
        "demand_change": 0,
        "data_centre_mw": 0,
        "description": (
            "Weniger direkte und mehr diffuse Strahlung als im typischen "
            "Monatsprofil."
        ),
    },
    "Elektrifizierung": {
        "icon": "↗",
        "button_label": "Elektrifizierung",
        "temperature_delta": 0.0,
        "direct_radiation_pct": 100,
        "diffuse_radiation_pct": 100,
        "demand_change": 15,
        "data_centre_mw": 0,
        "description": "Illustrativer struktureller Nachfrageanstieg um 15 %.",
    },
    "Rechenzentrumsboom": {
        "icon": "▦",
        "button_label": "Rechenzentren",
        "temperature_delta": 0.0,
        "direct_radiation_pct": 100,
        "diffuse_radiation_pct": 100,
        "demand_change": 0,
        "data_centre_mw": 2_000,
        "description": "Zusätzliche konstante Rechenzentrumslast von 2.000 MW.",
    },
    "Kombinierter Stresstest": {
        "icon": "⚠",
        "button_label": "Kombiniert",
        "temperature_delta": -3.0,
        "direct_radiation_pct": 50,
        "diffuse_radiation_pct": 130,
        "demand_change": 15,
        "data_centre_mw": 2_000,
        "description": (
            "Kälte, veränderte Strahlung, Elektrifizierung und Rechenzentren "
            "gemeinsam."
        ),
    },
}

SERIES_COLORS = {
    "Tatsächliche Last": "#102A43",
    "HGB-Prognose": "#078C8C",
    "Kalender-Baseline": "#D97706",
    "Referenzprofil": "#486581",
    "ML-Wetterszenario": "#4C78A8",
    "Gesamtszenario": "#D1495B",
}


st.set_page_config(
    page_title="GridCast Europe",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_visual_theme() -> None:
    """Ergänzt die Streamlit-Basisgestaltung um eine ruhige Dashboard-Hierarchie."""

    st.markdown(
        """
        <style>
        :root {
            --gc-ink: #102A43;
            --gc-muted: #52667A;
            --gc-teal: #078C8C;
            --gc-blue: #1B4F72;
            --gc-line: #D8E2EA;
            --gc-paper: rgba(255, 255, 255, 0.92);
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 92% 2%, rgba(7, 140, 140, 0.10), transparent 24rem),
                linear-gradient(180deg, #F7FAFC 0%, #EEF4F7 100%);
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1320px;
            padding-top: 4.5rem;
            padding-left: 1.6rem;
            padding-right: 1.6rem;
            padding-bottom: 4rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #102A43 0%, #173F5F 100%);
            border-right: 0;
        }

        [data-testid="stSidebar"] * {
            color: #F7FAFC;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label {
            border-radius: 0.7rem;
            padding: 0.35rem 0.55rem;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(255, 255, 255, 0.08);
        }

        [data-testid="stMetric"] {
            background: var(--gc-paper);
            border: 1px solid var(--gc-line);
            border-radius: 0.9rem;
            box-shadow: 0 8px 24px rgba(16, 42, 67, 0.06);
            padding: 1rem 1.05rem;
        }

        [data-testid="stMetricLabel"] {
            color: var(--gc-muted);
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--gc-paper);
            border-color: var(--gc-line);
            border-radius: 1rem;
            box-shadow: 0 10px 30px rgba(16, 42, 67, 0.05);
        }

        div[data-testid="stAlert"] {
            border-radius: 0.85rem;
        }

        .gc-hero {
            position: relative;
            overflow: hidden;
            padding: 2.2rem 2.35rem 2rem;
            margin-bottom: 1.35rem;
            border-radius: 1.25rem;
            color: white;
            background:
                linear-gradient(120deg, rgba(16, 42, 67, 0.98), rgba(7, 140, 140, 0.93));
            box-shadow: 0 18px 42px rgba(16, 42, 67, 0.16);
        }

        .gc-hero::after {
            content: "";
            position: absolute;
            width: 18rem;
            height: 18rem;
            right: -5rem;
            top: -8rem;
            border: 1px solid rgba(255, 255, 255, 0.20);
            border-radius: 50%;
            box-shadow:
                0 0 0 3rem rgba(255, 255, 255, 0.035),
                0 0 0 6rem rgba(255, 255, 255, 0.025);
        }

        .gc-eyebrow {
            position: relative;
            z-index: 1;
            display: inline-block;
            margin-bottom: 0.7rem;
            color: #BEE8E7;
            font-size: 0.78rem;
            font-weight: 750;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .gc-hero h1 {
            position: relative;
            z-index: 1;
            margin: 0;
            color: white;
            font-size: clamp(2.2rem, 5vw, 4rem);
            letter-spacing: -0.04em;
        }

        .gc-hero p {
            position: relative;
            z-index: 1;
            max-width: 53rem;
            margin: 0.75rem 0 0;
            color: #EAF7F7;
            font-size: 1.08rem;
            line-height: 1.65;
        }

        .gc-section-kicker {
            margin-bottom: 0.2rem;
            color: var(--gc-teal);
            font-size: 0.76rem;
            font-weight: 750;
            letter-spacing: 0.11em;
            text-transform: uppercase;
        }

        .gc-country-code {
            display: inline-flex;
            width: 2.4rem;
            height: 2.4rem;
            align-items: center;
            justify-content: center;
            margin-right: 0.65rem;
            border-radius: 0.7rem;
            color: white;
            background: var(--gc-teal);
            font-weight: 800;
        }

        .gc-note {
            color: var(--gc-muted);
            font-size: 0.87rem;
            line-height: 1.55;
        }

        .st-key-scenario_results {
            position: sticky;
            top: 4.75rem;
            z-index: 2;
        }

        .st-key-scenario_controls [data-testid="stVerticalBlock"] {
            gap: 0.62rem;
        }

        .st-key-scenario_controls [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 0.72rem 0.82rem;
            border-radius: 0.8rem;
        }

        .st-key-scenario_controls h3 {
            margin: 0;
            padding: 0;
            font-size: 1.35rem;
        }

        .st-key-scenario_controls h4 {
            margin: 0;
            padding: 0;
            font-size: 1.02rem;
        }

        .st-key-scenario_controls
        [data-testid="stMarkdownContainer"]:has(h4) {
            padding-bottom: 0.46rem;
        }

        .st-key-scenario_controls
        [data-testid="stMarkdownContainer"]:has(h3) {
            padding-bottom: 0.34rem;
        }

        .st-key-scenario_controls [data-testid="stCaptionContainer"] p {
            font-size: 0.76rem;
            line-height: 1.3;
        }

        .st-key-scenario_controls [data-testid="stWidgetLabel"] p {
            font-size: 0.82rem;
            line-height: 1.25;
        }

        .st-key-scenario_presets button {
            min-height: 2.45rem;
            padding: 0.3rem 0.38rem;
        }

        .st-key-scenario_presets button p {
            font-size: 0.77rem;
            line-height: 1.15;
        }

        .st-key-scenario_presets [data-testid="stAlert"] {
            padding: 0.55rem 0.68rem;
        }

        .st-key-scenario_presets [data-testid="stAlert"] p {
            font-size: 0.78rem;
            line-height: 1.3;
        }

        .st-key-scenario_results h3 {
            margin: 0;
            padding: 0;
            font-size: 1.35rem;
        }

        .st-key-scenario_results
        [data-testid="stMarkdownContainer"]:has(h3) {
            padding-bottom: 0.46rem;
        }

        .st-key-scenario_results [data-testid="stMetric"] {
            min-height: 0;
            padding: 0.62rem 0.72rem;
            border-radius: 0.75rem;
            box-shadow: 0 5px 16px rgba(16, 42, 67, 0.05);
        }

        .st-key-scenario_results [data-testid="stMetricLabel"] p {
            font-size: 0.76rem;
            line-height: 1.2;
        }

        .st-key-scenario_results [data-testid="stMetricValue"] {
            font-size: 1.62rem;
            line-height: 1.2;
        }

        .st-key-scenario_results [data-testid="stMetricDelta"] {
            font-size: 0.72rem;
        }

        h1, h2, h3 {
            color: var(--gc-ink);
            letter-spacing: -0.02em;
        }

        hr {
            border-color: var(--gc-line);
        }

        @media (max-width: 850px) {
            .gc-hero {
                padding: 1.6rem 1.4rem;
            }

            .st-key-scenario_results {
                position: static;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_scenario_page_width() -> None:
    """Nutzt nur für die informationsreiche Szenarioseite mehr Breite."""

    st.markdown(
        """
        <style>
        [data-testid="stMainBlockContainer"] {
            max-width: 1680px;
        }
        </style>
        """,
        unsafe_allow_html=True,
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


def get_scenario_logic():
    """Lädt bei einem Cloud-Hot-Reload garantiert die aktuelle Szenario-API."""

    if (
        getattr(scenario_logic, "SCENARIO_API_VERSION", 0)
        < EXPECTED_SCENARIO_API_VERSION
    ):
        invalidate_caches()
        reload(scenario_logic)
    if (
        getattr(scenario_logic, "SCENARIO_API_VERSION", 0)
        < EXPECTED_SCENARIO_API_VERSION
    ):
        raise RuntimeError(
            "App- und Szenariomodul besitzen unterschiedliche Versionen. "
            "Bitte die Streamlit-App neu starten."
        )
    return scenario_logic


@st.cache_data
def build_country_overview() -> pd.DataFrame:
    """Verdichtet die unangetasteten 2019-Daten für Karte und Tooltips."""

    data = load_backtest()
    data = data.assign(
        absolute_error_mw=(
            data["actual_load_mw"] - data["hgb_prediction_mw"]
        ).abs()
    )
    result = (
        data.groupby("country", as_index=False)
        .agg(
            teststunden=("actual_load_mw", "size"),
            mittlere_last_mw=("actual_load_mw", "mean"),
            spitzenlast_mw=("actual_load_mw", "max"),
            mae_mw=("absolute_error_mw", "mean"),
        )
        .assign(
            nmae_pct=lambda frame: (
                100 * frame["mae_mw"] / frame["mittlere_last_mw"]
            ),
            numeric_id=lambda frame: frame["country"].map(COUNTRY_NUMERIC_IDS),
            land=lambda frame: frame["country"].map(
                {code: spec.name for code, spec in COUNTRY_REGISTRY.items()}
            ),
        )
    )
    return result


def format_mw(value: float) -> str:
    return f"{value:,.0f} MW".replace(",", ".")


def format_pct(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f} %".replace(".", ",")


def format_hour(value: int | float) -> str:
    return f"{int(value):02d}:00 Uhr"


def render_page_header(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="gc-section-kicker">{kicker}</div>
        <h1 style="margin:0 0 .35rem 0;">{title}</h1>
        <p style="margin:0 0 1.25rem;color:#52667A;font-size:1.03rem;">
            {subtitle}
        </p>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    st.sidebar.markdown(
        """
        <div style="padding:.65rem .2rem 1rem;">
            <div style="font-size:.74rem;letter-spacing:.13em;
                        text-transform:uppercase;color:#A9D9D8;">
                GridCast Europe
            </div>
            <div style="font-size:1.55rem;font-weight:780;margin-top:.2rem;">
                Stromlast im Kontext
            </div>
            <div style="font-size:.82rem;color:#C9D9E5;margin-top:.35rem;">
                Historischer Test · Konditionale Szenarien
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    page = st.sidebar.radio(
        "Ansicht",
        NAVIGATION,
        key="page",
        label_visibility="collapsed",
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size:.78rem;color:#C9D9E5;line-height:1.55;">
            <b>Modellfenster</b><br>
            2015–2019 · DE / FR / PL<br><br>
            <b>Prüfungsprojekt</b><br>
            IU · Data Analytics und Big Data
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.caption("Tajan Biazevic · 2026")
    return page


def navigate_to(page: str, country: str, country_key: str) -> None:
    st.session_state[country_key] = country
    st.session_state["page"] = page


def build_europe_map(country_data: pd.DataFrame) -> alt.Chart:
    world = alt.topo_feature(EUROPE_TOPOJSON_URL, "countries")
    lookup = alt.LookupData(
        country_data,
        "numeric_id",
        [
            "country",
            "land",
            "nmae_pct",
            "mittlere_last_mw",
            "spitzenlast_mw",
            "teststunden",
        ],
    )
    selection = alt.selection_point(
        name="country_pick",
        fields=["country"],
        on="click",
        clear=False,
    )

    map_chart = (
        alt.Chart(world)
        .mark_geoshape(stroke="#FFFFFF", strokeWidth=0.75)
        .transform_lookup(lookup="id", from_=lookup)
        .encode(
            color=alt.condition(
                "isValid(datum.country)",
                alt.Color(
                    "nmae_pct:Q",
                    title="Test-nMAE 2019 (%)",
                    scale=alt.Scale(
                        domain=[2.4, 3.0],
                        range=["#69C2BF", "#075985"],
                    ),
                    legend=alt.Legend(
                        orient="bottom",
                        direction="horizontal",
                        gradientLength=180,
                    ),
                ),
                alt.value("#E2EAF0"),
            ),
            opacity=alt.condition(
                selection,
                alt.value(1),
                alt.value(0.82),
            ),
            tooltip=[
                alt.Tooltip("land:N", title="Land"),
                alt.Tooltip("country:N", title="Code"),
                alt.Tooltip(
                    "nmae_pct:Q",
                    title="Test-nMAE",
                    format=".2f",
                ),
                alt.Tooltip(
                    "mittlere_last_mw:Q",
                    title="Mittlere Last (MW)",
                    format=",.0f",
                ),
                alt.Tooltip(
                    "spitzenlast_mw:Q",
                    title="Spitzenlast (MW)",
                    format=",.0f",
                ),
                alt.Tooltip(
                    "teststunden:Q",
                    title="Teststunden 2019",
                    format=",.0f",
                ),
            ],
        )
        .add_params(selection)
    )
    return (
        map_chart
        .project(
            type="mercator",
            center=[10, 52],
            scale=520,
        )
        .properties(height=430)
        .configure_view(stroke=None)
    )


def extract_map_country(event) -> str | None:
    """Liest eine optionale Altair-Auswahl defensiv aus."""

    selection = getattr(event, "selection", None)
    if selection is None and isinstance(event, dict):
        selection = event.get("selection")
    if not selection:
        return None
    values = selection.get("country_pick", [])
    if not values:
        return None
    first = values[0] if isinstance(values, list) else values
    if isinstance(first, dict):
        country = first.get("country")
        if country in COUNTRY_REGISTRY:
            return country
    return None


def render_overview() -> None:
    st.markdown(
        """
        <div class="gc-hero">
            <div class="gc-eyebrow">QUA³CK · Knowledge Transfer</div>
            <h1>GridCast Europe</h1>
            <p>
                Stündliche Stromlast für Deutschland, Frankreich und Polen –
                mit unabhängigem Backtest, konditionalen Zukunftsszenarien
                und transparenten Grenzen.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Test-Makro-nMAE 2019",
        "2,71 %",
        help=(
            "nMAE = normalisierter mittlerer absoluter Fehler. Für jedes Land "
            "wird der MAE durch dessen mittlere tatsächliche Last geteilt; "
            "Makro bezeichnet den gleichgewichteten Mittelwert von DE, FR und "
            "PL. Je kleiner, desto besser. Gemessen im unangetasteten Testjahr "
            "2019."
        ),
    )
    col2.metric(
        "Fehlerreduktion vs. Kalender",
        "44,5 %",
        help=(
            "Relative Verringerung des Test-Makro-nMAE gegenüber der starken "
            "Kalender-Baseline: von 4,88 % auf 2,71 %. Ein positiver Wert "
            "bedeutet, dass das HGB-Modell genauer ist."
        ),
    )
    col3.metric(
        "Teststunden 2019",
        "26.275",
        help=(
            "Anzahl der nach der Datenqualitätsprüfung auswertbaren "
            "Länder-Stunden im unabhängigen Testjahr 2019, zusammengezählt "
            "für Deutschland, Frankreich und Polen."
        ),
    )
    col4.metric(
        "Freigegebene Länder",
        "3",
        help=(
            "Deutschland, Frankreich und Polen erfüllten die festgelegten "
            "Datenqualitätsanforderungen und gingen in die Modellauswertung ein."
        ),
    )

    st.markdown("## Europas Lastprofile im Modell")
    st.caption(
        "DE, FR und PL sind nach vollständiger Qualitätsprüfung freigegeben. "
        "Farbe = Modellfehler im unangetasteten Testjahr 2019."
    )

    if "overview_country" not in st.session_state:
        st.session_state["overview_country"] = "DE"

    map_col, detail_col = st.columns([1.65, 0.85], gap="large")
    country_data = build_country_overview()
    with map_col:
        map_event = st.altair_chart(
            build_europe_map(country_data),
            use_container_width=True,
            on_select="rerun",
            selection_mode=["country_pick"],
            key="europe_country_map",
        )
        picked_country = extract_map_country(map_event)
        if (
            picked_country is not None
            and picked_country != st.session_state["overview_country"]
        ):
            st.session_state["overview_country"] = picked_country
            st.rerun()
        st.caption(
            "Interaktiv: Land anklicken oder mit der Maus berühren, um "
            "Testgüte, Lastniveau und Datenumfang zu sehen."
        )

    with detail_col:
        with st.container(border=True):
            focus = st.radio(
                "Fokusland",
                options=list(COUNTRY_REGISTRY),
                format_func=lambda code: COUNTRY_SHORT_LABELS[code],
                key="overview_country",
                horizontal=True,
            )
            row = country_data.loc[country_data["country"].eq(focus)].iloc[0]
            st.markdown(
                f"""
                <div style="margin:.35rem 0 .9rem;">
                    <span class="gc-country-code">{focus}</span>
                    <b style="font-size:1.12rem;">{row["land"]}</b>
                </div>
                """,
                unsafe_allow_html=True,
            )
            metric_left, metric_right = st.columns(2)
            metric_left.metric(
                "Test-nMAE",
                format_pct(row["nmae_pct"], 2),
                help=(
                    "Normalisierter mittlerer absoluter Fehler des gewählten "
                    "Landes im Testjahr 2019: MAE geteilt durch die mittlere "
                    "tatsächliche Last. Je kleiner, desto besser."
                ),
            )
            metric_right.metric(
                "Mittlere Last (MW)",
                f"{row['mittlere_last_mw']:,.0f}".replace(",", "."),
                help=(
                    "Durchschnitt der tatsächlich beobachteten stündlichen "
                    "Stromlast des gewählten Landes im Testjahr 2019. "
                    "MW = Megawatt."
                ),
            )
            st.markdown(
                f"""
                <div class="gc-note" style="margin:.8rem 0 1rem;">
                    <b>{int(row["teststunden"]):,}</b> Teststunden ·
                    beobachtete Spitze <b>{format_mw(row["spitzenlast_mw"])}</b>
                </div>
                """.replace(",", "."),
                unsafe_allow_html=True,
            )
            backtest_button, scenario_button = st.columns(2)
            backtest_button.button(
                "Backtest öffnen",
                width="stretch",
                on_click=navigate_to,
                args=("🧪 Historischer Backtest", focus, "backtest_country"),
            )
            scenario_button.button(
                "Szenario öffnen",
                width="stretch",
                type="primary",
                on_click=navigate_to,
                args=("🔭 Zukunftsszenario", focus, "scenario_country"),
            )

    st.markdown("## Zwei strikt getrennte Analysewege")
    backtest_col, scenario_col = st.columns(2, gap="large")
    with backtest_col:
        with st.container(border=True):
            st.markdown("### 🧪 Historischer Backtest")
            st.markdown(
                """
                **Die belastbare Qualitätsaussage.** Das Modell wurde für
                diesen Vergleich nur auf 2015–2018 gefittet. 2019 blieb bis
                zur C-Phase vollständig zurückgehalten.
                """
            )
            st.caption("Istwert · HGB-Prognose · Kalender-Baseline")
    with scenario_col:
        with st.container(border=True):
            st.markdown("### 🔭 Konditionales Zukunftsszenario")
            st.markdown(
                """
                **Die transparente Was-wäre-wenn-Rechnung.** Historische
                Wetterprofile werden über Temperatur sowie direkte und
                diffuse Strahlung verändert und mit transparenten
                Strukturannahmen kombiniert.
                """
            )
            st.caption("Szenarien sind Stressannahmen, keine Zukunftsprognosen.")

    st.info(
        "Das App-Modell wurde nach der unabhängigen Auswertung auf 2015–2019 "
        "refittet. Die belastbare Güteaussage von 2,71 % stammt weiterhin aus "
        "dem vorherigen C-Backtest."
    )


def build_backtest_chart(day: pd.DataFrame) -> alt.Chart:
    chart_data = (
        day[
            [
                "utc_timestamp",
                "actual_load_mw",
                "hgb_prediction_mw",
                "calendar_prediction_mw",
            ]
        ]
        .rename(
            columns={
                "actual_load_mw": "Tatsächliche Last",
                "hgb_prediction_mw": "HGB-Prognose",
                "calendar_prediction_mw": "Kalender-Baseline",
            }
        )
        .melt(
            id_vars="utc_timestamp",
            var_name="Reihe",
            value_name="Last_MW",
        )
    )
    order = [
        "Tatsächliche Last",
        "HGB-Prognose",
        "Kalender-Baseline",
    ]
    nearest = alt.selection_point(
        name="hover",
        nearest=True,
        on="pointerover",
        fields=["utc_timestamp"],
        empty=False,
    )
    base = alt.Chart(chart_data).encode(
        x=alt.X(
            "utc_timestamp:T",
            title="UTC-Zeit",
            axis=alt.Axis(format="%H:%M", labelAngle=0),
        ),
        y=alt.Y(
            "Last_MW:Q",
            title="Last (MW)",
            scale=alt.Scale(zero=False),
        ),
        color=alt.Color(
            "Reihe:N",
            title=None,
            scale=alt.Scale(
                domain=order,
                range=[SERIES_COLORS[name] for name in order],
            ),
            sort=order,
            legend=alt.Legend(orient="top", direction="horizontal"),
        ),
        strokeDash=alt.StrokeDash(
            "Reihe:N",
            title=None,
            scale=alt.Scale(
                domain=order,
                range=[[1, 0], [1, 0], [8, 5]],
            ),
            sort=order,
            legend=None,
        ),
    )
    lines = base.mark_line(strokeWidth=2.7).encode(
        tooltip=[
            alt.Tooltip(
                "utc_timestamp:T",
                title="Zeit",
                format="%d.%m.%Y %H:%M",
            ),
            alt.Tooltip("Reihe:N", title="Reihe"),
            alt.Tooltip("Last_MW:Q", title="Last (MW)", format=",.0f"),
        ]
    )
    selectors = (
        alt.Chart(chart_data)
        .mark_point(opacity=0)
        .encode(x="utc_timestamp:T")
        .add_params(nearest)
    )
    points = base.mark_point(filled=True, size=75).encode(
        opacity=alt.condition(
            nearest,
            alt.value(1),
            alt.value(0),
        )
    )
    rule = (
        alt.Chart(chart_data)
        .mark_rule(color="#91A4B7")
        .encode(
            x="utc_timestamp:T",
            opacity=alt.condition(
                nearest,
                alt.value(0.55),
                alt.value(0),
            ),
        )
        .transform_filter(nearest)
    )
    return (
        (lines + selectors + points + rule)
        .properties(height=440)
        .configure_view(stroke=None)
        .configure_axis(gridColor="#E5ECF1", domainColor="#B8C7D2")
    )


def render_backtest() -> None:
    render_page_header(
        "C · Conclude & Compare",
        "Historischer Backtest 2019",
        "Out-of-sample-Prognosen eines HGB-Modells, das für diesen Vergleich "
        "nur 2015–2018 gesehen hat.",
    )
    data = load_backtest()

    with st.container(border=True):
        country_col, date_col, note_col = st.columns([1, 1, 1.35])
        with country_col:
            country = st.radio(
                "Land",
                options=list(COUNTRY_REGISTRY),
                format_func=lambda code: COUNTRY_SHORT_LABELS[code],
                key="backtest_country",
                horizontal=True,
            )
        country_data = data.loc[data["country"].eq(country)].copy()
        available_dates = sorted(country_data["local_date"].dt.date.unique())
        default_date = date(2019, 1, 15)
        if default_date not in available_dates:
            default_date = available_dates[0]
        with date_col:
            selected_date = st.date_input(
                "Tag im unangetasteten Testjahr",
                value=default_date,
                min_value=available_dates[0],
                max_value=available_dates[-1],
                key="backtest_date",
                format="DD.MM.YYYY",
            )
        with note_col:
            st.markdown(
                """
                <div class="gc-note" style="padding-top:1.75rem;">
                    <b>Leselogik:</b> Dunkel = Istwert, Türkis = HGB,
                    orange gestrichelt = starke Kalender-Baseline.
                    Hover zeigt die exakten Stundenwerte.
                </div>
                """,
                unsafe_allow_html=True,
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
    largest_error_index = int(np.argmax(np.abs(actual - hgb)))
    largest_error_hour = int(day.iloc[largest_error_index]["local_hour"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Tages-MAE HGB",
        format_mw(mae),
        help=(
            "MAE = mittlerer absoluter Fehler. Angezeigt wird die mittlere "
            "absolute Differenz zwischen Ist-Last und HGB-Prognose über alle "
            "Stunden des gewählten Tages, gemessen in MW. HGB steht für "
            "Histogram Gradient Boosting, das verwendete Regressionsmodell. "
            "Je kleiner, desto besser."
        ),
    )
    col2.metric(
        "Tages-nMAE HGB",
        format_pct(nmae, 2),
        help=(
            "nMAE = normalisierter MAE. Der Tages-MAE des HGB wird durch die "
            "mittlere tatsächliche Last desselben Tages geteilt. Die "
            "Prozentzahl ist dadurch zwischen unterschiedlich großen Ländern "
            "und Tagen besser vergleichbar. Je kleiner, desto besser."
        ),
    )
    col3.metric(
        "Fehlerreduktion vs. Kalender",
        format_pct(improvement, 1),
        help=(
            "Relative Verringerung des Tages-MAE gegenüber einer starken "
            "Kalender-Baseline ohne Wettermerkmale. Ein positiver Wert "
            "bedeutet, dass das HGB an diesem Tag genauer prognostiziert."
        ),
    )
    col4.metric(
        "Größte Abweichung um",
        format_hour(largest_error_hour),
        help=(
            "Lokale Stunde, in der die absolute Differenz zwischen Ist-Last "
            "und HGB-Prognose am gewählten Tag am größten ist."
        ),
    )

    st.altair_chart(
        build_backtest_chart(day),
        use_container_width=True,
    )

    if len(day) != 24:
        st.info(
            "Dieser lokale Kalendertag enthält aufgrund der Sommerzeitumstellung "
            f"{len(day)} statt 24 beobachtete Stunden."
        )

    with st.expander("Stundendaten und exakte Fehlerwerte", expanded=True):
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
        table["HGB-Fehler (MW)"] = (
            table["actual_load_mw"] - table["hgb_prediction_mw"]
        ).abs()
        table.columns = [
            "UTC-Zeit",
            "Lokale Stunde",
            "Temperatur (°C)",
            "Ist (MW)",
            "HGB (MW)",
            "Kalender (MW)",
            "HGB-Fehler (MW)",
        ]
        st.dataframe(
            table.style.format(
                {
                    "Temperatur (°C)": "{:.1f}",
                    "Ist (MW)": "{:,.0f}",
                    "HGB (MW)": "{:,.0f}",
                    "Kalender (MW)": "{:,.0f}",
                    "HGB-Fehler (MW)": "{:,.0f}",
                }
            ),
            hide_index=True,
            width="stretch",
        )


def initialize_scenario_state() -> None:
    if "scenario_preset" not in st.session_state:
        st.session_state["scenario_preset"] = "Historische Referenz"
    preset = SCENARIO_PRESETS[st.session_state["scenario_preset"]]
    st.session_state.setdefault(
        "scenario_temperature_delta",
        preset["temperature_delta"],
    )
    st.session_state.setdefault(
        "scenario_direct_radiation_pct",
        preset["direct_radiation_pct"],
    )
    st.session_state.setdefault(
        "scenario_diffuse_radiation_pct",
        preset["diffuse_radiation_pct"],
    )
    st.session_state.setdefault(
        "scenario_demand_change",
        preset["demand_change"],
    )
    st.session_state.setdefault(
        "scenario_data_centre_mw",
        preset["data_centre_mw"],
    )
    st.session_state.setdefault("scenario_quantile", 0.99)


def apply_scenario_preset(name: str) -> None:
    st.session_state["scenario_preset"] = name
    preset = SCENARIO_PRESETS[name]
    st.session_state["scenario_temperature_delta"] = preset[
        "temperature_delta"
    ]
    st.session_state["scenario_direct_radiation_pct"] = preset[
        "direct_radiation_pct"
    ]
    st.session_state["scenario_diffuse_radiation_pct"] = preset[
        "diffuse_radiation_pct"
    ]
    st.session_state["scenario_demand_change"] = preset["demand_change"]
    st.session_state["scenario_data_centre_mw"] = preset["data_centre_mw"]


def set_scenario_quantile(quantile: float) -> None:
    st.session_state["scenario_quantile"] = quantile


def build_scenario_chart(scenario: pd.DataFrame) -> alt.Chart:
    chart_data = (
        scenario[
            [
                "local_hour",
                "base_prediction_mw",
                "weather_prediction_mw",
                "scenario_prediction_mw",
            ]
        ]
        .rename(
            columns={
                "base_prediction_mw": "Referenzprofil",
                "weather_prediction_mw": "ML-Wetterszenario",
                "scenario_prediction_mw": "Gesamtszenario",
            }
        )
        .melt(
            id_vars="local_hour",
            var_name="Reihe",
            value_name="Last_MW",
        )
    )
    order = [
        "Referenzprofil",
        "ML-Wetterszenario",
        "Gesamtszenario",
    ]
    return (
        alt.Chart(chart_data)
        .mark_line(point=alt.OverlayMarkDef(size=45), strokeWidth=2.8)
        .encode(
            x=alt.X(
                "local_hour:Q",
                title="Lokale Stunde",
                scale=alt.Scale(domain=[0, 23]),
                axis=alt.Axis(values=list(range(0, 24, 2))),
            ),
            y=alt.Y(
                "Last_MW:Q",
                title="Last (MW)",
                scale=alt.Scale(zero=False),
            ),
            color=alt.Color(
                "Reihe:N",
                title=None,
                scale=alt.Scale(
                    domain=order,
                    range=[SERIES_COLORS[name] for name in order],
                ),
                sort=order,
                legend=alt.Legend(orient="top", direction="horizontal"),
            ),
            strokeDash=alt.StrokeDash(
                "Reihe:N",
                title=None,
                scale=alt.Scale(
                    domain=order,
                    range=[[7, 4], [3, 3], [1, 0]],
                ),
                sort=order,
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("local_hour:Q", title="Lokale Stunde"),
                alt.Tooltip("Reihe:N", title="Reihe"),
                alt.Tooltip("Last_MW:Q", title="Last (MW)", format=",.0f"),
            ],
        )
        .properties(height=440)
        .configure_view(stroke=None)
        .configure_axis(gridColor="#E5ECF1", domainColor="#B8C7D2")
    )


def build_temperature_input_chart(scenario: pd.DataFrame) -> alt.Chart:
    """Vergleicht typisches und gewähltes Temperaturprofil."""

    chart_data = (
        scenario[
            [
                "local_hour",
                "typical_temperature_c",
                "scenario_temperature_c",
            ]
        ]
        .rename(
            columns={
                "typical_temperature_c": "Typisches Profil",
                "scenario_temperature_c": "Gewähltes Wetter",
            }
        )
        .melt(
            id_vars="local_hour",
            var_name="Profil",
            value_name="Temperatur_C",
        )
    )
    order = ["Typisches Profil", "Gewähltes Wetter"]
    return (
        alt.Chart(chart_data)
        .mark_line(point=alt.OverlayMarkDef(size=35), strokeWidth=2.5)
        .encode(
            x=alt.X(
                "local_hour:Q",
                title="Lokale Stunde",
                scale=alt.Scale(domain=[0, 23]),
                axis=alt.Axis(values=list(range(0, 24, 3))),
            ),
            y=alt.Y(
                "Temperatur_C:Q",
                title="Temperatur (°C)",
                scale=alt.Scale(zero=False),
            ),
            color=alt.Color(
                "Profil:N",
                title=None,
                scale=alt.Scale(
                    domain=order,
                    range=["#486581", "#D1495B"],
                ),
                sort=order,
                legend=alt.Legend(orient="top", direction="horizontal"),
            ),
            strokeDash=alt.StrokeDash(
                "Profil:N",
                title=None,
                scale=alt.Scale(domain=order, range=[[7, 4], [1, 0]]),
                sort=order,
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("local_hour:Q", title="Lokale Stunde"),
                alt.Tooltip("Profil:N", title="Profil"),
                alt.Tooltip(
                    "Temperatur_C:Q",
                    title="Temperatur (°C)",
                    format=".1f",
                ),
            ],
        )
        .properties(height=320, title="Temperaturprofil")
    )


def build_radiation_input_chart(scenario: pd.DataFrame) -> alt.Chart:
    """Vergleicht direkte und diffuse Strahlung vor der ML-Inferenz."""

    parts = []
    for radiation_type, typical_column, scenario_column in [
        (
            "Direkte Strahlung",
            "typical_direct_radiation_wm2",
            "scenario_direct_radiation_wm2",
        ),
        (
            "Diffuse Strahlung",
            "typical_diffuse_radiation_wm2",
            "scenario_diffuse_radiation_wm2",
        ),
    ]:
        for profile, column in [
            ("Typisches Profil", typical_column),
            ("Gewähltes Wetter", scenario_column),
        ]:
            part = scenario[["local_hour", column]].copy()
            part.rename(columns={column: "Strahlung_Wm2"}, inplace=True)
            part["Strahlungsart"] = radiation_type
            part["Profil"] = profile
            parts.append(part)
    chart_data = pd.concat(parts, ignore_index=True)

    return (
        alt.Chart(chart_data)
        .mark_line(point=alt.OverlayMarkDef(size=30), strokeWidth=2.4)
        .encode(
            x=alt.X(
                "local_hour:Q",
                title="Lokale Stunde",
                scale=alt.Scale(domain=[0, 23]),
                axis=alt.Axis(values=list(range(0, 24, 3))),
            ),
            y=alt.Y(
                "Strahlung_Wm2:Q",
                title="Strahlung (W/m²)",
            ),
            color=alt.Color(
                "Strahlungsart:N",
                title=None,
                scale=alt.Scale(
                    domain=["Direkte Strahlung", "Diffuse Strahlung"],
                    range=["#D97706", "#078C8C"],
                ),
                legend=alt.Legend(orient="top", direction="horizontal"),
            ),
            strokeDash=alt.StrokeDash(
                "Profil:N",
                title=None,
                scale=alt.Scale(
                    domain=["Typisches Profil", "Gewähltes Wetter"],
                    range=[[7, 4], [1, 0]],
                ),
                legend=alt.Legend(
                    orient="bottom",
                    direction="horizontal",
                    columns=2,
                ),
            ),
            tooltip=[
                alt.Tooltip("local_hour:Q", title="Lokale Stunde"),
                alt.Tooltip("Strahlungsart:N", title="Strahlungsart"),
                alt.Tooltip("Profil:N", title="Profil"),
                alt.Tooltip(
                    "Strahlung_Wm2:Q",
                    title="Strahlung (W/m²)",
                    format=",.1f",
                ),
            ],
        )
        .properties(height=320, title="Strahlungsprofile")
    )


def render_scenario() -> None:
    apply_scenario_page_width()
    render_page_header(
        "K · Knowledge Transfer",
        "Konditionales Zukunftsszenario",
        "Was-wäre-wenn-Rechnung mit typischem Wetter und transparenten "
        "Strukturannahmen – keine autonome Langfristprognose.",
    )
    initialize_scenario_state()

    workspace = st.container(key="scenario_workspace")
    with workspace:
        control_col, result_col = st.columns([0.95, 1.55], gap="large")
    control_panel = control_col.container(key="scenario_controls")
    result_panel = result_col.container(key="scenario_results")

    with control_panel:
        st.markdown("### Szenario konfigurieren")
        with st.container(border=True, key="scenario_presets"):
            st.markdown("#### Vordefinierte Stressannahmen")
            st.caption(
                "Preset wählen und die Annahmen anschließend feinjustieren."
            )
            preset_items = list(SCENARIO_PRESETS.items())
            for row_start in range(0, len(preset_items), 4):
                preset_columns = st.columns(4, gap="small")
                for column, (index, (name, preset)) in zip(
                    preset_columns,
                    enumerate(
                        preset_items[row_start : row_start + 4],
                        row_start,
                    ),
                ):
                    with column:
                        st.button(
                            f"{preset['icon']} {preset['button_label']}",
                            key=f"scenario_preset_{index}",
                            type=(
                                "primary"
                                if st.session_state["scenario_preset"] == name
                                else "secondary"
                            ),
                            width="stretch",
                            on_click=apply_scenario_preset,
                            args=(name,),
                        )
            active_preset = SCENARIO_PRESETS[
                st.session_state["scenario_preset"]
            ]
            st.info(active_preset["description"], icon="💡")

        with st.container(border=True, key="scenario_ml_inputs"):
            st.markdown("#### 1 · Direkte ML-Eingaben")
            st.caption(
                "Land, Datum und Wetter bauen die Feature-Matrix neu auf und "
                "lösen eine HGB-Inferenz aus."
            )
            identity_col, date_col = st.columns(2, gap="small")
            with identity_col:
                country = st.radio(
                    "Land",
                    options=list(COUNTRY_REGISTRY),
                    format_func=lambda code: code,
                    key="scenario_country",
                    horizontal=True,
                    help="DE = Deutschland, FR = Frankreich, PL = Polen.",
                )
            with date_col:
                target_date = st.date_input(
                    "Szenariodatum",
                    value=date(2030, 1, 15),
                    min_value=date(2020, 1, 1),
                    max_value=date(2050, 12, 31),
                    key="scenario_date",
                    format="DD.MM.YYYY",
                )
            temp_col, direct_col, diffuse_col = st.columns(3, gap="small")
            with temp_col:
                temperature_delta = st.slider(
                    "Temperaturabweichung (°C)",
                    min_value=-5.0,
                    max_value=5.0,
                    step=0.5,
                    key="scenario_temperature_delta",
                    help="Abweichung vom historischen Monatsmedian.",
                )
            with direct_col:
                direct_radiation_pct = st.slider(
                    "Direkte Sonneneinstrahlung",
                    min_value=0,
                    max_value=200,
                    step=5,
                    key="scenario_direct_radiation_pct",
                    format="%d %%",
                    help=(
                        "Direkte Strahlung trifft ungestreut aus Sonnenrichtung "
                        "auf eine horizontale Fläche; die Modellwerte werden in "
                        "W/m² gemessen. 100 % übernimmt für jede lokale Stunde "
                        "den historischen Median für Land und Monat aus "
                        "1980–2019. Beispielsweise multiplizieren 150 % jeden "
                        "der 24 stündlichen Medianwerte mit 1,5."
                    ),
                )
            with diffuse_col:
                diffuse_radiation_pct = st.slider(
                    "Diffuse Sonneneinstrahlung",
                    min_value=0,
                    max_value=200,
                    step=5,
                    key="scenario_diffuse_radiation_pct",
                    format="%d %%",
                    help=(
                        "Diffuse Strahlung erreicht eine horizontale Fläche "
                        "nach Streuung durch Atmosphäre und Wolken; die "
                        "Modellwerte werden in W/m² gemessen. 100 % übernimmt "
                        "für jede lokale Stunde den historischen Median für "
                        "Land und Monat aus 1980–2019. Beispielsweise "
                        "multiplizieren 150 % jeden der 24 stündlichen "
                        "Medianwerte mit 1,5."
                    ),
                )

        assumption_col, evaluation_col = st.columns(2, gap="small")
        with assumption_col:
            with st.container(
                border=True,
                key="scenario_structure_inputs",
                height="stretch",
            ):
                st.markdown("#### 2 · Explizite Strukturannahmen")
                st.caption(
                    "Nicht gelernt: nach der ML-Inferenz transparent angewendet."
                )
                demand_change_pct = st.slider(
                    "Nachfrageänderung (%)",
                    min_value=-20,
                    max_value=50,
                    step=1,
                    key="scenario_demand_change",
                    help="Transparenter Strukturaufschlag nach der ML-Inferenz.",
                )
                data_centre_mw = st.slider(
                    "Rechenzentrumslast (MW)",
                    min_value=0,
                    max_value=5_000,
                    step=100,
                    key="scenario_data_centre_mw",
                    help="Zusätzliche konstante Last in jeder Szenariostunde.",
                )

        with evaluation_col:
            with st.container(
                border=True,
                key="scenario_evaluation",
                height="stretch",
            ):
                st.markdown("#### 3 · Auswertung")
                st.caption(
                    "Die Schwelle verändert nur die Einordnung der Lastkurve."
                )
                st.markdown("**Extremzustandsschwelle**")
                q95_col, q99_col = st.columns(2, gap="small")
                quantile = float(st.session_state["scenario_quantile"])
                with q95_col:
                    st.button(
                        "Q95",
                        key="scenario_quantile_q95",
                        type="primary" if quantile == 0.95 else "secondary",
                        width="stretch",
                        on_click=set_scenario_quantile,
                        args=(0.95,),
                        help="95-%-Quantil der historischen Last 2015–2017.",
                    )
                with q99_col:
                    st.button(
                        "Q99",
                        key="scenario_quantile_q99",
                        type="primary" if quantile == 0.99 else "secondary",
                        width="stretch",
                        on_click=set_scenario_quantile,
                        args=(0.99,),
                        help="99-%-Quantil der historischen Last 2015–2017.",
                    )
                st.caption(
                    "Historische nationale Lastschwelle 2015–2017; "
                    "Unsicherheit aus Residualtagen der Validierung 2018."
                )

    model = load_model()
    climatology = load_climatology()
    current_scenario_logic = get_scenario_logic()
    scenario = current_scenario_logic.predict_scenario_day(
        model,
        climatology,
        country=country,
        target_date=target_date,
        temperature_delta_c=temperature_delta,
        direct_radiation_factor=direct_radiation_pct / 100.0,
        diffuse_radiation_factor=diffuse_radiation_pct / 100.0,
        demand_change_fraction=demand_change_pct / 100.0,
        additional_data_centre_load_mw=data_centre_mw,
    )
    summary = current_scenario_logic.summarize_scenario(scenario)

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

    base_energy = summary["base_energy_mwh"]
    scenario_energy = summary["scenario_energy_mwh"]
    energy_delta = scenario_energy - base_energy
    energy_delta_pct = 100 * energy_delta / base_energy
    base_peak_hour = int(
        scenario.loc[scenario["base_prediction_mw"].idxmax(), "local_hour"]
    )
    scenario_peak_hour = int(
        scenario.loc[
            scenario["scenario_prediction_mw"].idxmax(),
            "local_hour",
        ]
    )
    base_hours_above = int(
        (scenario["base_prediction_mw"] > threshold).sum()
    )
    scenario_hours_above = int(
        (scenario["scenario_prediction_mw"] > threshold).sum()
    )

    result_panel.markdown("### Ergebnis gegenüber der historischen Referenz")
    col1, col2, col3, col4 = result_panel.columns(4, gap="small")
    col1.metric(
        "Szenario-Lastspitze",
        format_power_mw(summary["scenario_peak_mw"]),
        delta=format_power_mw(summary["peak_delta_mw"]),
    )
    col2.metric(
        "Szenario-Tagesenergie",
        format_energy_mwh(scenario_energy),
        delta=(
            f"{format_energy_mwh(energy_delta)} · "
            f"{format_pct(energy_delta_pct, 1)}"
        ),
    )
    col3.metric(
        "Zeitpunkt der Spitze",
        format_hour(scenario_peak_hour),
        delta=f"Referenz: {format_hour(base_peak_hour)}",
        delta_color="off",
    )
    col4.metric(
        f"Stunden über Q{int(100 * quantile)}",
        f"{scenario_hours_above} von 24",
        delta=f"Referenz: {base_hours_above}",
        delta_color="off",
    )

    profile_tab, weather_tab, values_tab, logic_tab = result_panel.tabs(
        [
            "📈 Lastprofil",
            "🌤 Wetterinputs",
            "🔢 Zukunftswerte",
            "🧭 Einordnung",
        ]
    )
    with profile_tab:
        st.altair_chart(
            build_scenario_chart(scenario),
            use_container_width=True,
        )
    with weather_tab:
        st.caption(
            "Gestrichelt: historisches Medianprofil 1980–2019. Durchgezogen: "
            "die tatsächlich an das HGB übergebenen Wettermerkmale."
        )
        temperature_chart, radiation_chart = st.columns(2, gap="large")
        with temperature_chart:
            st.altair_chart(
                build_temperature_input_chart(scenario),
                use_container_width=True,
            )
        with radiation_chart:
            st.altair_chart(
                build_radiation_input_chart(scenario),
                use_container_width=True,
            )
    with values_tab:
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
            "Referenz (MW)",
            "Nur Wetter (MW)",
            "Gesamtszenario (MW)",
            "P(Extremzustand) (%)",
        ]
        st.dataframe(
            table.style.format(
                {
                    "Typische Temperatur (°C)": "{:.1f}",
                    "Szenariotemperatur (°C)": "{:.1f}",
                    "Referenz (MW)": "{:,.0f}",
                    "Nur Wetter (MW)": "{:,.0f}",
                    "Gesamtszenario (MW)": "{:,.0f}",
                    "P(Extremzustand) (%)": "{:.1f}",
                }
            ),
            hide_index=True,
            width="stretch",
        )
    with logic_tab:
        logic_col, warning_col = st.columns(2, gap="large")
        with logic_col:
            st.markdown(
                """
                **Rechenlogik**

                1. Kalendermerkmale folgen dem gewählten Datum.
                2. Wetter ist der historische Median nach Land, Monat und Stunde.
                3. Temperatur sowie direkte und diffuse Strahlung werden vor
                   der ML-Inferenz verändert.
                4. Nachfrage und Rechenzentrumslast werden danach transparent
                   angewendet.
                """
            )
        with warning_col:
            st.warning(
                "Der Extremzustandsindikator bezeichnet ausschließlich die "
                "Überschreitung einer historischen nationalen Lastschwelle. "
                "Er ist keine Blackout-, Netzüberlastungs- oder "
                "Versorgungsausfallwahrscheinlichkeit."
            )

    result_panel.markdown(
        f"""
        **Schwellenreferenz:** {int(100 * quantile)}-%-Quantil der Last aus
        2015–2017 für {COUNTRY_REGISTRY[country].name} =
        **{format_power_mw(threshold)}**. Die Unsicherheit basiert auf
        vollständigen 24-Stunden-Residualpfaden der Validierung 2018. Daraus
        ergibt sich für dieses Szenario eine empirische Wahrscheinlichkeit
        von **{format_pct(100 * day_probability, 1)}** für mindestens eine
        Extremstunde.
        """
    )


def render_methodology() -> None:
    report = load_k_report()
    render_page_header(
        "Methodik · Reproduzierbarkeit · Grenzen",
        "Wie belastbar ist GridCast?",
        "Die App trennt gemessene Modellgüte, illustrative Szenarien und "
        "technische Reproduzierbarkeit sichtbar voneinander.",
    )

    st.markdown("### QUA³CK in fünf Schritten")
    phases = [
        ("Q", "Question", "Frage, Hypothesen und Erfolgskriterien"),
        ("U", "Understanding", "131.441 geprüfte Länder-Stunden"),
        ("A³", "Algorithms", "Baselines, Ridge und HGB auf 2018"),
        ("C", "Conclude", "Eingefrorenes HGB einmalig auf 2019"),
        ("K", "Transfer", "Modell, App und Prüfungsartefakte"),
    ]
    phase_columns = st.columns(5)
    for column, (letter, name, description) in zip(phase_columns, phases):
        with column:
            with st.container(border=True):
                st.markdown(f"### {letter}")
                st.markdown(f"**{name}**")
                st.caption(description)

    result_col, boundary_col = st.columns([1.05, 0.95], gap="large")
    with result_col:
        st.markdown("### Belastbares Ergebnis")
        metrics = pd.DataFrame(
            [
                ["Ländermittelwert", "15,64 %", "triviale Referenz"],
                ["Kalender-Baseline", "4,88 %", "starke Referenz"],
                ["HGB + Feiertag + Wetter", "2,71 %", "final ausgewählt"],
            ],
            columns=["Modell", "Makro-nMAE 2019", "Rolle"],
        )
        st.dataframe(metrics, hide_index=True, width="stretch")
        st.success(
            "Das finale HGB reduziert den Fehler gegenüber der starken "
            "Kalender-Baseline um 44,5 %."
        )
    with boundary_col:
        st.markdown("### Geltungsbereich")
        st.markdown(
            """
            - **Länder:** Deutschland, Frankreich und Polen
            - **Datenperiode:** OPSD 2015–2019
            - **Primärmetrik:** länderweise gleichgewichteter Makro-nMAE
            - **Test:** vollständiges, unangetastetes Kalenderjahr 2019
            - **Extremzustand:** nationale historische Quantilsüberschreitung
            """
        )

    st.markdown("### Grenzen")
    st.markdown(
        """
        - Reanalysewetter im Backtest ist keine echte Wettervorhersage.
        - Regionale deutsche Feiertage sind nicht separat modelliert.
        - Zukunftsaufschläge sind Annahmen, keine kausal gelernten Langfristtrends.
        - Das refittete App-Modell hat keine neue unabhängige Testkennzahl.
        - Extremzustand bedeutet eine historische Quantilsüberschreitung,
          nicht einen Netzausfall.
        """
    )

    with st.expander("Technischer Deployment- und Reproduzierbarkeitsstatus"):
        st.caption(
            "Dieser technische Block wurde bewusst aus der Überblicksseite "
            "in die Methodik verschoben."
        )
        deployment_summary = {
            "Modellartefakt": report["model"]["path"],
            "SHA-256": report["model"]["sha256"],
            "Trainingsperiode": report["model"]["training_period"],
            "Unabhängige Qualitätsquelle": report["model"][
                "independent_quality_source"
            ],
            "Smoke-Tests": report["verification"]["passed"],
            "App-Daten": report["app_assets"],
        }
        st.json(deployment_summary, expanded=False)


apply_visual_theme()
page = render_sidebar()

try:
    if page == "🏠 Überblick":
        render_overview()
    elif page == "🧪 Historischer Backtest":
        render_backtest()
    elif page == "🔭 Zukunftsszenario":
        render_scenario()
    else:
        render_methodology()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()
