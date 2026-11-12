from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path


def resolve_metric(result: dict, metric: str) -> float:
    if metric in result.get("summary", {}):
        value = result["summary"][metric]
    else:
        match = __import__("re").fullmatch(r"sections\[(\d+)\]\.([A-Za-z_][A-Za-z0-9_]*)", metric)
        if not match:
            raise ValueError(
                f"Unsupported metric '{metric}'. Use a summary key or sections[index].field."
            )
        index, field = int(match.group(1)), match.group(2)
        sections = result.get("sections", [])
        if index >= len(sections) or field not in sections[index]:
            raise ValueError(f"Metric '{metric}' is not present in the result JSON.")
        value = sections[index][field]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"Metric '{metric}' is not a finite numeric value.")
    return float(value)


def compare(result_path: Path, reference_path: Path, default_relative_tolerance: float) -> tuple[int, list[dict]]:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if not isinstance(result.get("summary"), dict):
        raise ValueError("Result JSON must contain a numeric 'summary' object.")
    rows = []
    with reference_path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"metric", "reference_value"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError("Reference CSV requires metric and reference_value columns.")
        for row in reader:
            metric = row["metric"].strip()
            reference = float(row["reference_value"])
            relative = float(row.get("relative_tolerance") or default_relative_tolerance)
            absolute = float(row.get("absolute_tolerance") or 0.0)
            if not metric or not math.isfinite(reference):
                raise ValueError("Metric names and reference values must be valid.")
            if relative < 0 or absolute < 0 or not math.isfinite(relative + absolute):
                raise ValueError(f"Invalid tolerance for metric '{metric}'.")
            actual = resolve_metric(result, metric)
            error = abs(actual - reference)
            allowed = max(absolute, relative * abs(reference))
            rows.append({
                "metric": metric,
                "reference": reference,
                "actual": actual,
                "absolute_error": error,
                "allowed_error": allowed,
                "passed": error <= allowed,
                "unit": row.get("unit", ""),
            })
    if not rows:
        raise ValueError("Reference CSV contains no comparison rows.")
    return sum(not row["passed"] for row in rows), rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare Mahras BEM JSON results with values exported from a QBlade reference case."
    )
    parser.add_argument("result_json", type=Path, help="Mahras BEM results JSON")
    parser.add_argument("reference_csv", type=Path, help="CSV with metric,reference_value and optional tolerances")
    parser.add_argument(
        "--relative-tolerance", type=float, default=0.05,
        help="Default relative tolerance (default: 0.05 = 5%%); per-row CSV values override it",
    )
    args = parser.parse_args()
    if args.relative_tolerance < 0 or not math.isfinite(args.relative_tolerance):
        parser.error("--relative-tolerance must be finite and non-negative")
    try:
        failures, rows = compare(args.result_json, args.reference_csv, args.relative_tolerance)
    except (OSError, json.JSONDecodeError, ValueError, csv.Error) as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        return 2

    print("metric,reference,mahras,absolute_error,allowed_error,unit,status")
    for row in rows:
        status = "PASS" if row["passed"] else "FAIL"
        print(
            f"{row['metric']},{row['reference']:.8g},{row['actual']:.8g},"
            f"{row['absolute_error']:.8g},{row['allowed_error']:.8g},"
            f"{row['unit']},{status}"
        )
    print(f"\n{len(rows) - failures}/{len(rows)} comparisons passed.")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
