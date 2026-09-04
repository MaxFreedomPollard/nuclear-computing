#!/usr/bin/env python3
# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""
The ampoule in real photon transport: the sealed machine of
transistor/SEALED.md and transistor/EMBODIMENT.md, built in OpenMC with the
official ENDF/B-VIII.0 photoatomic library, driven by the beta spectra of
its own ⁹⁰Sr/⁹⁰Y core, and measured where the design notes assumed.

The build note gives the machine at assembly grade; this script builds it
as a nested set of cylinders (dimensions in cm, materials by name, every
departure from the note recorded in results.md):

  core        an 8 x 10 mm SrTiO₃ pellet in a 1 mm 316L capsule, on the
              axis of a 30 x 40 mm krypton cell at 5 bar with 2 mm
              aluminium walls: the source and the lamp
  collar      a 2 mm tungsten sleeve around the lamp cell with one opening
              per site, the GATE terminal of every site, its angular width
              the thinning aperture
  compute     a borosilicate shell carrying 64 sites, 2 mm plastic
  shell       scintillator cells (CsI in one variant run) on an 8 x 8
              lattice of azimuth and height, with an optional 1 mm lead
              septum between two sectors
  boundary    a plastic scintillator ring and end caps (the 24 SiPM paddles),
              a silicon layer behind them, and four 5 mm CZT pixels
  shield      PMMA, 4 mm lead, 3 mm titanium, then air to a metre

The betas are handled by OpenMC's thick target bremsstrahlung treatment:
an electron born in the pellet deposits its energy there and emits the
bremsstrahlung a thick target of that material would, which is right for a
ceramic pellet whose radius exceeds the range of most of the spectrum and
is the approximation stated where the numbers are quoted. Because that
treatment makes the photons at the electron's birth whatever the geometry,
the source is taken in two steps: an emission stage measures the pellet
material's bremsstrahlung spectrum and yield per second from the two beta
spectra at their real activities, and every vessel stage is then driven by
photons born in the pellet with that spectrum at that rate, which is exact
within the treatment and a hundred times cheaper per photon.

Stages (each a fixed source run; every tally with its standard deviation to
tallies.json, already per second, because the sources carry the activity
as their strength: 1 GBq of each nuclide in equilibrium):

  emission    a speck of the pellet ceramic in vacuum with the two betas:
              the bremsstrahlung spectrum and yield per second, and the
              electron energy deposited per second
  source      the nominal ampoule: photons leaving the core, the field in
              every site, the boundary counts and their spectra, the energy
              deposited everywhere, the dose in air at contact and at one
              metre, the leakage out of the shield
  gate        the collar opening at 0, 25, 50, 75 and 100 percent of its
              nominal width: the transfer curve of the GATE terminal
  septum      the nominal ampoule with the lead septum in place
  synapse     the Green's function between sites: photons started in each
              site in turn, with the spectrum the source stage found there,
              tallied in every site: 64 x 64, open and with the septum

