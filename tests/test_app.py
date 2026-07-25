from pathlib import Path
import ast


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_streamlit_app_and_deployment_assets_exist():
    app_path = PROJECT_ROOT / "streamlit_app" / "app.py"
    source = app_path.read_text(encoding="utf-8")
    ast.parse(source)
    assert "Historischer Backtest" in source
    assert "Zukunftsszenario" in source
    for relative_path in [
        "models/gridcast_final_2015_2019.joblib",
        "data/app/backtest_2019.csv.gz",
        "data/app/weather_climatology_1980_2019.csv.gz",
        "data/app/risk_calibration_2018.npz",
        "reports/k/k_deployment.json",
    ]:
        assert (PROJECT_ROOT / relative_path).is_file()
