from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


def compare(reference: np.ndarray, predicted: np.ndarray) -> dict:
    reference = np.asarray(reference, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    if reference.shape != predicted.shape or reference.ndim != 1 or reference.size == 0:
        raise ValueError("Reference and predicted columns must be non-empty one-dimensional arrays of equal length.")
    valid = np.isfinite(reference) & np.isfinite(predicted)
    reference, predicted = reference[valid], predicted[valid]
    if reference.size == 0:
        raise ValueError("No finite reference/predicted pairs were found.")
    error = predicted - reference
    nonzero = np.abs(reference) > np.finfo(float).eps
    return {
        "n": int(reference.size),
        "bias": float(np.mean(error)),
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error ** 2))),
        "max_absolute_error": float(np.max(np.abs(error))),
        "mape_percent": float(np.mean(np.abs(error[nonzero] / reference[nonzero])) * 100.0) if np.any(nonzero) else None,
        "reference_mean": float(np.mean(reference)),
        "predicted_mean": float(np.mean(predicted)),
        "reference_min": float(np.min(reference)),
        "reference_max": float(np.max(reference)),
        "excluded_nonfinite_pairs": int(np.size(valid) - np.count_nonzero(valid)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Airfoil-CAD results with sourced experimental/reference CSV data.")
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--reference", required=True, help="CSV column containing measured/reference values.")
    parser.add_argument("--predicted", required=True, help="CSV column containing Airfoil-CAD predicted values.")
    parser.add_argument("--group-by", default=None, help="Optional condition/case column for per-condition metrics.")
    parser.add_argument("--output", type=Path, default=Path("reference_comparison.json"))
    args = parser.parse_args()

    with args.csv_file.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        parser.error("Input CSV has no data rows.")
    for name in (args.reference, args.predicted, args.group_by):
        if name and name not in rows[0]:
            parser.error(f"Column {name!r} was not found in CSV header.")

    def numeric(column: str) -> np.ndarray:
        values = []
        for row in rows:
            try:
                values.append(float(row[column]))
            except (TypeError, ValueError):
                values.append(float("nan"))
        return np.asarray(values, dtype=float)

    reference, predicted = numeric(args.reference), numeric(args.predicted)
    report = {
        "input_file": str(args.csv_file),
        "reference_column": args.reference,
        "predicted_column": args.predicted,
        "metrics": compare(reference, predicted),
        "group_metrics": {},
        "note": "Metrics quantify agreement only; interpretation requires documented source, units, matching conditions, and uncertainty.",
    }
    if args.group_by:
        groups = sorted({row[args.group_by] for row in rows if row[args.group_by] not in ("", None)})
        for group in groups:
            mask = np.asarray([row[args.group_by] == group for row in rows], dtype=bool)
            try:
                report["group_metrics"][group] = compare(reference[mask], predicted[mask])
            except ValueError as exc:
                report["group_metrics"][group] = {"error": str(exc)}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