Run `python3 model.py` (about half an hour on a laptop) or `--quick`.
"""
import argparse
import glob
import json
import math
import os
import re
import shutil
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "neutron"))
sys.path.insert(0, HERE)
from data import ensure_data  # noqa: E402
import beta  # noqa: E402

ACTIVITY_BQ = 1.0e9          # of each of 90Sr and 90Y, in equilibrium
DECAYS_PER_S = 2.0 * ACTIVITY_BQ
EV_J = 1.602176634e-19

# ---- dimensions (cm), from the build note where it gives them ------------
R_PELLET, H_PELLET = 0.4, 0.5            # radius, half height
CAPSULE = 0.1                            # 316L wall
R_KR, H_KR = 1.5, 2.0                    # lamp cell inner
AL_WALL = 0.2
R_COLLAR_IN, R_COLLAR_OUT = 1.7, 1.9     # tungsten sleeve
R_SHELL_OUT, H_SHELL = 2.5, 4.0          # borosilicate compute shell
R_SITE, H_SITE, R_CELL = 2.2, 0.1, 0.113 # site lattice radius; cell half height; cell radius (2 mm cube's volume)
N_AZ, N_Z = 8, 8                         # 64 sites
Z_SITES = np.linspace(-3.5, 3.5, N_Z)
TH_SITES = np.arange(N_AZ) * 2 * math.pi / N_AZ
OPEN_HALF_DEG, OPEN_HALF_Z = 10.0, 0.3   # nominal opening: +/-10 degrees, +/-3 mm
R_TRIM = 2.7                             # air ring for the trim foils
R_BOUND, H_BOUND = 3.3, 5.0              # scintillator ring and caps
SI = 0.1
R_CZT_C, A_CZT = 3.0, 0.25               # CZT pixel centre radius, half edge
PMMA, PB, TI = 0.8, 0.4, 0.3             # shield layers
SEPTUM_ANGLE_DEG, SEPTUM_T = 22.5, 0.1   # lead sheet between sectors 0 and 1
R_WORLD = 102.0

R_PMMA = R_BOUND + SI + PMMA
R_PB = R_PMMA + PB
R_TI = R_PB + TI
H_PMMA = H_BOUND + SI + PMMA
H_PB = H_PMMA + PB
H_TI = H_PB + TI

E_EDGES = np.logspace(1, math.log10(2.5e6), 51)     # eV, for spectra

BUDGET = {"full": dict(emission=4_000_000, source=10_000_000, gate=3_000_000, septum=3_000_000, synapse=1_500_000),
          "quick": dict(emission=400_000, source=600_000, gate=200_000, septum=200_000, synapse=100_000)}


# ---------------------------------------------------------------- materials
def add_natural(m, symbol, fraction, kind):
    """Add an element as its natural isotopes, using only the isotopes the
    library holds and renormalising over them. Photon interactions depend
    on Z alone, so leaving out a rare isotope (¹⁸O at 0.2 percent, ²H at
    0.01 percent) changes nothing but the atomic mass at the third digit;
    OpenMC's own expansion refuses rather than guess, which is right for
    neutrons and needless here."""
    import openmc
    import openmc.data as od
    lib = add_natural.lib
    if lib is None:
        dl = od.DataLibrary.from_xml(os.environ["OPENMC_CROSS_SECTIONS"])
        lib = set()
        for entry in dl.libraries:
            if entry["type"] == "neutron":
                lib.update(entry["materials"])
        add_natural.lib = lib
    isos = [(n, a) for n, a in od.NATURAL_ABUNDANCE.items()
            if re.match(r"([A-Z][a-z]?)\d", n) and re.match(r"([A-Z][a-z]?)\d", n).group(1) == symbol and n in lib]
    if not isos:
        raise ValueError(f"no natural isotope of {symbol} in the library")
    if kind == "ao":
        tot = sum(a for _, a in isos)
        for n, a in isos:
            m.add_nuclide(n, fraction * a / tot, "ao")
    else:
        w = [(n, a * od.atomic_mass(n)) for n, a in isos]
        tot = sum(x for _, x in w)
        for n, x in w:
            m.add_nuclide(n, fraction * x / tot, "wo")


add_natural.lib = None


def materials():
    import openmc
    def mat(name, rho, comp, kind):
        m = openmc.Material(name=name)
        for el, frac in comp:
            add_natural(m, el, frac, kind)
        m.set_density("g/cm3", rho)
        return m
    return {
        "srtio3": mat("SrTiO3", 5.11, [("Sr", 1), ("Ti", 1), ("O", 3)], "ao"),
        "ss316": mat("316L", 8.0, [("Fe", 0.655), ("Cr", 0.17), ("Ni", 0.12), ("Mo", 0.025), ("Mn", 0.02), ("Si", 0.01)], "wo"),
        "kr": mat("krypton 5 bar", 5 * 3.749e-3, [("Kr", 1)], "ao"),
        "al": mat("aluminium", 2.70, [("Al", 1)], "ao"),
        "glass": mat("borosilicate", 2.23, [("O", 0.540), ("Si", 0.377), ("B", 0.040), ("Na", 0.028), ("Al", 0.012), ("K", 0.003)], "wo"),
        "pvt": mat("plastic scintillator", 1.032, [("C", 10), ("H", 11)], "ao"),
        "csi": mat("CsI", 4.51, [("Cs", 1), ("I", 1)], "ao"),
        "w": mat("tungsten", 19.3, [("W", 1)], "ao"),
        "pb": mat("lead", 11.35, [("Pb", 1)], "ao"),
        "ti": mat("titanium", 4.51, [("Ti", 1)], "ao"),
        "si": mat("silicon", 2.33, [("Si", 1)], "ao"),
        "pmma": mat("PMMA", 1.19, [("C", 5), ("H", 8), ("O", 2)], "ao"),
        "czt": mat("CZT", 5.8, [("Cd", 0.9), ("Zn", 0.1), ("Te", 1.0)], "ao"),
        "air": mat("air", 1.205e-3, [("N", 0.755), ("O", 0.245)], "wo"),
    }


# ---------------------------------------------------------------- geometry
def azimuth_plane(angle_rad, offset=0.0):
    """The plane through the z axis at that angle (offset shifts it along
    its normal); its positive side is the half space of larger azimuth."""
    import openmc
    return openmc.Plane(a=-math.sin(angle_rad), b=math.cos(angle_rad), c=0.0, d=offset)


def build(open_fraction=1.0, septum=False, site_material="pvt"):
    import openmc
    openmc.reset_auto_ids()
    M = materials()
    cells, parts = [], {"mats": M}

    def cyl(r, h):
        return -openmc.ZCylinder(r=r) & +openmc.ZPlane(z0=-h) & -openmc.ZPlane(z0=h)

    pellet = cyl(R_PELLET, H_PELLET)
    cap_cyl = openmc.ZCylinder(r=R_PELLET + CAPSULE)
    cap_lo, cap_hi = openmc.ZPlane(z0=-(H_PELLET + CAPSULE)), openmc.ZPlane(z0=H_PELLET + CAPSULE)
    capsule = -cap_cyl & +cap_lo & -cap_hi
    parts["capsule_surfaces"] = [cap_cyl, cap_lo, cap_hi]
    kr = cyl(R_KR, H_KR)
    alcan = cyl(R_KR + AL_WALL, H_KR + AL_WALL)
    collar = cyl(R_COLLAR_OUT, H_SHELL) & ~cyl(R_COLLAR_IN, H_SHELL)
    shell = cyl(R_SHELL_OUT, H_SHELL) & ~cyl(R_COLLAR_OUT, H_SHELL)
    inner_air = cyl(R_COLLAR_IN, H_SHELL) & ~alcan
    trim = cyl(R_TRIM, H_SHELL) & ~cyl(R_SHELL_OUT, H_SHELL)
    bound = cyl(R_BOUND, H_BOUND) & ~cyl(R_TRIM, H_SHELL)
    si = cyl(R_BOUND + SI, H_BOUND + SI) & ~cyl(R_BOUND, H_BOUND)
    pmma = cyl(R_PMMA, H_PMMA) & ~cyl(R_BOUND + SI, H_BOUND + SI)
    pb = cyl(R_PB, H_PB) & ~cyl(R_PMMA, H_PMMA)
    ti_cyl = openmc.ZCylinder(r=R_TI)
    ti_lo, ti_hi = openmc.ZPlane(z0=-H_TI), openmc.ZPlane(z0=H_TI)
    ti_outer = -ti_cyl & +ti_lo & -ti_hi
    parts["ti_surfaces"] = [ti_cyl, ti_lo, ti_hi]
    ti = ti_outer & ~cyl(R_PB, H_PB)
    contact = cyl(R_TI + 0.2, H_TI + 0.2) & ~ti_outer
    world = -openmc.Sphere(r=R_WORLD, boundary_type="vacuum")
    dose10 = -openmc.Sphere(r=10.5) & +openmc.Sphere(r=9.5)
    dose100 = -openmc.Sphere(r=101.0) & +openmc.Sphere(r=99.0)

    cells.append(openmc.Cell(name="pellet", fill=M["srtio3"], region=pellet))
    cells.append(openmc.Cell(name="capsule", fill=M["ss316"], region=capsule & ~pellet))
    cells.append(openmc.Cell(name="krypton", fill=M["kr"], region=kr & ~capsule))
    cells.append(openmc.Cell(name="lamp_wall", fill=M["al"], region=alcan & ~kr))
    cells.append(openmc.Cell(name="inner_air", fill=M["air"], region=inner_air))

    # the sites, and the collar openings that face them
    sites, openings = [], []
    for iz, z0 in enumerate(Z_SITES):
        for ia, th in enumerate(TH_SITES):
            x0, y0 = R_SITE * math.cos(th), R_SITE * math.sin(th)
            reg = (-openmc.ZCylinder(x0=x0, y0=y0, r=R_CELL)
                   & +openmc.ZPlane(z0=z0 - H_SITE) & -openmc.ZPlane(z0=z0 + H_SITE))
            c = openmc.Cell(name=f"site_{iz}_{ia}", fill=M[site_material], region=reg)
            sites.append(c)
            if open_fraction > 0:
                d = math.radians(OPEN_HALF_DEG * open_fraction)
                zc = z0 * (0.5 * (R_COLLAR_IN + R_COLLAR_OUT)) / R_SITE     # where the pellet's sight line crosses the collar
                wedge = (+azimuth_plane(th - d) & -azimuth_plane(th + d)
                         & +openmc.ZPlane(z0=zc - OPEN_HALF_Z) & -openmc.ZPlane(z0=zc + OPEN_HALF_Z))
                openings.append(collar & wedge)
    parts["sites"] = sites
    cells += sites
    collar_region = collar
    for o in openings:
        collar_region = collar_region & ~o
    cells.append(openmc.Cell(name="collar", fill=M["w"], region=collar_region))
    for i, o in enumerate(openings):
        cells.append(openmc.Cell(name=f"opening_{i}", fill=M["air"], region=o))

    shell_region = shell
    for c in sites:
        shell_region = shell_region & ~c.region
    if septum:
        a = math.radians(SEPTUM_ANGLE_DEG)
        sheet = (+azimuth_plane(a, -SEPTUM_T / 2) & -azimuth_plane(a, SEPTUM_T / 2)
                 & +openmc.Plane(a=math.cos(a), b=math.sin(a), c=0.0, d=0.0)   # the correct half
                 & shell)
        cells.append(openmc.Cell(name="septum", fill=M["pb"], region=sheet))
        shell_region = shell_region & ~sheet
        parts["septum"] = True
    cells.append(openmc.Cell(name="glass", fill=M["glass"], region=shell_region))
    cells.append(openmc.Cell(name="trim_air", fill=M["air"], region=trim))

    czts = []
    for k, (cx, cy) in enumerate([(R_CZT_C, 0), (0, R_CZT_C), (-R_CZT_C, 0), (0, -R_CZT_C)]):
        reg = (+openmc.XPlane(x0=cx - A_CZT) & -openmc.XPlane(x0=cx + A_CZT)
               & +openmc.YPlane(y0=cy - A_CZT) & -openmc.YPlane(y0=cy + A_CZT)
               & +openmc.ZPlane(z0=-A_CZT) & -openmc.ZPlane(z0=A_CZT))
        czts.append(openmc.Cell(name=f"czt_{k}", fill=M["czt"], region=reg))
    bound_region = bound
    for c in czts:
        bound_region = bound_region & ~c.region
    paddles = openmc.Cell(name="paddles", fill=M["pvt"], region=bound_region)
    cells += czts + [paddles]
    parts["czt"], parts["paddles"] = czts, paddles
    cells.append(openmc.Cell(name="sipm_si", fill=M["si"], region=si))
    cells.append(openmc.Cell(name="pmma", fill=M["pmma"], region=pmma))
    cells.append(openmc.Cell(name="lead", fill=M["pb"], region=pb))
    cells.append(openmc.Cell(name="titanium", fill=M["ti"], region=ti))
    contact_c = openmc.Cell(name="contact", fill=M["air"], region=contact)
    d10 = openmc.Cell(name="dose10", fill=M["air"], region=dose10)
    d100 = openmc.Cell(name="dose100", fill=M["air"], region=dose100)
    outer = cyl(R_TI + 0.2, H_TI + 0.2)
    cells += [contact_c, d10, d100,
              openmc.Cell(name="air", fill=M["air"], region=world & ~outer & ~dose10 & ~dose100)]
    parts.update(contact=contact_c, dose10=d10, dose100=d100)
    model = openmc.Model(geometry=openmc.Geometry(cells), materials=openmc.Materials(list(M.values())))
    s = model.settings
    s.run_mode = "fixed source"
    s.photon_transport = True
    s.electron_treatment = "ttb"
    s.output = {"summary": False, "tallies": False}
    s.seed = 90
    s.batches = 20
    parts["cells"] = {c.name: c for c in cells}
    return model, parts


def beta_sources():
    """The two betas of the core, uniform in the pellet, each with its
    activity as its strength, so that every tally is per second."""
    import openmc
    srcs = []
    for name in ("90Sr", "90Y"):
        T, Tm, N = beta.spectrum(name)
        srcs.append(openmc.IndependentSource(
            particle="electron",
            space=openmc.stats.CylindricalIndependent(
                r=openmc.stats.PowerLaw(0.0, R_PELLET, 1.0),
                phi=openmc.stats.Uniform(0.0, 2 * math.pi),
                z=openmc.stats.Uniform(-H_PELLET, H_PELLET)),
            energy=openmc.stats.Tabular(T * 1e3, np.append(N / np.diff(T * 1e3), 0.0), interpolation="histogram"),
            strength=ACTIVITY_BQ))
    return srcs


def emission_model():
    """A 0.2 mm speck of the pellet ceramic in vacuum, with the two betas:
    the thick target treatment stops each electron where it is born, so
    what crosses the speck's surface is the bremsstrahlung the pellet
    material makes, per second, before any of the vessel absorbs it."""
    import openmc
    openmc.reset_auto_ids()
    M = materials()
    sph = openmc.Sphere(r=0.02)
    world = openmc.Sphere(r=2.0, boundary_type="vacuum")
    cin = openmc.Cell(name="speck", fill=M["srtio3"], region=-sph)
    cout = openmc.Cell(name="vacuum", region=+sph & -world)
    model = openmc.Model(geometry=openmc.Geometry([cin, cout]), materials=openmc.Materials([M["srtio3"]]))
    s = model.settings
    s.run_mode = "fixed source"; s.photon_transport = True; s.electron_treatment = "ttb"
    s.output = {"summary": False, "tallies": False}; s.seed = 90; s.batches = 20
    srcs = []
    for src in beta_sources():
        src.space = openmc.stats.Point((0.0, 0.0, 0.0))
        srcs.append(src)
    s.source = srcs
    t = openmc.Tally(name="emitted")
    t.filters = [openmc.SurfaceFilter([sph]), openmc.CellFromFilter([cin]), openmc.CellFilter([cout]),
                 openmc.ParticleFilter(["photon"]), openmc.EnergyFilter(E_EDGES)]
    t.scores = ["current"]
    h = openmc.Tally(name="deposited"); h.filters = [openmc.CellFilter([cin])]; h.scores = ["heating"]
    model.tallies = openmc.Tallies([t, h])
    return model


def photon_source(emission):
    """Photons born uniformly in the pellet, isotropic, with the emission
    stage's spectrum and its yield per second as the strength."""
    import openmc
    spec = np.array(emission["spectrum_per_s"])
    total = float(spec.sum())
    dens = np.append(spec / np.diff(E_EDGES), 0.0)
    return openmc.IndependentSource(
        particle="photon",
        space=openmc.stats.CylindricalIndependent(
            r=openmc.stats.PowerLaw(0.0, R_PELLET, 1.0),
            phi=openmc.stats.Uniform(0.0, 2 * math.pi),
            z=openmc.stats.Uniform(-H_PELLET, H_PELLET)),
        energy=openmc.stats.Tabular(E_EDGES, dens, interpolation="histogram"),
        strength=total)


