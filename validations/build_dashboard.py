from __future__ import annotations

import argparse
import csv
import json
from html import escape
from pathlib import Path
from typing import Any


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def number(row: dict[str, str], key: str) -> float | None:
    value = row.get(key, "")
    try:
        return float(value) if value not in ("", None) else None
    except (TypeError, ValueError):
        return None


def build_dashboard(output_dir: Path, output_path: Path | None = None) -> Path:
    """Build a Persian, interactive HTML dashboard from archived validation outputs.

    Plotly is loaded from its public CDN by the browser; this builder has no
    additional Python dependencies. The dashboard is descriptive and does not
    upgrade model-to-model comparisons into field validation.
    """
    summary = read_json(output_dir / "hourly_poa_summary.json")
    monthly = read_csv(output_dir / "monthly_poa_bias.csv")
    lag = read_csv(output_dir / "time_lag_sensitivity.csv")
    hourly = read_csv(output_dir / "open_meteo_hourly_poa_comparison.csv")
    if not summary:
        raise FileNotFoundError(f"Missing validation summary: {output_dir / 'hourly_poa_summary.json'}")

    month_labels = [row.get("month", "") for row in monthly]
    internal_monthly = [number(row, "internal") for row in monthly]
    pvgis_monthly = [number(row, "pvgis") for row in monthly]
    monthly_bias = [number(row, "bias_percent") for row in monthly]
    lag_labels = [row.get("lag_hours", "") for row in lag]
    lag_mae = [number(row, "mae") for row in lag]
    lag_rmse = [number(row, "rmse") for row in lag]

    # A deterministic, readable subset is used for the scatter plot while all
    # available hourly points remain in the time-series and residual plots.
    stride = max(1, len(hourly) // 1800)
    scatter_rows = hourly[::stride]
    internal_gti = [number(row, "internal_isotropic_poa_w_m2") for row in hourly]
    reference_gti = [number(row, "open_meteo_gti_w_m2") for row in hourly]
    residuals = [number(row, "internal_minus_gti_w_m2") for row in hourly]
    timestamps = [row.get("timestamp_utc", "") for row in hourly]
    scatter_x = [number(row, "open_meteo_gti_w_m2") for row in scatter_rows]
    scatter_y = [number(row, "internal_isotropic_poa_w_m2") for row in scatter_rows]
    scatter_max = max([v for v in scatter_x + scatter_y if v is not None] or [1])

    def fmt(value: Any, digits: int = 2) -> str:
        try:
            return f"{float(value):,.{digits}f}"
        except (TypeError, ValueError):
            return "ناموجود"

    meta = summary.get("metadata", {})
    site = meta.get("site", {})
    orientation = meta.get("requested_orientation", {})
    gti = summary.get("open_meteo_internal_poa_vs_gti", {})
    title = f"داشبورد اعتبارسنجی تابش خورشیدی — {meta.get('common_year', summary.get('year', ''))}"
    cards = [
        ("اختلاف انرژی سالانه با PVGIS", f"{fmt(summary.get('annual_bias_percent'))}٪"),
        ("MAE ساعتی با PVGIS", f"{fmt(summary.get('hourly_mae_w_m2'))} W/m²"),
        ("RMSE ساعتی با PVGIS", f"{fmt(summary.get('hourly_rmse_w_m2'))} W/m²"),
        ("همبستگی ساعتی با PVGIS", fmt(summary.get("hourly_correlation"), 4)),
        ("اختلاف انرژی سالانه با GTI", f"{fmt(gti.get('annual_bias_percent'))}٪"),
        ("تعداد ساعات مقایسه", str(summary.get("hours", len(hourly)))),
    ]
    card_html = "".join(
        f'<article class="metric"><div>{escape(label)}</div><strong>{escape(value)}</strong></article>'
        for label, value in cards
    )
    data = {
        "monthLabels": month_labels,
        "internalMonthly": internal_monthly,
        "pvgisMonthly": pvgis_monthly,
        "monthlyBias": monthly_bias,
        "lagLabels": lag_labels,
        "lagMae": lag_mae,
        "lagRmse": lag_rmse,
        "timestamps": timestamps,
        "internalGti": internal_gti,
        "referenceGti": reference_gti,
        "residuals": residuals,
        "scatterX": scatter_x,
        "scatterY": scatter_y,
        "scatterMax": scatter_max,
    }
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    output_path = output_path or output_dir / "dashboard.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root{{color-scheme:light;--ink:#182230;--muted:#596579;--line:#dbe2ea;--paper:#f4f7fb;--card:#fff;--accent:#176b87}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:Vazirmatn,"Noto Sans Arabic",Tahoma,sans-serif;line-height:1.7}}
main{{max-width:1500px;margin:auto;padding:28px}}header{{padding:8px 0 20px}}h1{{font-size:clamp(1.5rem,3vw,2.2rem);margin:0 0 8px}}h2{{font-size:1.1rem;margin:0 0 4px}}p{{margin:4px 0;color:var(--muted)}}.meta{{font-size:.9rem}}
.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0 22px}}.metric,.panel,.notice{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;box-shadow:0 2px 8px #14223808}}.metric div{{color:var(--muted);font-size:.9rem}}.metric strong{{display:block;direction:ltr;text-align:right;font-size:1.35rem;margin-top:5px;overflow-wrap:anywhere}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}.panel{{min-width:0}}.chart{{height:360px;direction:ltr}}.wide{{grid-column:1/-1}}.notice{{margin:16px 0;border-right:4px solid var(--accent)}}.notice strong{{display:block;margin-bottom:4px}}footer{{font-size:.85rem;color:var(--muted);padding:22px 0}}a{{color:var(--accent)}}@media(max-width:850px){{main{{padding:14px}}.grid{{grid-template-columns:1fr}}.wide{{grid-column:auto}}.chart{{height:320px}}}}
</style>
</head>
<body><main>
<header><h1>{escape(title)}</h1>
<p class="meta">مختصات: {fmt(site.get('latitude'), 5)}، {fmt(site.get('longitude'), 5)} | شیب: {fmt(orientation.get('tilt_deg'))}° | آزیموت از شمال: {fmt(orientation.get('azimuth_from_north_deg'))}°</p>
<p>نمایش تعاملی خروجی اعتبارسنجی ساعتی تابش روی صفحه (POA)</p></header>
<section class="metrics">{card_html}</section>
<section class="notice"><strong>محدودیت تفسیر علمی</strong>
این گزارش مقایسهٔ مدل داخلی با داده‌های مرجع ماهواره‌ای/بازتحلیل است، نه اعتبارسنجی میدانی. توافق سالانه می‌تواند اختلاف فصلی یا ساعتی را پنهان کند. مقایسهٔ GTI با Open-Meteo از همان ارائه‌دهنده استفاده می‌کند و مستقل از منبع هواشناسی نیست. نمودارها عملکرد توان الکتریکی یا انرژی AC را ارزیابی نمی‌کنند.</section>
<section class="grid">
<article class="panel"><h2>انرژی تابش ماهانه: مدل داخلی در برابر PVGIS</h2><p>مجموع ماهانه، kWh/m²</p><div id="monthly" class="chart"></div></article>
<article class="panel"><h2>Bias ماهانه نسبت به PVGIS</h2><p>مقدار مثبت یعنی مدل داخلی بیشتر و مقدار منفی یعنی کمتر از مرجع است.</p><div id="bias" class="chart"></div></article>
<article class="panel wide"><h2>سری زمانی ساعتی: POA داخلی و GTI در Open-Meteo</h2><p>از نوار پایین برای بزرگ‌نمایی بازهٔ زمانی استفاده کنید. زمان‌ها UTC هستند.</p><div id="timeseries" class="chart"></div></article>
<article class="panel"><h2>نمودار پراکندگی: POA داخلی در برابر GTI</h2><p>خط نقطه‌چین نشان‌دهندهٔ برابری عددی دو سری است؛ این مقایسه مستقل از منبع اقلیمی نیست.</p><div id="scatter" class="chart"></div></article>
<article class="panel"><h2>توزیع باقیمانده‌ها: داخلی منهای GTI</h2><p>W/m²؛ مقدار مثبت نشان‌دهندهٔ بیش‌برآورد مدل داخلی است.</p><div id="residual" class="chart"></div></article>
<article class="panel wide"><h2>حساسیت خطا به جابه‌جایی زمانی</h2><p>برای مقایسهٔ ساعتی با PVGIS؛ جابه‌جایی صفر بهترین MAE را داشته است یا ندارد، بر اساس دادهٔ همین اجرا.</p><div id="lag" class="chart"></div></article>
</section>
<footer>منابع: <a href="https://open-meteo.com/en/docs/historical-weather-api">Open-Meteo Historical Weather API</a> · <a href="https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/using-pvgis-5/api-non-interactive-service_en">PVGIS API</a><br>
برای نمایش نمودارها اتصال اینترنت لازم است تا کتابخانهٔ Plotly از CDN بارگذاری شود. داده‌ها از فایل‌های همین اجرای اعتبارسنجی خوانده شده‌اند؛ اجرای مجدد باید خروجی‌های متناظر را تولید کند.</footer>
</main>
<script>
const D = {data_json};
const baseLayout = {{autosize:true,margin:{{l:58,r:28,t:28,b:65}},paper_bgcolor:"#fff",plot_bgcolor:"#fff",font:{{family:"Tahoma, sans-serif",size:12,color:"#182230"}},xaxis:{{gridcolor:"#edf1f5"}},yaxis:{{gridcolor:"#edf1f5"}},legend:{{orientation:"h",y:-0.22}}}};
function plot(id,traces,layout={{}}){{Plotly.newPlot(id,traces,Object.assign({{}},baseLayout,layout),{{responsive:true,displaylogo:false,scrollZoom:true}});}}
plot("monthly",[
{{x:D.monthLabels,y:D.internalMonthly,name:"مدل داخلی",type:"bar"}},
{{x:D.monthLabels,y:D.pvgisMonthly,name:"PVGIS",type:"bar"}}
],{{barmode:"group",yaxis:{{title:"kWh/m²",gridcolor:"#edf1f5"}},xaxis:{{title:"ماه"}}}});
plot("bias",[{{x:D.monthLabels,y:D.monthlyBias,type:"bar",name:"Bias ماهانه",marker:{{color:D.monthlyBias.map(v=>v>=0?"#c46b35":"#277da1")}}}}],
{{yaxis:{{title:"Bias (%)",zeroline:true,zerolinewidth:2,zerolinecolor:"#293241"}},xaxis:{{title:"ماه"}}}});
plot("timeseries",[
{{x:D.timestamps,y:D.internalGti,name:"POA داخلی",type:"scatter",mode:"lines",line:{{width:1.2}}}},
{{x:D.timestamps,y:D.referenceGti,name:"GTI در Open-Meteo",type:"scatter",mode:"lines",line:{{width:1.2}}}}
],{{xaxis:{{title:"زمان UTC",rangeslider:{{visible:true}}}},yaxis:{{title:"تابش (W/m²)",rangemode:"tozero"}}}});
plot("scatter",[
{{x:D.scatterX,y:D.scatterY,type:"scatter",mode:"markers",name:"ساعات نمونه‌برداری‌شده",marker:{{size:4,opacity:.35}}}},
{{x:[0,D.scatterMax],y:[0,D.scatterMax],type:"scatter",mode:"lines",name:"خط برابری y=x",line:{{dash:"dash",color:"#333"}}}}
],{{xaxis:{{title:"GTI مرجع (W/m²)",rangemode:"tozero"}},yaxis:{{title:"POA داخلی (W/m²)",rangemode:"tozero"}}}});
plot("residual",[{{x:D.residuals,type:"histogram",name:"باقیمانده",nbinsx:60,marker:{{color:"#477a91"}}}}],
{{xaxis:{{title:"POA داخلی − GTI (W/m²)"}},yaxis:{{title:"تعداد ساعات"}}}});
plot("lag",[
{{x:D.lagLabels,y:D.lagMae,name:"MAE",type:"scatter",mode:"lines+markers"}},
{{x:D.lagLabels,y:D.lagRmse,name:"RMSE",type:"scatter",mode:"lines+markers"}}
],{{xaxis:{{title:"جابه‌جایی زمانی (ساعت)"}},yaxis:{{title:"خطا (W/m²)"}}}});
</script></body></html>"""
    output_path.write_text(html, encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an interactive Persian PV validation dashboard.")
    parser.add_argument("--input-dir", required=True, help="Directory containing validation output files.")
    parser.add_argument("--output", help="Optional HTML output path; defaults to dashboard.html in input-dir.")
    args = parser.parse_args()
    result = build_dashboard(Path(args.input_dir), Path(args.output) if args.output else None)
    print(f"Dashboard written to: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
