#!/usr/bin/env python3
# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""
Calibration of the photon instrument before it is pointed at the ampoule.

Three checks, cheapest first, each against a reference that is not OpenMC:

  attenuation    the total mass attenuation coefficient of lead, iron,
                 tungsten and water at 100, 500, 1000 and 2000 keV, read
                 from the library files the model uses, against the NIST
                 XCOM values (Hubbell and Seltzer): the data
  transmission   the fraction of a pencil beam that crosses a slab without
                 a single collision and at its own energy, Monte Carlo
                 against exp(-mu x) with the XCOM coefficient: the transport
  bremsstrahlung the energy an electron stopped in a thick target radiates,
                 in water and iron at 0.5, 1 and 2 MeV, against the
                 textbook thick target rule Y = 6e-4 Z T / (1 + 6e-4 Z T),
                 which is good to a few tens of percent and known to run
                 high at low Z; OpenMC's thick
                 target bremsstrahlung treatment was validated by its
                 authors against ESTAR and Geant4 (Lund and Romano 2018),
                 and this is only the check that the version and data in
                 hand behave as published: the source term

Writes calibration.json, read by report.py.
"""
import json
import math
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "neutron"))
from data import ensure_data  # noqa: E402
sys.path.insert(0, HERE)
from model import add_natural  # noqa: E402

NA = 6.02214076e23
# NIST XCOM total attenuation with coherent scattering, cm2/g
XCOM = {
    "Pb": {"M": 207.2, "rho": 11.35, "mu": {100e3: 5.549, 500e3: 0.1614, 1e6: 0.07102, 2e6: 0.04606}},
    "Fe": {"M": 55.845, "rho": 7.874, "mu": {100e3: 0.3717, 500e3: 0.08414, 1e6: 0.05995, 2e6: 0.04265}},
    "W":  {"M": 183.84, "rho": 19.3, "mu": {100e3: 4.438, 500e3: 0.1378, 1e6: 0.06618, 2e6: 0.04433}},
}
WATER = {"rho": 1.0, "mu": {100e3: 0.1707, 500e3: 0.09687, 1e6: 0.07072, 2e6: 0.04942}}
Z_EFF = {"water": 7.42, "iron": 26.0}


def attenuation(xs_path):
    import openmc.data
    root = os.path.dirname(xs_path)
    rows = []
    for el, d in XCOM.items():
        ph = openmc.data.IncidentPhoton.from_hdf5(os.path.join(root, "photon", el + ".h5"))
        for E, ref in d["mu"].items():
            tot = sum(ph.reactions[mt].xs(np.array([E]))[0] for mt in (502, 504, 515, 517, 522) if mt in ph.reactions)
            mu = tot * 1e-24 * NA / d["M"]
            rows.append(dict(material=el, E_keV=E / 1e3, library=mu, xcom=ref, ratio=mu / ref))
    # water: 2 H + O by mass
    H = openmc.data.IncidentPhoton.from_hdf5(os.path.join(root, "photon", "H.h5"))
    O = openmc.data.IncidentPhoton.from_hdf5(os.path.join(root, "photon", "O.h5"))
    for E, ref in WATER["mu"].items():
        def m(ph, M):
            return sum(ph.reactions[mt].xs(np.array([E]))[0] for mt in (502, 504, 515, 517, 522) if mt in ph.reactions) * 1e-24 * NA / M
        mu = (2 * 1.008 * m(H, 1.008) + 15.999 * m(O, 15.999)) / 18.015
        rows.append(dict(material="water", E_keV=E / 1e3, library=mu, xcom=ref, ratio=mu / ref))
    return rows


def slab_model(material, thickness, E):
    import openmc
    m = openmc.Material(name=material)
    if material == "water":
        add_natural(m, "H", 2, "ao"); add_natural(m, "O", 1, "ao"); m.set_density("g/cm3", 1.0)
    else:
        add_natural(m, material, 1, "ao"); m.set_density("g/cm3", XCOM[material]["rho"])
    x0, x1 = openmc.XPlane(x0=0.0), openmc.XPlane(x0=thickness)
    box = openmc.model.RectangularParallelepiped(-1.0, thickness + 1.0, -50, 50, -50, 50, boundary_type="vacuum")
    slab = +x0 & -x1 & -box
    cells = [openmc.Cell(fill=m, region=slab), openmc.Cell(region=-box & ~slab)]
    model = openmc.Model(geometry=openmc.Geometry(cells), materials=openmc.Materials([m]))
    s = model.settings
    s.run_mode = "fixed source"; s.photon_transport = True; s.electron_treatment = "ttb"
    s.batches = 10; s.particles = 40000; s.output = {"summary": False, "tallies": False}
    s.source = openmc.IndependentSource(particle="photon", space=openmc.stats.Point((-0.5, 0, 0)),
                                        angle=openmc.stats.Monodirectional((1, 0, 0)),
                                        energy=openmc.stats.Discrete([E], [1.0]))
    t = openmc.Tally(name="out")
    t.filters = [openmc.SurfaceFilter([x1]), openmc.CellFromFilter([cells[0]]), openmc.CellFilter([cells[1]]),
                 openmc.ParticleFilter(["photon"]), openmc.CollisionFilter([0]),
                 openmc.EnergyFilter([E * 0.999, E * 1.001])]
    # both filters are needed: a coherent scatter keeps the energy but counts as
    # a collision, and a secondary photon (annihilation, fluorescence, the
    # bremsstrahlung of a photoelectron) has never collided but is not the beam
    t.scores = ["current"]
    model.tallies = openmc.Tallies([t])
    return model


def brems_model(material, T):
    """An electron at the centre of a small sphere of the material. The thick
    target treatment stops the electron where it is born whatever the
    sphere's size, so a sphere a fraction of a millimetre across lets every
    bremsstrahlung photon out unabsorbed: what crosses its surface is what
    was radiated."""
    import openmc
    m = openmc.Material(name=material)
    if material == "water":
        add_natural(m, "H", 2, "ao"); add_natural(m, "O", 1, "ao"); m.set_density("g/cm3", 1.0)
        R = 0.02
    else:
        add_natural(m, "Fe", 1, "ao"); m.set_density("g/cm3", 7.874)
        R = 0.02
    sph = openmc.Sphere(r=R)
    world = openmc.Sphere(r=R + 5.0, boundary_type="vacuum")
    cin = openmc.Cell(fill=m, region=-sph)
    cout = openmc.Cell(region=+sph & -world)
    model = openmc.Model(geometry=openmc.Geometry([cin, cout]), materials=openmc.Materials([m]))
    s = model.settings
    s.run_mode = "fixed source"; s.photon_transport = True; s.electron_treatment = "ttb"
    s.batches = 10; s.particles = 40000; s.output = {"summary": False, "tallies": False}
    s.source = openmc.IndependentSource(particle="electron", space=openmc.stats.Point((0, 0, 0)),
                                        energy=openmc.stats.Discrete([T], [1.0]))
    edges = np.logspace(3, math.log10(T * 1.01), 60)
    t = openmc.Tally(name="out")
    t.filters = [openmc.SurfaceFilter([sph]), openmc.CellFromFilter([cin]), openmc.CellFilter([cout]),
                 openmc.ParticleFilter(["photon"]), openmc.EnergyFilter(edges)]
    t.scores = ["current"]
    model.tallies = openmc.Tallies([t])
    return model, edges


def main():
    import openmc
    xs = ensure_data()
    exe = os.environ.get("OPENMC_EXEC", "openmc")
    work = os.path.join(HERE, "work", "calibration")
    out = {"attenuation": attenuation(xs), "transmission": [], "bremsstrahlung": []}
    for r in out["attenuation"]:
        print(f"  {r['material']:6s} {r['E_keV']:6.0f} keV  library {r['library']:.4f}  XCOM {r['xcom']:.4f}  ratio {r['ratio']:.3f}")
    for material, thickness, E in (("Pb", 1.0, 1e6), ("Pb", 0.5, 500e3), ("Fe", 5.0, 1e6), ("W", 0.5, 2e6), ("water", 10.0, 1e6)):
        model = slab_model(material, thickness, E)
        wd = os.path.join(work, f"slab_{material}_{int(E/1e3)}")
        shutil.rmtree(wd, ignore_errors=True); os.makedirs(wd)
        sp = model.run(cwd=wd, output=False, openmc_exec=exe)
        with openmc.StatePoint(sp) as st:
            t = st.get_tally(name="out"); mc, sd = float(abs(t.mean.sum())), float(np.sqrt((t.std_dev ** 2).sum()))
        rho = 1.0 if material == "water" else XCOM[material]["rho"]
        mu = (WATER if material == "water" else XCOM[material])["mu"][E]
        exp = math.exp(-mu * rho * thickness)
        out["transmission"].append(dict(material=material, thickness_cm=thickness, E_keV=E / 1e3, mc=mc, mc_std=sd, expected=exp, ratio=mc / exp))
        print(f"  slab {material:6s} {thickness:4.1f} cm {E/1e3:5.0f} keV  uncollided MC {mc:.4f} ± {sd:.4f}  exp(-mu x) {exp:.4f}  ratio {mc/exp:.3f}")
    for material in ("water", "iron"):
        for T in (0.5e6, 1e6, 2e6):
            model, edges = brems_model(material, T)
            wd = os.path.join(work, f"brems_{material}_{int(T/1e3)}")
            shutil.rmtree(wd, ignore_errors=True); os.makedirs(wd)
            sp = model.run(cwd=wd, output=False, openmc_exec=exe)
            with openmc.StatePoint(sp) as st:
                t = st.get_tally(name="out"); cur = np.abs(t.mean.ravel())
            mids = np.sqrt(edges[:-1] * edges[1:])
            radiated = float((cur * mids).sum())
            Z = Z_EFF[material]
            rule = 6e-4 * Z * (T / 1e6) / (1 + 6e-4 * Z * (T / 1e6))
            out["bremsstrahlung"].append(dict(material=material, T_keV=T / 1e3, photons_per_electron=float(cur.sum()),
                                              radiated_fraction=radiated / T, rule=rule, ratio=radiated / T / rule))
            print(f"  brems {material:5s} {T/1e3:5.0f} keV  radiated fraction {radiated/T:.4f}  rule {rule:.4f}  ratio {radiated/T/rule:.2f}  photons/e {cur.sum():.3f}")
    json.dump(out, open(os.path.join(HERE, "calibration.json"), "w"), indent=1)
    print("wrote calibration.json")


if __name__ == "__main__":
    main()
