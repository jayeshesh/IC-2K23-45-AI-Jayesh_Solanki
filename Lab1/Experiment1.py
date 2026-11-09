#!/usr/bin/env python3
"""
Experiment 1: AI Development Environment Setup and Verification.

Course : Artificial Intelligence Laboratory (IC-703 C)
Lab    : Lab 1 - AI Environment Setup, Production Systems, Water Jug Problem

This script verifies that the machine is ready for the AI laboratory. It
    1. checks the Python interpreter version against a required minimum,
    2. reports platform and virtual-environment information,
    3. checks pip and the Jupyter tool chain (ipykernel, nbformat, ...),
    4. detects whether the code is running inside Google Colab,
    5. verifies the standard-library modules used by the Lab 1 programs,
    6. reports (for information only) the AI libraries used in later labs,
    7. runs a small sanity computation and measures its execution time,
    8. prints a READY / NOT READY verdict and optionally saves a JSON report.

Only "required" checks decide the verdict; "optional" checks are informative.

Usage examples
--------------
    python exp1_environment_setup.py
    python exp1_environment_setup.py --min-python 3.10
    python exp1_environment_setup.py --json ../outputs/env_report.json

Only the Python standard library is used.
"""

import argparse
import importlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import sys
import time
from dataclasses import asdict, dataclass
from typing import List, Optional, Sequence, Tuple

LINE_WIDTH = 72
EXIT_READY = 0
EXIT_NOT_READY = 1
EXIT_INVALID_INPUT = 2

# Standard-library modules imported by the Lab 1 programs.
LAB1_STDLIB_MODULES = ("argparse", "collections", "dataclasses", "math",
                       "operator", "time", "typing", "json")

# Jupyter tool chain used to open / execute the .ipynb notebook.
JUPYTER_PACKAGES = ("ipykernel", "nbformat", "nbconvert", "notebook",
                    "jupyterlab")

# Libraries of later labs (Lab 3 - Lab 7). Reported only, never required.
FUTURE_LAB_PACKAGES = (("numpy", "numpy"), ("pandas", "pandas"),
                       ("matplotlib", "matplotlib"),
                       ("scikit-learn", "sklearn"), ("torch", "torch"))


@dataclass
class CheckResult:
    """Result of one environment check."""

    name: str
    status: str          # PASS, FAIL, INFO or MISSING
    detail: str
    required: bool


def parse_version(text: str) -> Tuple[int, int]:
    """Convert 'MAJOR.MINOR' into a tuple; raise ValueError if malformed."""
    parts = text.strip().split(".")
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        raise ValueError(f"version must look like 3.10, got '{text}'")
    major, minor = int(parts[0]), int(parts[1])
    if major < 3:
        raise ValueError("only Python 3 versions are supported")
    return major, minor


def mask_home(path: str) -> str:
    """Hide the user's home directory in printed paths (privacy)."""
    home = os.path.expanduser("~")
    return path.replace(home, "~") if home and home != "~" else path


def package_version(distribution: str) -> Optional[str]:
    """Installed version of a distribution, or None if not installed."""
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def check_python(minimum: Tuple[int, int]) -> CheckResult:
    """Required: interpreter version must be >= minimum."""
    current = sys.version_info[:2]
    ok = current >= minimum
    detail = (f"Python {platform.python_version()} "
              f"({platform.python_implementation()}), required >= "
              f"{minimum[0]}.{minimum[1]}")
    return CheckResult("Python interpreter", "PASS" if ok else "FAIL",
                       detail, True)


def check_platform() -> List[CheckResult]:
    """Informational: OS, architecture, executable and virtual env."""
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    venv_detail = (f"active ({mask_home(sys.prefix)})" if in_venv
                   else "not active (system interpreter)")
    return [
        CheckResult("Operating system", "INFO",
                    f"{platform.system()} {platform.release()} "
                    f"({platform.machine()})", False),
        CheckResult("Interpreter path", "INFO",
                    mask_home(sys.executable), False),
        CheckResult("Virtual environment", "INFO", venv_detail, False),
    ]


def check_pip() -> CheckResult:
    """Required: pip is needed to install packages for later labs."""
    version = package_version("pip")
    if version:
        return CheckResult("pip package manager", "PASS",
                           f"pip {version}", True)
    return CheckResult("pip package manager", "FAIL",
                       "pip not found - install with: python -m "
                       "ensurepip --upgrade", True)


def check_jupyter() -> List[CheckResult]:
    """Optional: Jupyter components for running the .ipynb notebook."""
    results = []
    for package in JUPYTER_PACKAGES:
        version = package_version(package)
        results.append(CheckResult(
            f"Jupyter: {package}", "PASS" if version else "MISSING",
            version or "not installed (pip install notebook)", False))
    return results


