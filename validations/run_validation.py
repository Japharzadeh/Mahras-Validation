from __future__ import annotations

import argparse
import csv
import json
import sys

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

HTTP = requests.Session()
HTTP.mount("https://", HTTPAdapter(max_retries=Retry(total=3, connect=3, read=2, status=3, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=frozenset(["GET"]))))

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from solar.pv_component_validation import open_meteo_interval_center
from solar.pv_hourly_validation import (
    _solar_position,
    compare_hourly_poa_with_pvgis,
    summarize_hourly_poa,
)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def azimuth_from_north_to_api_aspect(azimuth_from_north: float) -> float:
    """Convert clockwise-from-north azimuth to zero-south, west-positive convention."""
    return ((float(azimuth_from_north) - 180.0 + 180.0) % 360.0) - 180.0


def compare_open_meteo_gti(
    latitude: float,
    longitude: float,
    tilt: float,
    azimuth_from_north: float,
    year: int,
) -> dict[str, Any]:
    aspect = azimuth_from_north_to_api_aspect(azimuth_from_north)
    response = HTTP.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": "{}-12-31".format(year - 1),
            "end_date": "{}-01-01".format(year + 1),
            "hourly": "global_tilted_irradiance",
            "timezone": "UTC",
            "tilt": tilt,
            "azimuth": aspect,
        },
        timeout=(20, 120),
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(payload.get("reason", "Open-Meteo returned an API error"))
    hourly = payload.get("hourly") or {}
    all_times = hourly.get("time") or []
    all_values = hourly.get("global_tilted_irradiance") or []
    if len(all_times) < 8760 or len(all_values) != len(all_times):
        raise ValueError(
            "Open-Meteo GTI returned {} records; at least 8760 complete hourly records were expected.".format(len(all_times))
        )
    if any(value is None for value in all_values):
        raise ValueError("Open-Meteo GTI contains missing hourly values.")
    indices = [
        i for i, stamp in enumerate(all_times)
        if open_meteo_interval_center(stamp).year == year
    ]
    if len(indices) != 8760:
        raise ValueError(
            "Open-Meteo GTI has {} interval centers inside {}; 8760 were expected.".format(len(indices), year)
        )
    times = [all_times[i] for i in indices]
    values = [float(all_values[i]) for i in indices]
    return {
        "source": "Open-Meteo Historical Weather API",
        "year": year,
        "hours": len(times),
        "times_utc": times,
        "gti_w_m2": values,
        "tilt_deg": tilt,
        "azimuth_from_north_deg": azimuth_from_north,
        "api_aspect_zero_south_positive_west_deg": aspect,
        "note": (
            "GTI is an independent implementation using the same weather service, "
            "not an independent climate dataset. Use it to test transposition conventions."
        ),
    }


def fetch_open_meteo_components(
    latitude: float, longitude: float, year: int
) -> dict[str, Any]:
    response = requests.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": "{}-12-31".format(year - 1),
            "end_date": "{}-01-01".format(year + 1),
            "hourly": "shortwave_radiation,direct_normal_irradiance,diffuse_radiation",
            "timezone": "UTC",
        },
        timeout=(10, 90),
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(payload.get("reason", "Open-Meteo returned an API error"))
    hourly = payload.get("hourly") or {}
    all_times = hourly.get("time") or []
    if len(all_times) < 8760:
        raise ValueError(
            "Open-Meteo returned {} timestamps; at least 8760 were expected.".format(len(all_times))
        )
    indices = [
        i for i, stamp in enumerate(all_times)
        if open_meteo_interval_center(stamp).year == year
    ]
    if len(indices) != 8760:
        raise ValueError(
            "Open-Meteo has {} interval centers inside {}; 8760 were expected.".format(len(indices), year)
        )
    columns = {}
    for key in ("shortwave_radiation", "direct_normal_irradiance", "diffuse_radiation"):
        values = hourly.get(key) or []
        if len(values) != len(all_times) or any(value is None for value in values):
            raise ValueError("Missing or incomplete Open-Meteo column: {}".format(key))
        columns[key] = [float(values[i]) for i in indices]
    return {"times_utc": [all_times[i] for i in indices], **columns}


