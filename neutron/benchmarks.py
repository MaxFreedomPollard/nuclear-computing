#!/usr/bin/env python3
# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""
Calibration of the instrument: handbook criticality benchmarks run with the
same code and the same data as the gate.

The International Handbook of Evaluated Criticality Safety Benchmark
Experiments (ICSBEP) publishes experiments whose k_eff is known to a few
tenths of a percent. Before the gate is believed, the code and data must
reproduce them at both ends of the spectrum the gate spans:

  HEU-MET-FAST-001, Godiva      a bare sphere of highly enriched uranium
                                metal: the fast spectrum and the fission
                                cross sections, nothing else
  LEU-SOL-THERM-001, SHEBA-II   an unreflected tank of 5 percent enriched
                                uranyl fluoride solution: the thermal
                                spectrum, the water scattering law, and
                                the material family of the gate
  LEU-SOL-THERM-004, STACY      a water reflected 60 cm tank of 10 percent
  case 1                        enriched uranyl nitrate solution: the
                                tightest thermal solution benchmark in the
                                handbook, water reflected like the gate

Geometries and atom densities follow the handbook benchmark models as
transcribed in the MIT CRPG benchmark collection (github.com/mit-crpg/
benchmarks, MIT licence), verified against it to machine precision. The
handbook k_eff values, and the JEFF-3.1 results on the same three cases,
are those tabulated in the JEFF-3.1 validation report (OECD/NEA JEFF
Report 21, Appendix 2). The JEFF-3.1 column is carried because it says
whether a discrepancy belongs to this calculation or to the benchmark:
SHEBA-II is overpredicted by every modern library, and a result that
lands on JEFF-3.1 rather than on the handbook is the library agreeing
with its peers, not the model being wrong. Writes benchmarks.json.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from data import ensure_data  # noqa: E402

# handbook benchmark model k_eff, and JEFF-3.1's result on the same case,
# both from JEFF Report 21 Appendix 2 (Godiva's handbook value is also
# quoted in ICSBEP and in LA-UR-15-23266)
BENCHMARK_K = {
    "HEU-MET-FAST-001":    dict(benchmark=(1.00000, 0.00100), jeff31=(0.99644, 0.00019)),
    "LEU-SOL-THERM-001":   dict(benchmark=(0.99910, 0.00290), jeff31=(1.01252, 0.00086)),
    "LEU-SOL-THERM-004-1": dict(benchmark=(0.99940, 0.00080), jeff31=(1.00046, 0.00076)),
}


def mat(name, nuclides, sab=None):
    import openmc
    m = openmc.Material(name=name)
    for n, a in nuclides:
        m.add_nuclide(n, a)
    m.set_density("sum")
    if sab:
        m.add_s_alpha_beta(sab)
    return m


def godiva():
    """HEU-MET-FAST-001 case 1: six concentric HEU shells with thin air
    gaps, as in the benchmark model."""
    import openmc
    radii = [1.0216, 1.0541, 6.2809, 6.2937, 7.7525, 7.7620, 8.2527, 8.2610, 8.7062, 8.7499]
    shells = [
        [("U234", 4.9357e-04), ("U235", 4.4936e-02), ("U238", 2.7213e-03)],
        [("U234", 4.9357e-04), ("U235", 4.5244e-02), ("U238", 2.4168e-03)],
        [("U234", 4.9357e-04), ("U235", 4.5268e-02), ("U238", 2.3930e-03)],
        [("U234", 4.9357e-04), ("U235", 4.5090e-02), ("U238", 2.5690e-03)],
        [("U234", 4.9357e-04), ("U235", 4.5239e-02), ("U238", 2.4215e-03)],
        [("U234", 4.8974e-04), ("U235", 4.4874e-02), ("U238", 2.4169e-03)],
    ]
    mats = [mat(f"HEU shell {i+1}", c) for i, c in enumerate(shells)]
    air = mat("air", [("N14", 3.5214e-05), ("O16", 1.5092e-05)])
    spheres = [openmc.Sphere(r=r) for r in radii]
    spheres[-1].boundary_type = "vacuum"
    fills = [mats[0], air, mats[1], air, mats[2], air, mats[3], air, mats[4], mats[5]]
    cells, prev = [], None
    for s, fill in zip(spheres, fills):
        region = -s if prev is None else (+prev & -s)
        cells.append(openmc.Cell(fill=fill, region=region))
        prev = s
    model = openmc.Model(geometry=openmc.Geometry(cells),
                         materials=openmc.Materials(mats + [air]))
    model.settings.source = openmc.IndependentSource(
        space=openmc.stats.Box((-1, -1, -1), (1, 1, 1)))
    return model


