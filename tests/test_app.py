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
    assert 'st.button(\n                    "Q95"' in source
    assert 'st.button(\n                    "Q99"' in source
    assert 'st.session_state.setdefault("scenario_quantile", 0.99)' in source
    assert '"Mittlere Last (MW)"' in source
    assert '"Stundendaten und exakte Fehlerwerte", expanded=True' in source
    assert "EXPECTED_SCENARIO_API_VERSION = 2" in source
    assert "padding-top: 4.5rem" in source
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