# ---------------------------------------------------------------- tallies
def add_tallies(model, parts, synapse=False):
    import openmc
    ph = openmc.ParticleFilter(["photon"])
    T = []
    t = openmc.Tally(name="sites"); t.filters = [openmc.CellFilter(parts["sites"]), ph]
    t.scores = ["total", "heating", "flux"]; T.append(t)
    if not synapse:
        t = openmc.Tally(name="site_spectrum"); t.filters = [openmc.CellFilter(parts["sites"]), ph, openmc.EnergyFilter(E_EDGES)]
        t.scores = ["flux"]; T.append(t)
        det = [parts["paddles"]] + parts["czt"]
        t = openmc.Tally(name="detectors"); t.filters = [openmc.CellFilter(det), ph]
        t.scores = ["total", "heating", "flux"]; T.append(t)
        t = openmc.Tally(name="detector_spectrum"); t.filters = [openmc.CellFilter(det), ph, openmc.EnergyFilter(E_EDGES)]
        t.scores = ["flux"]; T.append(t)
        cap = parts["cells"]["capsule"]
        t = openmc.Tally(name="core_out"); t.filters = [openmc.SurfaceFilter(parts["capsule_surfaces"]), openmc.CellFromFilter([cap]), openmc.CellFilter([parts["cells"]["krypton"]]), ph, openmc.EnergyFilter(E_EDGES)]
        t.scores = ["current"]; T.append(t)
        for name in ("contact", "dose10", "dose100"):
            t = openmc.Tally(name=name); t.filters = [openmc.CellFilter([parts[name]]), ph, openmc.EnergyFilter(E_EDGES)]
            t.scores = ["flux"]; T.append(t)
        t = openmc.Tally(name="leak"); t.filters = [openmc.SurfaceFilter(parts["ti_surfaces"]), openmc.CellFromFilter([parts["cells"]["titanium"]]), openmc.CellFilter([parts["contact"]]), ph, openmc.EnergyFilter(E_EDGES)]
        t.scores = ["current"]; T.append(t)
        allcells = [c for c in parts["cells"].values()]
        t = openmc.Tally(name="heating_by_cell"); t.filters = [openmc.CellFilter(allcells)]
        t.scores = ["heating"]; T.append(t)
        parts["heating_cells"] = [c.name for c in allcells]
    model.tallies = openmc.Tallies(T)


