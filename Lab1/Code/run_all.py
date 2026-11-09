#!/usr/bin/env python3
"""
Run every Lab 1 experiment and save the real console output to ../outputs/.

Each output file starts with a short header (command, date, Python version,
exit code) followed by the exact text printed by the program (stdout and
stderr). Nothing is edited after capture.

Usage:
    python run_all.py
"""

import datetime
import os
import platform
import subprocess
import sys
from typing import List, Sequence, Tuple

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(os.path.dirname(CODE_DIR), "outputs")

# (output file, [list of argument lists]) - several commands may share a file.
RUNS: List[Tuple[str, List[List[str]]]] = [
    ("exp1_environment_setup_output.txt",
     [["exp1_environment_setup.py", "--json",
       "../outputs/exp1_environment_report.json"]]),
    ("exp1_invalid_input_output.txt",
     [["exp1_environment_setup.py", "--min-python", "3.x"]]),
    ("exp2_production_system_output.txt",
     [["exp2_production_system.py"]]),
    ("exp2_custom_input_output.txt",
     [["exp2_production_system.py", "-m", "25", "-t", "29", "-r", "no",
       "-s", "vegetative"]]),
    ("exp2_invalid_input_output.txt",
     [["exp2_production_system.py", "-m", "120", "-t", "30", "-r", "no",
       "-s", "mature"],
      ["exp2_production_system.py", "-m", "40", "-t", "30", "-r", "maybe",
       "-s", "mature"],
      ["exp2_production_system.py", "-m", "40"]]),
    ("exp3_water_jug_output.txt",
     [["exp3_water_jug.py", "--trace"]]),
    ("exp3_water_jug_any_jug_output.txt",
     [["exp3_water_jug.py", "-a", "4", "-b", "3", "-t", "2", "-g", "ANY"]]),
    ("exp3_water_jug_unsolvable_and_invalid_output.txt",
     [["exp3_water_jug.py", "-a", "6", "-b", "4", "-t", "3", "-g", "ANY"],
      ["exp3_water_jug.py", "-a", "3", "-b", "2", "-t", "5"],
      ["exp3_water_jug.py", "-a", "0", "-b", "3", "-t", "2"],
      ["exp3_water_jug.py", "-a", "four", "-b", "3", "-t", "2"]]),
    ("exp3_water_jug_benchmark_output.txt",
     [["exp3_water_jug.py", "--benchmark"]]),
]


def run_one(args: Sequence[str]) -> Tuple[int, str]:
    """Run one experiment and return (exit code, combined output)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    completed = subprocess.run([sys.executable, *args], cwd=CODE_DIR,
                               capture_output=True, text=True,
                               encoding="utf-8", env=env, check=False)
    return completed.returncode, completed.stdout + completed.stderr


def main() -> int:
    """Execute all runs and write the output files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for filename, commands in RUNS:
        blocks = []
        for args in commands:
            code, text = run_one(args)
            header = (f"$ python {' '.join(args)}\n"
                      f"# Captured: {stamp} | Python "
                      f"{platform.python_version()} | "
                      f"{platform.system()} | exit code: {code}\n")
            blocks.append(header + text.rstrip() + "\n")
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(blocks))
        print(f"saved outputs/{filename}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
