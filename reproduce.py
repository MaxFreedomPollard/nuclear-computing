#!/usr/bin/env python3
# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""
Recompute every number, table and figure in the repository from the
committed data, in the order the CI does it, and say whether the tree came
back the same.

    python reproduce.py            run every step, about two minutes
    python reproduce.py --check    run every step, then fail if any tracked
                                   file other than a PNG differs from HEAD
                                   or any new file appeared
    python reproduce.py --list     print the steps and stop
    python reproduce.py --only gates,simulator
                                   run the steps whose script path contains
                                   one of the substrings

The steps are the ones .github/workflows/build.yml runs, and a test
(tests/test_repository.py) fails if the two lists drift apart. Nothing here
needs the network or OpenMC: the three transport directories are reported
from their committed tallies, and the OpenMC runs that regenerate those
tallies live in .github/workflows/openmc.yml and the Dockerfile.

What "the same" means. Every results file, CSV, JSON and SVG figure is
compared byte for byte, and under the pinned requirements.txt they match
on macOS and on Linux: the numbers are deterministic (seeded generators,
committed inputs) and the SVGs are drawn as vectors with no date and no
embedded raster. PNG figures are rasterised by the platform's own font and
antialiasing libraries and differ between operating systems by a few pixels,
so they are regenerated but not compared.
"""
import argparse
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))

# (script, what it regenerates); the order matters where a later step reads an earlier one's output
STEPS = [
    ("figures/make_figures.py", "figures 2 to 7: the laws, the keystone criterion, readiness"),
    ("gates/isomer_screen.py", "the isomer catalogue, the candidate table, figure 8 (cached IAEA data)"),
    ("transport/gate_demos.py", "the routine gates, transport/results.md"),
    ("transport/degree_check.py", "the degree checker, transport/degree_results.md"),
    ("transport/compiler_demo.py", "the compiler three ways, figure 14"),
    ("gates/edm_plan.py", "the energy division channel plan"),
    ("simulator/nuclear_ising.py", "the digital twin, figure 9"),
    ("simulator/components.py", "the component proofs of concept, figure 13"),
    ("transistor/make_transistor_figure.py", "figure 10"),
    ("transistor/make_datasheet_figure.py", "figure 12"),
    ("transistor/sealed_unit.py", "the ampoule computed, figure 11"),
    ("neutron/report.py", "the neutron gate from its committed tallies, figure 15"),
    ("photon/census.py", "the photon keystone census from the committed level schemes, figure 16"),
    ("ampoule/report.py", "the ampoule from its committed tallies, figure 17"),
    ("ampoule/compile.py", "the vessel compiled, figure 18"),
    ("build_html.py", "index.html"),
]


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="fail unless the tree (PNGs aside) is unchanged afterwards")
    ap.add_argument("--list", action="store_true", help="print the steps and stop")
    ap.add_argument("--only", default="", help="comma separated substrings of script paths to run")
    args = ap.parse_args()

    steps = [s for s in STEPS if not args.only or any(k in s[0] for k in args.only.split(","))]
    if args.list:
        for script, what in steps:
            print(f"{script:40s} {what}")
        return 0

    t_all = time.time()
    for script, what in steps:
        t0 = time.time()
        print(f"== {script}: {what}", flush=True)
        r = subprocess.run([sys.executable, os.path.join(ROOT, script)], cwd=ROOT,
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-4000:])
            print(r.stderr[-4000:])
            print(f"FAILED: {script}")
            return 1
        print(f"   ok, {time.time() - t0:.0f} s", flush=True)
    print(f"all {len(steps)} steps ran in {time.time() - t_all:.0f} s")

    if not args.check:
        return 0
    changed = [l[3:] for l in git("status", "--porcelain", "--untracked-files=all").splitlines()]
    changed = [p for p in changed if not p.lower().endswith(".png")]
    if changed:
        print("the tree is not the same after regeneration:")
        for p in changed:
            print("   ", p)
        print("(a changed results file means a number moved; a changed SVG means a figure moved; "
              "a new file means a step wrote something the repository does not track)")
        return 2
    print("the tree is the same after regeneration: every number, table and vector figure reproduced byte for byte")
    return 0


if __name__ == "__main__":
    sys.exit(main())