def harvest(sp_path, parts, synapse=False):
    import openmc
    out = {}
    nE = len(E_EDGES) - 1
    with openmc.StatePoint(sp_path) as sp:
        t = sp.get_tally(name="sites")
        out["sites"] = {s: [t.mean[:, 0, j].tolist(), t.std_dev[:, 0, j].tolist()] for j, s in enumerate(t.scores)}
        if not synapse:
            t = sp.get_tally(name="site_spectrum")
            out["site_spectrum"] = t.mean.reshape(len(parts["sites"]), nE).sum(axis=0).tolist()
            t = sp.get_tally(name="detectors")
            out["detectors"] = {"names": ["paddles"] + [f"czt_{k}" for k in range(4)],
                                **{s: [t.mean[:, 0, j].tolist(), t.std_dev[:, 0, j].tolist()] for j, s in enumerate(t.scores)}}
            t = sp.get_tally(name="detector_spectrum")
            m = t.mean.reshape(5, nE)
            out["detector_spectrum"] = {"paddles": m[0].tolist(), "czt": m[1:].sum(axis=0).tolist()}
            t = sp.get_tally(name="core_out")
            m = np.abs(t.mean.reshape(-1, nE)).sum(axis=0); sd = np.sqrt((t.std_dev.reshape(-1, nE) ** 2).sum(axis=0))
            out["core_out"] = {"mean": m.tolist(), "std": sd.tolist()}
            for name in ("contact", "dose10", "dose100"):
                t = sp.get_tally(name=name)
                out[name] = {"mean": t.mean.ravel().tolist(), "std": t.std_dev.ravel().tolist()}
            t = sp.get_tally(name="leak")
            m = np.abs(t.mean.reshape(-1, nE)).sum(axis=0); sd = np.sqrt((t.std_dev.reshape(-1, nE) ** 2).sum(axis=0))
            out["leak"] = {"mean": m.tolist(), "std": sd.tolist()}
            t = sp.get_tally(name="heating_by_cell")
            out["heating_by_cell"] = {n: [float(t.mean[i, 0, 0]), float(t.std_dev[i, 0, 0])]
                                      for i, n in enumerate(parts["heating_cells"])}
    return out