def check_colab() -> CheckResult:
    """Informational: detect execution inside Google Colab."""
    in_colab = "google.colab" in sys.modules
    if not in_colab:
        try:
            in_colab = importlib.util.find_spec("google.colab") is not None
        except (ImportError, ValueError):
            # Parent package "google" absent -> certainly not Colab.
            in_colab = False
    return CheckResult("Google Colab runtime", "INFO",
                       "running inside Colab" if in_colab
                       else "not detected (local machine)", False)


def check_stdlib() -> CheckResult:
    """Required: every standard module used by Lab 1 must import."""
    failed = []
    for module in LAB1_STDLIB_MODULES:
        try:
            importlib.import_module(module)
        except ImportError:
            failed.append(module)
    if failed:
        return CheckResult("Lab 1 standard modules", "FAIL",
                           "cannot import: " + ", ".join(failed), True)
    return CheckResult("Lab 1 standard modules", "PASS",
                       f"{len(LAB1_STDLIB_MODULES)} modules imported: "
                       + ", ".join(LAB1_STDLIB_MODULES), True)


def check_future_libraries() -> List[CheckResult]:
    """Informational: libraries needed only from Lab 3 onwards."""
    results = []
    for distribution, _module in FUTURE_LAB_PACKAGES:
        version = package_version(distribution)
        results.append(CheckResult(
            f"Later labs: {distribution}", "INFO",
            version if version else "not installed (not needed in Lab 1)",
            False))
    return results


def check_sanity() -> CheckResult:
    """Required: run a small computation and time it."""
    start = time.perf_counter()
    total = sum(i * i for i in range(100_000))
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    expected = (99_999 * 100_000 * 199_999) // 6
    ok = total == expected
    return CheckResult("Sanity computation", "PASS" if ok else "FAIL",
                       f"sum of squares 0..99999 = {total} "
                       f"in {elapsed_ms:.2f} ms", True)


def run_checks(minimum: Tuple[int, int]) -> List[CheckResult]:
    """Run all checks in the documented order."""
    results = [check_python(minimum)]
    results += check_platform()
    results.append(check_pip())
    results += check_jupyter()
    results.append(check_colab())
    results.append(check_stdlib())
    results += check_future_libraries()
    results.append(check_sanity())
    return results


def print_report(results: Sequence[CheckResult], ready: bool) -> None:
    """Print the checks as an aligned table followed by the verdict."""
    print("=" * LINE_WIDTH)
    print(" EXPERIMENT 1 : AI DEVELOPMENT ENVIRONMENT SETUP AND VERIFICATION")
    print("=" * LINE_WIDTH)
    print(f"  {'Check':<28}{'Req.':<6}{'Status':<9}Detail")
    print("  " + "-" * (LINE_WIDTH - 2))
    for item in results:
        req = "yes" if item.required else "no"
        print(f"  {item.name:<28}{req:<6}{item.status:<9}{item.detail}")
    print("  " + "-" * (LINE_WIDTH - 2))
    required = [r for r in results if r.required]
    passed = sum(r.status == "PASS" for r in required)
    print(f"  Required checks passed : {passed}/{len(required)}")
    verdict = ("READY - environment is suitable for Lab 1"
               if ready else "NOT READY - fix the FAIL items above")
    print(f"  Environment status     : {verdict}")


def save_json(results: Sequence[CheckResult], ready: bool,
              path: str) -> None:
    """Write the report to a JSON file (directories created if needed)."""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    report = {"experiment": "Lab 1 - Experiment 1: Environment Setup",
              "ready": ready,
              "checks": [asdict(r) for r in results]}
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print(f"  JSON report saved to   : {os.path.basename(path)}")


def build_parser() -> argparse.ArgumentParser:
    """Command-line interface definition."""
    parser = argparse.ArgumentParser(
        description="Verify the Python/Jupyter environment for the AI lab.")
    parser.add_argument("--min-python", default="3.8",
                        help="minimum Python version, e.g. 3.10 "
                             "(default 3.8)")
    parser.add_argument("--json", metavar="PATH",
                        help="also save the report as JSON to PATH")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Program entry point; returns a process exit code."""
    args = build_parser().parse_args(argv)
    try:
        minimum = parse_version(args.min_python)
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return EXIT_INVALID_INPUT

    results = run_checks(minimum)
    ready = all(r.status == "PASS" for r in results if r.required)
    print_report(results, ready)
    if args.json:
        try:
            save_json(results, ready, args.json)
        except OSError as exc:
            print(f"Could not write JSON report: {exc}", file=sys.stderr)
    return EXIT_READY if ready else EXIT_NOT_READY


if __name__ == "__main__":
    sys.exit(main())
