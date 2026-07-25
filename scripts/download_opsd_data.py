"""Lädt die zwei verbindlichen OPSD-Rohdatenpakete reproduzierbar herunter."""

from __future__ import annotations

import argparse
import shutil
import urllib.request
import zipfile
from pathlib import Path


LOAD_URL = (
    "https://data.open-power-system-data.org/time_series/2020-10-06/"
    "time_series_60min_singleindex.csv"
)
WEATHER_URL = (
    "https://data.open-power-system-data.org/weather_data/"
    "opsd-weather_data-2020-09-16.zip"
)


def download(url: str, target: Path, force: bool = False) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not force:
        print(f"Vorhanden, übersprungen: {target}")
        return
    temporary = target.with_suffix(target.suffix + ".part")
    print(f"Lade {url}")
    with urllib.request.urlopen(url) as response, temporary.open("wb") as output:
        shutil.copyfileobj(response, output)
    temporary.replace(target)
    print(f"Gespeichert: {target}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    load_target = (
        root
        / "data/raw/opsd/time_series_2020-10-06"
        / "time_series_60min_singleindex.csv"
    )
    weather_dir = root / "data/raw/opsd/weather_data_2020-09-16"
    weather_zip = weather_dir / "opsd-weather_data-2020-09-16.zip"
    weather_csv = weather_dir / "weather_data.csv"

    download(LOAD_URL, load_target, args.force)
    download(WEATHER_URL, weather_zip, args.force)
    if args.force or not weather_csv.exists():
        with zipfile.ZipFile(weather_zip) as archive:
            member = "opsd-weather_data-2020-09-16/weather_data.csv"
            weather_dir.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, weather_csv.open("wb") as output:
                shutil.copyfileobj(source, output)
        print(f"Entpackt: {weather_csv}")
    else:
        print(f"Vorhanden, übersprungen: {weather_csv}")


if __name__ == "__main__":
    main()