def sheba():
    """LEU-SOL-THERM-001, SHEBA-II: uranyl fluoride solution in a stainless
    steel tank with a central thimble, unreflected."""
    import openmc
    ss = mat("SS304L", [
        ("Cr50", 0.0007103206), ("Cr52", 0.01369782572), ("Cr53", 0.00155322348),
        ("Cr54", 0.0003866302), ("Mn55", 0.0017192), ("Fe54", 0.0035092211),
        ("Fe56", 0.05508726652), ("Fe57", 0.00127220522), ("Fe58", 0.00016930716),
        ("Ni58", 0.0049299929442), ("Ni60", 0.0018990244558), ("Ni61", 8.25492782e-05),
        ("Ni62", 0.000263203221), ("Ni64", 6.70301008e-05)])
    air = mat("air", [("N14", 3.5085011118e-05), ("N15", 1.28988882e-07),
                      ("O16", 1.5086280132e-05), ("O17", 5.719868e-09)])
    fuel = mat("uranyl fluoride solution", [
        ("U234", 6.7855e-07), ("U235", 0.00012377), ("U236", 1.2085e-06),
        ("U238", 0.0023508), ("H1", 0.056179), ("O16", 0.032954505507),
        ("O17", 1.2494493e-05), ("F19", 0.0051035)], sab="c_H_in_H2O")
    z1 = openmc.ZPlane(z0=-40.0, boundary_type="vacuum")
    z2, z3, z4 = openmc.ZPlane(z0=-37.1425), openmc.ZPlane(z0=7.6575), openmc.ZPlane(z0=39.375)
    z5 = openmc.ZPlane(z0=41.28, boundary_type="vacuum")
    c6, c7, c8 = openmc.ZCylinder(r=2.54), openmc.ZCylinder(r=3.175), openmc.ZCylinder(r=24.4475)
    c9 = openmc.ZCylinder(r=25.4, boundary_type="vacuum")
    cells = [
        openmc.Cell(fill=air, region=+z1 & -z2 & -c6),
        openmc.Cell(fill=ss, region=+z1 & -z2 & +c6 & -c9),
        openmc.Cell(fill=air, region=+z2 & -z4 & -c6),
        openmc.Cell(fill=ss, region=+z2 & -z4 & +c6 & -c7),
        openmc.Cell(fill=fuel, region=+z2 & -z3 & +c7 & -c8),
        openmc.Cell(fill=air, region=+z3 & -z4 & +c7 & -c8),
        openmc.Cell(fill=ss, region=+z2 & -z4 & +c8 & -c9),
        openmc.Cell(fill=air, region=+z4 & -z5 & -c6),
        openmc.Cell(fill=ss, region=+z4 & -z5 & +c6 & -c9),
    ]
    model = openmc.Model(geometry=openmc.Geometry(cells),
                         materials=openmc.Materials([ss, air, fuel]))
    model.settings.source = openmc.IndependentSource(
        space=openmc.stats.Box((-20, -20, -30), (20, 20, 5)), constraints={"fissionable": True})
    return model


