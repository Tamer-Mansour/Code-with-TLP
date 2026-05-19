"""Master runner — seeds all courses.

Prerequisites: run `python -m app.seed` first to create subjects and course stubs.

Run from the backend/ directory:
    python seed/seed_all.py

All steps are idempotent and safe to re-run.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import seed.intro_algorithms_seed as algo1
import seed.intro_algorithms_seed_part2 as algo2
import seed.intro_algorithms_seed_part3 as algo3
import seed.angular_frontend_seed as angular
import seed.sql_fundamentals_seed as sql
import seed.python_basics_seed as python_basics

STEPS = [
    # ── Algorithms ────────────────────────────────────────────
    ("Algorithms  — Modules  1-4  (Getting Started → Data Structures)", algo1.seed),
    ("Algorithms  — Modules  5-8  (Hash Tables → Binary Heaps)",        algo2.seed),
    ("Algorithms  — Modules 9-12  (Graphs → Greedy & MST)",             algo3.seed),
    # ── Web Development ───────────────────────────────────────
    ("Angular     — Modules  1-8  (TypeScript → HTTP & RxJS)",          angular.seed),
    # ── Databases ─────────────────────────────────────────────
    ("SQL         — Modules  1-8  (Intro → DB Design)",                 sql.seed),
    # ── Programming Languages ─────────────────────────────────
    ("Python      — Modules  1-8  (Basics → Best Practices)",           python_basics.seed),
]


def main() -> None:
    print("=" * 60)
    print("  Studying App — full seed")
    print("=" * 60)
    print("  Courses:")
    print("    • Introduction to Algorithms  (12 modules)")
    print("    • Modern Frontend with Angular (8 modules)")
    print("    • SQL Fundamentals             (8 modules)")
    print("    • Python Programming Basics    (8 modules)")
    print("=" * 60)

    for label, fn in STEPS:
        print(f"\n>>> {label}")
        try:
            fn()
        except Exception:
            traceback.print_exc()
            print("\nSeed aborted at the step above.")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("  All courses seeded successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
