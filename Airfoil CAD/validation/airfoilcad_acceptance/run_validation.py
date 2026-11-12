from __future__ import annotations

import csv
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
AIRFOIL = HERE.parents[1]
REPO = HERE.parents[2]
REPORTS = HERE / "reports"
JUNIT = REPORTS / "junit.xml"


def collect_cases(xml_path: Path) -> list[dict]:
    root = ET.parse(xml_path).getroot()
    cases = []
    for case in root.iter("testcase"):
        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")
        status = "FAIL" if failure is not None or error is not None else ("SKIP" if skipped is not None else "PASS")
        detail_node = failure if failure is not None else error if error is not None else skipped
        cases.append({
            "suite": case.attrib.get("classname", ""),
            "test": case.attrib.get("name", ""),
            "duration_seconds": float(case.attrib.get("time", "0") or 0),
            "status": status,
            "details": detail_node.attrib.get("message", "") if detail_node is not None else "",
        })
    return cases


def write_reports(cases: list[dict], exit_code: int) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    counts = {status: sum(case["status"] == status for case in cases) for status in ("PASS", "FAIL", "SKIP")}
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Airfoil-CAD backend regression/acceptance checks",
        "test_count": len(cases),
        "counts": counts,
        "runner_exit_code": exit_code,
        "tests": cases,
        "interpretation": "Software regression checks only; not certification or external experimental validation.",
    }
    (REPORTS / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with (REPORTS / "results.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["suite", "test", "duration_seconds", "status", "details"])
        writer.writeheader()
        writer.writerows(cases)

    table = ["| Backend area / test | Result | Duration (s) |", "|---|---:|---:|"]
    for case in cases:
        label = (case["suite"] + "." + case["test"]).strip(".").replace("|", "\\|")
        table.append("| " + label + " | **" + case["status"] + "** | " + format(case["duration_seconds"], ".3f") + " |")
    report = [
        "# Airfoil-CAD Backend Validation Report",
        "",
        "- Generated (UTC): " + payload["generated_at_utc"],
        "- Total tests: **" + str(len(cases)) + "**",
        "- Passed: **" + str(counts["PASS"]) + "** · Failed: **" + str(counts["FAIL"]) + "** · Skipped: **" + str(counts["SKIP"]) + "**",
        "- CI runner exit code: " + str(exit_code),
        "",
        "> Automated software checks only; not evidence of certification or agreement with experimental/QBlade results.",
        "",
        "## Test results",
        "",
        *table,
        "",
        "## Interpretation",
        "",
        "- Investigate every failed check before relying on the affected backend.",
        "- Passing invariants do not prove the full physical model is accurate.",
        "- External benchmark comparisons require sourced, licensed data and matched units, geometry, and operating conditions.",
        "",
    ]
    (REPORTS / "report.md").write_text("\n".join(report), encoding="utf-8")

    width, height = 720, 120 + max(1, len(cases)) * 22
    colors = {"PASS": "#238636", "FAIL": "#cf222e", "SKIP": "#9a6700"}
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="' + str(width) + '" height="' + str(height) + '" viewBox="0 0 ' + str(width) + ' ' + str(height) + '">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="24" y="32" font-family="sans-serif" font-size="20" font-weight="bold">Airfoil-CAD backend validation</text>',
        '<text x="24" y="58" font-family="sans-serif" font-size="13">Total: ' + str(len(cases)) + ' | Pass: ' + str(counts["PASS"]) + ' | Fail: ' + str(counts["FAIL"]) + ' | Skip: ' + str(counts["SKIP"]) + '</text>',
    ]
    for index, case in enumerate(cases):
        y = 82 + index * 22
        label = escape((case["test"][:66] + "…") if len(case["test"]) > 67 else case["test"])
        svg.append('<text x="24" y="' + str(y + 13) + '" font-family="sans-serif" font-size="11">' + label + '</text>')
        svg.append('<rect x="420" y="' + str(y) + '" width="230" height="15" rx="2" fill="' + colors[case["status"]] + '"/>')
        svg.append('<text x="660" y="' + str(y + 12) + '" font-family="sans-serif" font-size="10">' + case["status"] + '</text>')
    svg.append("</svg>")
    (REPORTS / "report.svg").write_text("\n".join(svg), encoding="utf-8")


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    test_paths = [AIRFOIL / "tests" / "test_bem_solver.py", AIRFOIL / "tests" / "test_composite_failure.py", AIRFOIL / "tests" / "test_progressive_damage.py", HERE / "test_backend_acceptance.py"]
    command = [sys.executable, "-m", "pytest", "-q", "--junitxml", str(JUNIT)] + [str(path) for path in test_paths]
    completed = subprocess.run(command, cwd=REPO, check=False)
    cases = collect_cases(JUNIT) if JUNIT.exists() else []
    write_reports(cases, completed.returncode)
    print("Validation report files written to: " + str(REPORTS))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