def run(model, workdir, exe):
    if os.path.isdir(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    t0 = time.time()
    sp = model.run(cwd=workdir, output=False, openmc_exec=exe)
    return sp, time.time() - t0


def volumes(parts):
    return {"site": math.pi * R_CELL ** 2 * 2 * H_SITE,
            "contact": math.pi * ((R_TI + 0.2) ** 2 * (H_TI + 0.2) - R_TI ** 2 * H_TI) * 2,
            "dose10": 4 / 3 * math.pi * (10.5 ** 3 - 9.5 ** 3),
            "dose100": 4 / 3 * math.pi * (101.0 ** 3 - 99.0 ** 3),
            "czt": (2 * A_CZT) ** 3}


# ---------------------------------------------------------------- protocol
def protocol(args):
    import openmc
    budget = BUDGET["quick" if args.quick else "full"]
    exe = os.environ.get("OPENMC_EXEC", "openmc")
    work = args.workdir
    path = os.path.join(HERE, "tallies.json")
    results = json.load(open(path)) if (os.path.exists(path) and args.only) else {"runs": {}}
    runs = results["runs"]
    minutes_before = results.get("provenance", {}).get("wall_clock_minutes", 0.0)   # --only adds to an existing run
    wanted = lambda n: (not args.only) or any(k in n for k in args.only.split(","))
    t_start = time.time()

    def record(name, model, parts, n, synapse=False, extra=None):
        add_tallies(model, parts, synapse)
        model.settings.particles = max(n // model.settings.batches, 100)
        sp, wall = run(model, os.path.join(work, name), exe)
        r = harvest(sp, parts, synapse)
        r.update(particles=int(model.settings.particles * model.settings.batches), seconds=round(wall, 1))
        if extra:
            r.update(extra)
        runs[name] = r
        print(f"  {name:18s} ({wall:.0f} s)", flush=True)
        json.dump(results, open(path, "w"), indent=1)
        return r

    print("the ampoule in photon transport: OpenMC", openmc.__version__, "| budget", "quick" if args.quick else "full", flush=True)

    # -- emission: the pellet's bremsstrahlung, per second ----------------
    if wanted("emission"):
        model = emission_model()
        model.settings.particles = max(budget["emission"] // 20, 100)
        sp, wall = run(model, os.path.join(work, "emission"), exe)
        with openmc.StatePoint(sp) as st:
            t = st.get_tally(name="emitted")
            spec = np.abs(t.mean.ravel()); spec_s = t.std_dev.ravel()
            h = st.get_tally(name="deposited")
            runs["emission"] = {"spectrum_per_s": spec.tolist(), "std": spec_s.tolist(),
                                "photons_per_s": float(spec.sum()),
                                "electron_heating_W": float(h.mean[0, 0, 0]) * EV_J,
                                "particles": int(model.settings.particles * 20), "seconds": round(wall, 1)}
        mids = np.sqrt(E_EDGES[:-1] * E_EDGES[1:])
        print(f"  emission           {spec.sum():.3e} photons/s, mean {(spec*mids).sum()/spec.sum()/1e3:.0f} keV, "
              f"{runs['emission']['electron_heating_W']*1e6:.0f} µW deposited by the betas   ({wall:.0f} s)", flush=True)
        json.dump(results, open(path, "w"), indent=1)
    emission = runs["emission"]

    # -- source -----------------------------------------------------------
    if wanted("source"):
        model, parts = build()
        model.settings.source = photon_source(emission)
        record("source", model, parts, budget["source"])
    # the build note leaves the site material open, plastic or CsI; the
    # vessel is run with plastic throughout, and once more here with CsI
    # cells so that the report can say what the denser choice buys
    if wanted("source_csi"):
        model, parts = build(site_material="csi")
        model.settings.source = photon_source(emission)
        record("source_csi", model, parts, budget["source"], extra={"site_material": "CsI"})

    # -- gate: the collar opening ----------------------------------------
    for f in (0.0, 0.25, 0.5, 0.75):
        name = f"gate_{int(f*100):03d}"
        if wanted(name):
            model, parts = build(open_fraction=f)
            model.settings.source = photon_source(emission)
            record(name, model, parts, budget["gate"], extra={"open_fraction": f})

    # the closed collar once more with CsI cells, for the CsI contrast
    if wanted("gate_000_csi"):
        model, parts = build(open_fraction=0.0, site_material="csi")
        model.settings.source = photon_source(emission)
        record("gate_000_csi", model, parts, budget["gate"], extra={"open_fraction": 0.0, "site_material": "CsI"})

    # -- septum ------------------------------------------------------------
    if wanted("septum"):
        model, parts = build(septum=True)
        model.settings.source = photon_source(emission)
        record("septum", model, parts, budget["septum"], extra={"septum": True})

    # -- synapse: the Green's function between sites ----------------------
    # The lattice is symmetric under rotation by 45 degrees and under z -> -z,
    # so a source at azimuth 0 and one of four heights stands for eight
    # sources by rotation and two by reflection; four runs give all 64
    # columns of G in the open geometry. The septum breaks the rotation, so
    # its runs are the same four sources next to it, compared column by
    # column with the open case.
    if any(wanted(f"synapse_{tag}") for tag in ("open", "septum")):
        spec = np.array(runs["source"]["site_spectrum"])
        mids = np.sqrt(E_EDGES[:-1] * E_EDGES[1:])
        spec = spec / spec.sum()
        energy = openmc.stats.Discrete(mids.tolist(), spec.tolist())
        rep = [iz * N_AZ for iz in range(N_Z // 2)]         # sites 0, 8, 16, 24: azimuth 0, z = -3.5 .. -0.5
        for tag, sep in (("open", False), ("septum", True)):
            if not wanted(f"synapse_{tag}"):
                continue
            meas, meas_s = {}, {}
            for j in rep:
                iz, ia = divmod(j, N_AZ)
                th, z0 = TH_SITES[ia], Z_SITES[iz]
                model, parts = build(septum=sep)
                model.settings.source = openmc.IndependentSource(
                    particle="photon",
                    space=openmc.stats.CylindricalIndependent(
                        r=openmc.stats.PowerLaw(0.0, R_CELL, 1.0), phi=openmc.stats.Uniform(0, 2 * math.pi),
                        z=openmc.stats.Uniform(z0 - H_SITE, z0 + H_SITE),
                        origin=(R_SITE * math.cos(th), R_SITE * math.sin(th), 0.0)),
                    energy=energy)
                add_tallies(model, parts, synapse=True)
                model.settings.particles = max(budget["synapse"] // 20, 100)
                sp, wall = run(model, os.path.join(work, f"syn_{tag}_{j}"), exe)
                with openmc.StatePoint(sp) as st:
                    t = st.get_tally(name="sites")
                    meas[j] = t.mean[:, 0, 0].copy(); meas_s[j] = t.std_dev[:, 0, 0].copy()
                shutil.rmtree(os.path.join(work, f"syn_{tag}_{j}"), ignore_errors=True)
                print(f"  synapse_{tag} site {j:2d}: self {meas[j][j]:.4f}, to all others {meas[j].sum()-meas[j][j]:.2e}   ({wall:.0f} s)", flush=True)
            G = np.zeros((64, 64)); S = np.zeros((64, 64))
            for j in range(64):
                iz, ia = divmod(j, N_AZ)
                flip = iz >= N_Z // 2
                jz = (N_Z - 1 - iz) if flip else iz
                src = jz * N_AZ                                    # the representative source
                if sep and (ia != 0 or flip):
                    continue                                       # only the measured columns
                for k in range(64):
                    kz, ka = divmod(k, N_AZ)
                    kz_m = (N_Z - 1 - kz) if flip else kz
                    ka_m = (ka - ia) % N_AZ
                    km = kz_m * N_AZ + ka_m
                    G[k, j] = meas[src][km]; S[k, j] = meas_s[src][km]
            runs[f"synapse_{tag}"] = {"G": G.tolist(), "std": S.tolist(), "sources": rep,
                                     "measured_columns": ([j for j in range(64)] if not sep else rep),
                                     "particles_per_source": int(max(budget["synapse"] // 20, 100) * 20),
                                     "note": "columns outside measured_columns are filled by the lattice symmetry"}
            json.dump(results, open(path, "w"), indent=1)

    import openmc.data
    dE, dh = openmc.data.dose_coefficients("photon", geometry="AP")
    results["provenance"] = {
        "dose_coefficients_ICRP116_AP": {"energy_eV": np.asarray(dE).tolist(), "pSv_cm2": np.asarray(dh).tolist()},
        "openmc_version": openmc.__version__, "library": "ENDF/B-VIII.0 official OpenMC HDF5 distribution (photoatomic, EPICS2014 based)",
        "electron_treatment": "thick target bremsstrahlung", "budget": "quick" if args.quick else "full",
        "decays_per_s": DECAYS_PER_S, "activity_Bq_each": ACTIVITY_BQ, "tallies_are": "per second",
        "energy_edges_eV": E_EDGES.tolist(),
        "volumes_cm3": volumes(None), "sites": 64, "site_layout": {"radius_cm": R_SITE, "z_cm": Z_SITES.tolist(), "azimuths_rad": TH_SITES.tolist()},
        "geometry_cm": {"pellet": [R_PELLET, H_PELLET], "capsule_wall": CAPSULE, "lamp_cell": [R_KR, H_KR], "al_wall": AL_WALL,
                        "collar": [R_COLLAR_IN, R_COLLAR_OUT], "shell_out": R_SHELL_OUT, "shell_half_height": H_SHELL,
                        "opening_half_deg": OPEN_HALF_DEG, "opening_half_z": OPEN_HALF_Z, "trim_out": R_TRIM,
                        "boundary": [R_BOUND, H_BOUND], "si": SI, "czt_half_edge": A_CZT, "pmma": PMMA, "pb": PB, "ti": TI,
                        "outer_radius": R_TI, "outer_half_length": H_TI, "septum_deg": SEPTUM_ANGLE_DEG, "septum_t": SEPTUM_T},
        "wall_clock_minutes": round(minutes_before + (time.time() - t_start) / 60, 1),
    }
    json.dump(results, open(path, "w"), indent=1)
    print(f"wrote {path} ({(time.time()-t_start)/60:.0f} min)")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--quick", action="store_true")
    p.add_argument("--only", default="")
    p.add_argument("--workdir", default=os.path.join(HERE, "work"))
    args = p.parse_args()
    ensure_data()
    protocol(args)


if __name__ == "__main__":
    main()