def calculate_isotropic_poa(
    times_utc: list[str],
    ghi: list[float],
    dni: list[float],
    dhi: list[float],
    latitude: float,
    longitude: float,
    tilt_deg: float,
    azimuth_from_north_deg: float,
) -> list[float]:
    from datetime import timedelta

    from datetime import datetime as dt

    midpoint_times = []
    for value in times_utc:
        stamp = dt.fromisoformat(str(value).replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        midpoint_times.append((stamp.astimezone(timezone.utc) - timedelta(minutes=30)).isoformat())
    altitude, sun_azimuth = _solar_position(latitude, longitude, midpoint_times)
    tilt = __import__("math").radians(tilt_deg)
    panel_azimuth = __import__("math").radians(azimuth_from_north_deg % 360.0)
    import math
    import numpy as np

    ghi_array = np.asarray(ghi, dtype=float)
    dni_array = np.asarray(dni, dtype=float)
    dhi_array = np.asarray(dhi, dtype=float)
    cosine_incidence = (
        np.sin(altitude) * math.cos(tilt)
        + np.cos(altitude) * math.sin(tilt)
        * np.cos(sun_azimuth - panel_azimuth)
    )
    beam = np.where(altitude > 0.0, dni_array * np.maximum(cosine_incidence, 0.0), 0.0)
    diffuse = np.where(altitude > 0.0, dhi_array * (1.0 + math.cos(tilt)) / 2.0, 0.0)
    reflected = np.where(
        altitude > 0.0, ghi_array * 0.20 * (1.0 - math.cos(tilt)) / 2.0, 0.0
    )
    return np.maximum(beam + diffuse + reflected, 0.0).tolist()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Re-run the 2023 hourly POA comparison and archive validation outputs."
    )
    parser.add_argument("--latitude", type=float, required=True)
    parser.add_argument("--longitude", type=float, required=True)
    parser.add_argument("--tilt", type=float, default=32.0)
    parser.add_argument("--azimuth", type=float, default=190.0,
                        help="Panel azimuth clockwise from north.")
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--output-dir", default="validations/results/latest")
    args = parser.parse_args()

    if not -90 <= args.latitude <= 90:
        parser.error("latitude must be between -90 and 90")
    if not -180 <= args.longitude <= 180:
        parser.error("longitude must be between -180 and 180")
    if not 0 <= args.tilt <= 90:
        parser.error("tilt must be between 0 and 90 degrees")
    if args.year != 2023:
        parser.error("The current PVGIS hourly validation implementation supports common year 2023.")

    output_dir = (ROOT / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    result = compare_hourly_poa_with_pvgis(
        args.latitude, args.longitude, args.tilt, args.azimuth, year=args.year
    )
    gti = compare_open_meteo_gti(
        args.latitude, args.longitude, args.tilt, args.azimuth, args.year
    )
    components = fetch_open_meteo_components(args.latitude, args.longitude, args.year)
    if components["times_utc"] != gti["times_utc"]:
        raise ValueError("Open-Meteo component and GTI timestamps do not match exactly.")
    internal_poa = calculate_isotropic_poa(
        components["times_utc"],
        components["shortwave_radiation"],
        components["direct_normal_irradiance"],
        components["diffuse_radiation"],
        args.latitude, args.longitude, args.tilt, args.azimuth,
    )
    gti_metrics = summarize_hourly_poa(internal_poa, gti["gti_w_m2"])
    gti_metrics["reference"] = "Open-Meteo global_tilted_irradiance"
    gti_metrics["interpretation"] = (
        "Same weather provider, different transposition calculation. "
        "This isolates implementation/convention differences better than cross-provider comparison."
    )

    hourly_rows = []
    for index, stamp in enumerate(components["times_utc"]):
        hourly_rows.append({
            "timestamp_utc": open_meteo_interval_center(stamp).isoformat(),
            "open_meteo_label_utc": stamp,
            "ghi_w_m2": components["shortwave_radiation"][index],
            "dni_w_m2": components["direct_normal_irradiance"][index],
            "dhi_w_m2": components["diffuse_radiation"][index],
            "internal_isotropic_poa_w_m2": internal_poa[index],
            "open_meteo_gti_w_m2": gti["gti_w_m2"][index],
            "internal_minus_gti_w_m2": internal_poa[index] - gti["gti_w_m2"][index],
        })
    write_csv(output_dir / "open_meteo_hourly_poa_comparison.csv", hourly_rows)

    monthly_gti = {}
    for row in hourly_rows:
        month = row["timestamp_utc"][:7]
        bucket = monthly_gti.setdefault(month, {"internal": [], "reference": []})
        bucket["internal"].append(row["internal_isotropic_poa_w_m2"])
        bucket["reference"].append(row["open_meteo_gti_w_m2"])
    monthly_gti_rows = []
    for month, values in sorted(monthly_gti.items()):
        metrics = summarize_hourly_poa(values["internal"], values["reference"])
        monthly_gti_rows.append({"month": month, **metrics})
    write_csv(output_dir / "monthly_open_meteo_gti_comparison.csv", monthly_gti_rows)

    result["metadata"] = {
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "site": {"latitude": args.latitude, "longitude": args.longitude},
        "requested_orientation": {
            "tilt_deg": args.tilt,
            "azimuth_from_north_deg": args.azimuth,
            "pvgis_aspect_zero_south_positive_west_deg":
                azimuth_from_north_to_api_aspect(args.azimuth),
        },
        "common_year": args.year,
        "sources": {
            "open_meteo_archive": "https://open-meteo.com/en/docs/historical-weather-api",
            "pvgis_api": "https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/using-pvgis-5/api-non-interactive-service_en",
        },
        "interpretation": (
            "POA comparison only; no temperature, inverter, or system losses are included. "
            "This is not field validation."
        ),
    }
    result["open_meteo_gti_reference"] = {
        key: value for key, value in gti.items() if key not in ("times_utc", "gti_w_m2")
    }
    result["open_meteo_internal_poa_vs_gti"] = gti_metrics

    (output_dir / "hourly_poa_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    monthly_rows = [
        {"month": month, **values}
        for month, values in sorted(result.get("monthly_poa", {}).items())
    ]
    write_csv(output_dir / "monthly_poa_bias.csv", monthly_rows)
    write_csv(output_dir / "time_lag_sensitivity.csv", result.get("time_lag_sensitivity", []))

    from validations.build_dashboard import build_dashboard
    dashboard_path = build_dashboard(output_dir)

    report = [
        "# اجرای اعتبارسنجی ساعتی تابش روی صفحه",
        "",
        "- زمان اجرا (UTC): {}".format(result["metadata"]["run_timestamp_utc"]),
        "- مختصات: {}, {}".format(args.latitude, args.longitude),
        "- سال مشترک: {}".format(args.year),
        "- شیب: {}°؛ آزیموت از شمال: {}°".format(args.tilt, args.azimuth),
        "- ساعت‌های مشترک: {}".format(result.get("hours")),
        "- POA داخلی: {} kWh/m²".format(result.get("internal_poa_kwh_m2")),
        "- POA در PVGIS: {} kWh/m²".format(result.get("pvgis_poa_kwh_m2")),
        "- Bias سالانه: {}٪".format(result.get("annual_bias_percent")),
        "- Bias ساعتی: {} W/m²".format(result.get("hourly_bias_w_m2")),
        "- MAE: {} W/m²".format(result.get("hourly_mae_w_m2")),
        "- RMSE: {} W/m²".format(result.get("hourly_rmse_w_m2")),
        "- همبستگی: {}".format(result.get("hourly_correlation")),
        "- بهترین جابه‌جایی زمانی تشخیصی: {}".format(result.get("best_time_lag")),
        "",
        "## آزمون تبدیل تابش با GTI در Open-Meteo",
        "",
        "- POA داخلی: {} kWh/m²".format(gti_metrics.get("internal_poa_kwh_m2")),
        "- GTI مرجع: {} kWh/m²".format(gti_metrics.get("pvgis_poa_kwh_m2")),
        "- Bias سالانه: {}٪".format(gti_metrics.get("annual_bias_percent")),
        "- MAE ساعتی: {} W/m²".format(gti_metrics.get("hourly_mae_w_m2")),
        "- RMSE ساعتی: {} W/m²".format(gti_metrics.get("hourly_rmse_w_m2")),
        "- همبستگی ساعتی: {}".format(gti_metrics.get("hourly_correlation")),
        "",
        "## فایل‌های خروجی",
        "",
        "- hourly_poa_summary.json: پارامترها و معیارهای خلاصه.",
        "- monthly_poa_bias.csv: bias ماهانه.",
        "- time_lag_sensitivity.csv: آزمون جابه‌جایی زمانی.",
        "- open_meteo_hourly_poa_comparison.csv: GHI/DNI/DHI، POA داخلی و GTI ساعتی.",
        "- monthly_open_meteo_gti_comparison.csv: معیارهای ماهانهٔ POA داخلی در برابر GTI.",
        "- open_meteo_internal_poa_vs_gti در JSON: معیارهای ساعتی این مقایسه.",
        "- dashboard.html: داشبورد تعاملی نمودارهای اعتبارسنجی (نیازمند اینترنت برای بارگذاری Plotly).",
        "",
        "## محدودیت",
        "",
        "این خروجی اعتبارسنجی تابش است، نه اعتبارسنجی توان یا اندازه‌گیری میدانی. "
        "GTI در Open-Meteo از همان سرویس دادهٔ هواشناسی استفاده می‌کند و آزمون استقلال منبع نیست. "
        "برای نتیجهٔ تولید، باید مدل دما، اینورتر و تلفات در مقایسه‌ای جداگانه همسان شوند.",
        "",
    ]
    (output_dir / "report.md").write_text("\n".join(report), encoding="utf-8")
    print("Validation results saved to: {}".format(output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
