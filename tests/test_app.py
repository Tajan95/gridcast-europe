from pathlib import Path
import ast


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_streamlit_app_and_deployment_assets_exist():
    app_path = PROJECT_ROOT / "streamlit_app" / "app.py"
    source = app_path.read_text(encoding="utf-8")
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    ast.parse(source)
    assert "Historischer Backtest" in source
    assert "Zukunftsszenario" in source
    assert "EUROPE_TOPOJSON_URL" in source
    assert "Kombinierter Stresstest" in source
    assert "Direkte Sonneneinstrahlung" in source
    assert "Diffuse Sonneneinstrahlung" in source
    assert "Wetterinputs" in source
    assert "Direkte ML-Eingaben" in source
    assert "Explizite Strukturannahmen" in source
    assert '"Q95",' in source
    assert '"Q99",' in source
    assert 'st.session_state.setdefault("scenario_quantile", 0.99)' in source
    assert '"Mittlere Last (MW)"' in source
    assert '"Stundendaten und exakte Fehlerwerte", expanded=True' in source
    assert "EXPECTED_SCENARIO_API_VERSION = 2" in source
    assert "padding-top: 4.5rem" in source
    assert "max-width: 1320px" in source
    assert "max-width: 1680px" in source
    assert "def apply_scenario_page_width()" in source
    assert "apply_scenario_page_width()" in source
    assert 'st.columns([0.95, 1.55], gap="large")' in source
    assert 'control_col.container(key="scenario_controls")' in source
    assert 'result_col.container(key="scenario_results")' in source
    assert 'st.container(border=True, key="scenario_presets")' in source
    assert "range(0, len(preset_items), 4)" in source
    assert "preset['button_label']" in source
    assert "identity_col, date_col = st.columns(2" in source
    assert "temp_col, direct_col, diffuse_col = st.columns(3" in source
    assert "assumption_col, evaluation_col = st.columns(2" in source
    assert "result_panel.columns(4" in source
    assert ".st-key-scenario_controls" in source
    assert ".st-key-scenario_results" in source
    assert "[data-testid=\"stMarkdownContainer\"]:has(h4)" in source
    assert "[data-testid=\"stMarkdownContainer\"]:has(h3)" in source
    assert "padding-bottom: 0.46rem" in source
    assert 'key="scenario_structure_inputs",' in source
    assert 'key="scenario_evaluation",' in source
    assert source.count('height="stretch",') >= 2
    assert 'orient="bottom"' in source
    assert "columns=2" in source
    assert source.count('format="DD.MM.YYYY"') == 2
    assert "Histogram Gradient Boosting" in source
    assert "historischen Median für Land und Monat aus" in source
    assert "der 24 stündlichen Medianwerte mit 1,5" in source
    assert "format_power_mw" in source
    assert "format_energy_mwh" in source
    assert "Technischer Deployment- und Reproduzierbarkeitsstatus" in source
    for heading in [
        "# ⚡ GridCast Europe",
        "## 🎯 Forschungsfrage",
        "## 📊 Kernergebnisse",
        "## 🔄 QUA³CK-Projektverlauf",
        "## 🚀 Streamlit-App lokal starten",
        "## ⚠️ Grenzen",
    ]:
        assert heading in readme
    for relative_path in [
        "models/gridcast_final_2015_2019.joblib",
        "data/app/backtest_2019.csv.gz",
        "data/app/weather_climatology_1980_2019.csv.gz",
        "data/app/risk_calibration_2018.npz",
        "reports/k_deployment.json",
    ]:
        assert (PROJECT_ROOT / relative_path).is_file()