def stacy():
    """LEU-SOL-THERM-004 case 1, STACY: 10 percent enriched uranyl nitrate
    in a 60 cm stainless steel tank, water reflected."""
    import openmc
    fuel = mat("uranyl nitrate solution", [
        ("U234", 6.3833e-07), ("U235", 7.9213e-05), ("U236", 7.9114e-08),
        ("U238", 0.00070556), ("H1", 0.056956), ("N14", 0.0028778),
        ("O16", 0.038014587009), ("O17", 1.4412991e-05)], sab="c_H_in_H2O")
    ss = mat("stainless steel", [
        ("C12", 4.3736e-05 * 0.9893), ("C13", 4.3736e-05 * 0.0107),
        ("Si28", 0.00098012480936), ("Si29", 4.976794132e-05), ("Si30", 3.280724932e-05),
        ("Mn55", 0.0011561), ("P31", 1.317e-05), ("S32", 1.88009591868e-06),
        ("S33", 1.481058558e-08), ("S34", 8.300507418e-08), ("S36", 2.8842156e-10),
        ("Ni58", 0.0056778176907), ("Ni60", 0.0021870852093), ("Ni61", 9.50710797e-05),
        ("Ni62", 0.0003031282035), ("Ni64", 7.71978168e-05),
        ("Cr50", 0.00072887375), ("Cr52", 0.01405560475), ("Cr53", 0.00159379275),
        ("Cr54", 0.00039672875), ("Fe54", 0.00347315745), ("Fe56", 0.05452114434),
        ("Fe57", 0.00125913099), ("Fe58", 0.00016756722)])
    water = mat("water at 25 C", [("H1", 0.066658), ("O16", 0.033316368309),
                                  ("O17", 1.2631691e-05)], sab="c_H_in_H2O")
    air = mat("air", [("N14", 3.9016e-05), ("O16", 1.0405054989e-05), ("O17", 3.945011e-09)])
    c1, c2 = openmc.ZCylinder(r=29.5), openmc.ZCylinder(r=29.8)
    c3 = openmc.ZCylinder(r=59.8, boundary_type="vacuum")
    z4 = openmc.ZPlane(z0=-32.0, boundary_type="vacuum")
    z5, z6, z7 = openmc.ZPlane(z0=-2.0), openmc.ZPlane(z0=0.0), openmc.ZPlane(z0=41.53)
    z8, z9 = openmc.ZPlane(z0=150.0), openmc.ZPlane(z0=152.5)
    z10 = openmc.ZPlane(z0=172.5, boundary_type="vacuum")
    cells = [
        openmc.Cell(fill=water, region=+z4 & -z5 & -c3),
        openmc.Cell(fill=ss, region=+z5 & -z6 & -c1),
        openmc.Cell(fill=fuel, region=+z6 & -z7 & -c1),
        openmc.Cell(fill=air, region=+z7 & -z8 & -c1),
        openmc.Cell(fill=ss, region=+z8 & -z9 & -c1),
        openmc.Cell(fill=ss, region=+z5 & -z9 & +c1 & -c2),
        openmc.Cell(fill=water, region=+z5 & -z9 & +c2 & -c3),
        openmc.Cell(fill=water, region=+z9 & -z10 & -c3),
    ]
    model = openmc.Model(geometry=openmc.Geometry(cells),
                         materials=openmc.Materials([fuel, ss, water, air]))
    model.settings.source = openmc.IndependentSource(
        space=openmc.stats.Box((-25, -25, 2), (25, 25, 38)), constraints={"fissionable": True})
    return model


CASES = [("HEU-MET-FAST-001", godiva), ("LEU-SOL-THERM-001", sheba),
         ("LEU-SOL-THERM-004-1", stacy)]


def main():
    import openmc
    p = argparse.ArgumentParser()
    p.add_argument("--quick", action="store_true")
    p.add_argument("--workdir", default=os.path.join(HERE, "work"))
    args = p.parse_args()
    ensure_data()
    exe = os.environ.get("OPENMC_EXEC", "openmc")
    particles, batches, inactive = (10000, 420, 40) if not args.quick else (4000, 90, 30)
    out = {"provenance": {"openmc_version": openmc.__version__,
                          "cross_sections": os.environ.get("OPENMC_CROSS_SECTIONS"),
                          "particles": particles, "batches": batches, "inactive": inactive},
           "cases": {}}
    for key, builder in CASES:
        model = builder()
        s = model.settings
        s.run_mode = "eigenvalue"
        s.particles, s.batches, s.inactive = particles, batches, inactive
        s.output = {"summary": False, "tallies": False}
        s.seed = 229
        wd = os.path.join(args.workdir, "bench_" + key)
        os.makedirs(wd, exist_ok=True)
        t0 = time.time()
        sp = model.run(cwd=wd, output=False, openmc_exec=exe)
        with openmc.StatePoint(sp) as st:
            k, dk = float(st.keff.n), float(st.keff.s)
        ref = BENCHMARK_K[key]
        kb, dkb = ref["benchmark"]
        out["cases"][key] = {"k": [k, dk], "benchmark": list(ref["benchmark"]),
                             "jeff31": list(ref["jeff31"]),
                             "seconds": round(time.time() - t0, 1)}
        print(f"  {key:22s} k = {k:.5f} +/- {dk:.5f}   handbook {kb:.5f} +/- {dkb:.5f}"
              f"   JEFF-3.1 {ref['jeff31'][0]:.5f}   ({time.time()-t0:.0f} s)", flush=True)
    path = os.path.join(HERE, "benchmarks.json")
    json.dump(out, open(path, "w"), indent=1)
    print("wrote", path)


if __name__ == "__main__":
    main()
