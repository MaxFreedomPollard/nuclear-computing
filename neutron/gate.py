#!/usr/bin/env python3
# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""
The neutron sector gate, computed: two coupled subcritical solution tanks
in OpenMC with the official ENDF/B-VIII.0 library.

The unit is the neutron gate of the reference transistor (transistor/README.md,
Scale 3), built from parts a criticality safety engineer would recognise:

  two cylindrical tanks of 4.9 percent enriched uranyl fluoride solution
  (the composition of handbook benchmark LEU-SOL-THERM-002; benchmarks.py
  reproduces the handbook with this same code and data), each with
  k about 0.90 on its own, standing side by side in a water bath (the
  BODY), 3 cm of water apart, with an absorber that can be lowered into the
  water between them (the GATE): a 1 mm cadmium sheet, the classic thermal
  filter, or a 2 cm boron carbide blade. A Cf-252 point source in tank A
  is the SOURCE terminal; the fission rate in tank B is the DRAIN; the
  neutron population in B is the CHANNEL.

Everything at k < 1, always. The script runs the protocol below and writes
every raw tally, with its Monte Carlo uncertainty, to tallies.json;
report.py turns that file into results.md and figure 15. Stages:

  alone      eigenvalue of each tank by itself: M = 1/(1 - k) is a number
  coupled    eigenvalue of the pair: open, the cadmium sheet at 25, 50, 75
             and 100 percent insertion, and the boron carbide blade, each
             with a Shannon entropy trace to show the source converged,
             writing the converged fission bank for the coupling stage
  coupling   the fission matrix: fission neutrons born in tank j (the
             fundamental mode source restricted to j, fission treated as
             capture so exactly one generation is counted) produce K_ij
             fission neutrons in tank i; the dominant eigenvalue of K must
             reproduce the transport k of the pair, and a control run on
             the unsplit bank must reproduce it directly
  firstgen   the first generation response c_i of each tank to a driver
             neutron (Cf-252 in A, Cf-252 in B, 14.1 MeV in B)
  gate       the gate itself, fixed source with full multiplication, for
             every drive and every absorber state: drain current per
             source neutron, the neutron budget, the fission emission
             spectrum in B (level restoration) and the spectrum arriving
             at B through its wall (the input that was restored)
  feedback   the pair at 350 K solution temperature, with and without the
             thermal expansion of the liquid: the only signal controlled
             inhibition the neutron sector has, priced

Run `python3 gate.py` (about forty minutes on a laptop) or `--quick` for a
tenth of the particles. Requires OpenMC (conda-forge) and the data that
data.py fetches on first use.
"""
import argparse
import glob
import json
import math
import os
import shutil
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from data import ensure_data  # noqa: E402

# ---------------------------------------------------------------------------
# the unit: dimensions and materials (design choices are marked as such)
# ---------------------------------------------------------------------------
R_TANK = 24.0        # cm, inner radius; chosen so that k(alone) is about 0.90
H_TANK = 40.0        # cm, solution height; same choice
WALL = 0.1588        # cm, the aluminium shell of LEU-SOL-THERM-002
GAP = 3.0            # cm of water between the two tank walls (design choice)
ABSORBERS = {        # the GATE: material, thickness (cm)
    "cd":  ("cadmium", 0.10),     # a standard 1 mm cadmium sheet
    "b4c": ("b4c", 2.00),         # a 2 cm boron carbide blade
}
ABS_MARGIN = 6.0     # cm the absorber overhangs the tanks in y and z
REFL = 20.0          # cm of water beyond the tanks on every side
X_TANK = R_TANK + WALL + GAP / 2      # tank axes at x = -X_TANK and +X_TANK

CF252_WATT = (1.18e6, 1.03419e-6)     # a (eV), b (1/eV): Cf-252 spontaneous fission, Froehner 1990 fit (mean 2.13 MeV)
DT_ENERGY = 14.1e6                    # eV, deuterium tritium fusion neutrons

# uranyl fluoride solution: the benchmark model composition of
# LEU-SOL-THERM-002 (atoms per barn cm), 4.9 percent enriched
SOLUTION = [("U234", 2.3271e-07), ("U235", 5.6655e-05), ("U238", 1.0878e-03),
            ("F19", 2.2893e-03), ("O16", 0.033389340642),
            ("O17", 1.2659358e-05), ("H1", 0.062226)]
# type 1100 aluminium, same benchmark
AL1100 = [("Al27", 0.059699), ("Si28", 0.000509126279536),
          ("Si29", 2.5851979831999998e-05), ("Si30", 1.7041740632e-05),
          ("Cu63", 3.5518206e-05), ("Cu65", 1.5845794e-05),
          ("Zn64", 1.2271848600000001e-05), ("Zn66", 6.9208534e-06),
          ("Zn67", 1.0083032e-06), ("Zn68", 4.604751e-06),
          ("Zn70", 1.522438e-07), ("Mn55", 1.4853e-05)]
WATER = [("H1", 0.066659), ("O16", 0.033316368309), ("O17", 1.2631690999999998e-05)]
CD_DENSITY = 8.65    # g/cm3, natural cadmium
B4C_DENSITY = 2.52   # g/cm3, boron carbide, natural boron

# water density relative to 294 K, for the thermal expansion of the liquid
# (the solution is assumed to expand as water does; stated in the README)
WATER_RHO = {294.0: 0.99795, 350.0: 0.97368}

ENERGY_EDGES = np.logspace(-5, math.log10(2e7), 61)   # eV, five bins per decade

# particle budgets: full and quick
BUDGET = {
    "full":  dict(eig_p=20000, eig_b=200, eig_i=50, coupling=2_000_000,
                  firstgen=1_000_000, gate=400_000),
    "quick": dict(eig_p=4000, eig_b=100, eig_i=30, coupling=200_000,
                  firstgen=100_000, gate=40_000),
}

STATES = ["open", "cd", "b4c"]          # absorber states used by every stage
DRIVES = {
    "cfA":  [("cf", -1)],
    "cfB":  [("cf", +1)],
    "cfAB": [("cf", -1), ("cf", +1)],
    "dtB":  [("dt", +1)],
}


# ---------------------------------------------------------------------------
# model builder
# ---------------------------------------------------------------------------
def make_materials(temperature=294.0, expand=False, absorber=None):
    """The absorber material is built only when its nuclides are needed, so a
    library without boron can still run every cadmium and open configuration."""
    import openmc
    scale = WATER_RHO[temperature] / WATER_RHO[294.0] if expand else 1.0
    mats = {}
    for tag in ("A", "B"):
        m = openmc.Material(name=f"solution_{tag}")
        for n, a in SOLUTION:
            m.add_nuclide(n, a * scale)
        m.set_density("sum")
        m.add_s_alpha_beta("c_H_in_H2O")
        m.temperature = temperature
        mats[f"sol_{tag}"] = m
    al = openmc.Material(name="al1100")
    for n, a in AL1100:
        al.add_nuclide(n, a)
    al.set_density("sum")
    mats["al"] = al
    w = openmc.Material(name="water")
    for n, a in WATER:
        w.add_nuclide(n, a * scale)
    w.set_density("sum")
    w.add_s_alpha_beta("c_H_in_H2O")
    w.temperature = temperature
    mats["water"] = w
    if absorber == "cd":
        cd = openmc.Material(name="cadmium")
        cd.add_element("Cd", 1.0)
        cd.set_density("g/cm3", CD_DENSITY)
        mats["cadmium"] = cd
    if absorber == "b4c":
        b4c = openmc.Material(name="b4c")
        b4c.add_element("B", 4.0)
        b4c.add_nuclide("C12", 0.9893)
        b4c.add_nuclide("C13", 0.0107)
        b4c.set_density("g/cm3", B4C_DENSITY)
        mats["b4c"] = b4c
    return mats


def build(tank_a=True, tank_b=True, absorber=None, fraction=1.0,
          temperature=294.0, expand=False, half=False):
    """Geometry of the pair. Returns (model, parts) with the cells, surfaces
    and materials the tallies refer to.

    With half=True only the x > 0 side is built and the plane x = 0 is
    reflective. Because the full geometry is mirror symmetric in x, the
    half model's eigenvalue is exactly the symmetric fundamental mode of
    the pair, and it has no tilt mode to converge at all: the slowly
    mixing second eigenvector of Section 3.1 does not exist in it. Its
    fission bank, mirrored, is therefore the fundamental mode source that
    the fission matrix needs, obtained by construction rather than by
    waiting."""
    import openmc
    openmc.reset_auto_ids()
    mats = make_materials(temperature, expand, absorber if fraction > 0 else None)
    cells, parts = [], {"mats": mats}
    half_x = X_TANK + R_TANK + WALL + REFL
    half_y = R_TANK + WALL + REFL
    half_z = H_TANK / 2 + WALL + REFL
    mirror_plane = None
    if half:
        tank_a = False
        mirror_plane = openmc.XPlane(x0=0.0, boundary_type="reflective")
        box = (+mirror_plane
               & -openmc.XPlane(x0=half_x, boundary_type="vacuum")
               & +openmc.YPlane(y0=-half_y, boundary_type="vacuum")
               & -openmc.YPlane(y0=half_y, boundary_type="vacuum")
               & +openmc.ZPlane(z0=-half_z, boundary_type="vacuum")
               & -openmc.ZPlane(z0=half_z, boundary_type="vacuum"))
        water_region = box
    else:
        box = openmc.model.RectangularParallelepiped(
            -half_x, half_x, -half_y, half_y, -half_z, half_z, boundary_type="vacuum")
        water_region = -box

    for tag, present, x0 in (("A", tank_a, -X_TANK), ("B", tank_b, X_TANK)):
        if not present:
            continue
        ci = openmc.ZCylinder(x0=x0, r=R_TANK)
        co = openmc.ZCylinder(x0=x0, r=R_TANK + WALL)
        zi0, zi1 = openmc.ZPlane(z0=-H_TANK / 2), openmc.ZPlane(z0=H_TANK / 2)
        zo0, zo1 = openmc.ZPlane(z0=-H_TANK / 2 - WALL), openmc.ZPlane(z0=H_TANK / 2 + WALL)
        inner = -ci & +zi0 & -zi1
        outer = -co & +zo0 & -zo1
        sol = openmc.Cell(name=f"solution_{tag}", fill=mats[f"sol_{tag}"], region=inner)
        wall = openmc.Cell(name=f"wall_{tag}", fill=mats["al"], region=outer & ~inner)
        cells += [sol, wall]
        parts[f"sol_{tag}"], parts[f"wall_{tag}"] = sol, wall
        parts[f"inner_{tag}"] = [ci, zi0, zi1]
        water_region &= ~outer

    if absorber and fraction > 0:
        mat_name, thick = ABSORBERS[absorber]
        ly = R_TANK + WALL + ABS_MARGIN
        z_hi = H_TANK / 2 + WALL + ABS_MARGIN
        z_lo = z_hi - fraction * 2 * z_hi
        # the slab keeps its full width in both models: in the half model the
        # x < 0 half lies behind the mirror plane and is never visited, which
        # avoids putting a second surface on top of the reflective boundary
        # (coincident surfaces are what lose particles)
        slab = (+openmc.XPlane(x0=-thick / 2) & -openmc.XPlane(x0=thick / 2)
                & +openmc.YPlane(y0=-ly) & -openmc.YPlane(y0=ly)
                & +openmc.ZPlane(z0=z_lo) & -openmc.ZPlane(z0=z_hi))
        if mirror_plane is not None:
            # the reflective plane must bound every cell that touches it, not
            # just the water: a particle inside the absorber would otherwise
            # never see the mirror and would escape out of the far face
            slab = slab & +mirror_plane
        blade = openmc.Cell(name="absorber", fill=mats[mat_name], region=slab)
        cells.append(blade)
        parts["absorber"] = blade
        parts["absorber_material"] = mat_name
        water_region &= ~slab

    water = openmc.Cell(name="water", fill=mats["water"], region=water_region)
    cells.append(water)
    parts["water"] = water

    model = openmc.Model(geometry=openmc.Geometry(cells),
                         materials=openmc.Materials(list(mats.values())))
    model.settings.output = {"summary": False, "tallies": False}
    model.settings.temperature = {"method": "interpolation"}
    model.settings.seed = 229
    return model, parts


def add_tallies(model, parts, spectra=False):
    """The standard tally set: region tallies for whichever tanks exist,
    absorption by material, the global balance, and optionally the spectra
    in and into tank B."""
    import openmc
    tallies = []
    region_cells = [parts[k] for k in ("sol_A", "sol_B") if k in parts]
    t = openmc.Tally(name="regions")
    t.filters = [openmc.CellFilter(region_cells)]
    t.scores = ["flux", "fission", "nu-fission", "absorption",
                "inverse-velocity", "delayed-nu-fission"]
    tallies.append(t)

    mat_keys = [k for k in ("sol_A", "sol_B") if k in parts] + ["al", "water"]
    if "absorber_material" in parts:
        mat_keys.append(parts["absorber_material"])
    mat_list = [parts["mats"][k] for k in mat_keys]
    t = openmc.Tally(name="materials")
    t.filters = [openmc.MaterialFilter(mat_list)]
    t.scores = ["absorption"]
    tallies.append(t)

    t = openmc.Tally(name="global")
    t.scores = ["flux", "fission", "nu-fission", "absorption", "inverse-velocity"]
    tallies.append(t)

    if spectra and "sol_B" in parts:
        t = openmc.Tally(name="chi_B")
        t.filters = [openmc.CellFilter([parts["sol_B"]]),
                     openmc.EnergyoutFilter(ENERGY_EDGES)]
        t.scores = ["nu-fission"]
        t.estimator = "analog"
        tallies.append(t)
        t = openmc.Tally(name="flux_B")
        t.filters = [openmc.CellFilter([parts["sol_B"]]),
                     openmc.EnergyFilter(ENERGY_EDGES)]
        t.scores = ["flux"]
        tallies.append(t)
        t = openmc.Tally(name="into_B")
        t.filters = [openmc.SurfaceFilter(parts["inner_B"]),
                     openmc.CellFromFilter([parts["wall_B"]]),
                     openmc.CellFilter([parts["sol_B"]]),
                     openmc.EnergyFilter(ENERGY_EDGES)]
        t.scores = ["current"]
        tallies.append(t)
    model.tallies = openmc.Tallies(tallies)
    return [c.name for c in region_cells], [m.name for m in mat_list]


def point_source(x0, kind):
    import openmc
    if kind == "cf":
        energy = openmc.stats.Watt(*CF252_WATT)
    elif kind == "dt":
        energy = openmc.stats.Discrete([DT_ENERGY], [1.0])
    else:
        raise ValueError(kind)
    return openmc.IndependentSource(space=openmc.stats.Point((x0, 0.0, 0.0)),
                                    energy=energy)


# ---------------------------------------------------------------------------
# running and harvesting
# ---------------------------------------------------------------------------
def harvest(sp_path, region_names, mat_names, spectra=False):
    """Read a statepoint into plain floats: [mean, std] pairs everywhere."""
    import openmc
    out = {}
    with openmc.StatePoint(sp_path) as sp:
        if sp.run_mode == "eigenvalue":
            out["k"] = [float(sp.keff.n), float(sp.keff.s)]
            if sp.entropy is not None and len(sp.entropy):
                ent = np.asarray(sp.entropy, dtype=float).ravel()
                out["entropy"] = [round(float(x), 4) for x in ent]
        t = sp.get_tally(name="regions")
        out["regions"] = {}
        for i, name in enumerate(region_names):
            out["regions"][name[-1]] = {
                s: [float(t.mean[i, 0, j]), float(t.std_dev[i, 0, j])]
                for j, s in enumerate(t.scores)}
        t = sp.get_tally(name="materials")
        out["absorption_by_material"] = {
            name: [float(t.mean[i, 0, 0]), float(t.std_dev[i, 0, 0])]
            for i, name in enumerate(mat_names)}
        t = sp.get_tally(name="global")
        out["global"] = {s: [float(t.mean[0, 0, j]), float(t.std_dev[0, 0, j])]
                         for j, s in enumerate(t.scores)}
        if spectra:
            for name in ("chi_B", "flux_B", "into_B"):
                t = sp.get_tally(name=name)
                # into_B has one bin per bounding surface of the solution, each
                # signed by that surface's normal; the wall to solution direction
                # is fixed per surface, so the magnitudes add
                m = np.abs(t.mean.reshape(-1, len(ENERGY_EDGES) - 1)).sum(axis=0)
                s = np.sqrt((t.std_dev.reshape(-1, len(ENERGY_EDGES) - 1) ** 2).sum(axis=0))
                out[name] = {"mean": m.tolist(), "std": s.tolist()}
    return out


def run_model(model, workdir, exe):
    if os.path.isdir(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    t0 = time.time()
    sp = model.run(cwd=workdir, output=False, openmc_exec=exe)
    return sp, time.time() - t0


def mirror(site):
    """Reflect a fission site through the plane x = 0. Every configuration
    here is mirror symmetric in x (identical tanks at +/- X_TANK, the
    absorber slab centred on the plane), so this maps the geometry onto
    itself exactly."""
    import openmc
    return openmc.SourceParticle(
        r=(-site.r[0], site.r[1], site.r[2]),
        u=(-site.u[0], site.u[1], site.u[2]),
        E=site.E, time=site.time, wgt=site.wgt,
        delayed_group=site.delayed_group, surf_id=site.surf_id,
        particle=site.particle)


def source_from_half(workdir, out_a, out_b, out_all):
    """Take the fission bank of a half model run (every site has x > 0, in
    tank B) and build the three sources the fission matrix needs, in the
    full geometry: the bank itself for tank B, its mirror image for tank A,
    and both together for the control. This is the exact symmetric
    fundamental mode, so the control must return the transport k."""
    import openmc
    files = sorted(glob.glob(os.path.join(workdir, "source*.h5")))
    if not files:
        raise RuntimeError(f"no source file written in {workdir}")
    b = list(openmc.read_source_file(files[-1]))
    a = [mirror(s) for s in b]
    openmc.write_source_file(a, out_a)
    openmc.write_source_file(b, out_b)
    openmc.write_source_file(a + b, out_all)
    return len(a), len(b)


def split_source(workdir, out_a, out_b, out_all, out_rawall):
    """Turn the converged fission bank of a coupled eigenvalue run into the
    per tank sources the fission matrix needs.

    A pair of weakly coupled multiplying regions is the textbook loosely
    coupled system: the fundamental mode is symmetric, the second mode is
    the tilt between the tanks, and their eigenvalues differ by only
    2 k_cross, so the dominance ratio here is 0.95 to 0.99 and the tilt
    both decays and re randomises over of order a hundred generations.
    Fission bank sampling noise therefore drives a standing tilt of a few
    percent that no affordable number of batches averages away, and the
    Shannon entropy of the source is nearly blind to it because entropy is
    dominated by the shape inside each tank.

    The geometry, however, is exactly mirror symmetric, so the true
    fundamental mode has exactly half its fissions in each tank and the
    tilt is pure error. Symmetrising the bank (every site together with
    its mirror image) projects the antisymmetric component out exactly and
    doubles the statistics, which is the same reasoning that lets a
    symmetric core be modelled as a half core. The raw bank is written too,
    unmodified, so that the report can show what it costs to skip this.
    """
    import openmc
    files = sorted(glob.glob(os.path.join(workdir, "source*.h5")))
    if not files:
        raise RuntimeError(f"no source file written in {workdir}")
    sites = list(openmc.read_source_file(files[-1]))
    raw_a = [s for s in sites if s.r[0] < 0]
    raw_b = [s for s in sites if s.r[0] > 0]
    # every site in tank A, plus the mirror of every site in tank B
    sym_a = raw_a + [mirror(s) for s in raw_b]
    sym_b = [mirror(s) for s in sym_a]
    openmc.write_source_file(sym_a, out_a)
    openmc.write_source_file(sym_b, out_b)
    openmc.write_source_file(sym_a + sym_b, out_all)
    openmc.write_source_file(sites, out_rawall)
    return len(raw_a), len(raw_b)


def state_kwargs(state):
    if state == "open":
        return {}
    return {"absorber": state, "fraction": 1.0}


# ---------------------------------------------------------------------------
# the protocol
# ---------------------------------------------------------------------------
def protocol(args):
    import openmc
    budget = BUDGET["quick" if args.quick else "full"]
    exe = os.environ.get("OPENMC_EXEC", "openmc")
    work = args.workdir
    os.makedirs(work, exist_ok=True)
    results_path = os.path.join(HERE, "tallies.json")
    results = {"runs": {}}
    if os.path.exists(results_path) and args.only:
        results = json.load(open(results_path))
    runs = results["runs"]
    wanted = lambda name: (not args.only) or any(k in name for k in args.only.split(","))
    t_start = time.time()

    def record(name, model, parts, spectra=False, extra=None):
        region_names, mat_names = add_tallies(model, parts, spectra)
        sp, wall = run_model(model, os.path.join(work, name), exe)
        r = harvest(sp, region_names, mat_names, spectra)
        r["mode"] = model.settings.run_mode
        r["particles"] = int(model.settings.particles)
        r["batches"] = int(model.settings.batches)
        if model.settings.run_mode == "eigenvalue":
            r["inactive"] = int(model.settings.inactive)
        r["seconds"] = round(wall, 1)
        if extra:
            r.update(extra)
        runs[name] = r
        k = f"k = {r['k'][0]:.5f} +/- {r['k'][1]:.5f}" if "k" in r else "fixed source"
        print(f"  {name:26s} {k}   ({wall:.0f} s)", flush=True)
        json.dump(results, open(results_path, "w"), indent=1)
        return r

    def eigen_settings(model, sourcepoint=False, half=False):
        s = model.settings
        s.run_mode = "eigenvalue"
        s.particles, s.batches, s.inactive = budget["eig_p"], budget["eig_b"], budget["eig_i"]
        x_lo = 0.0 if half else -X_TANK - R_TANK
        s.source = openmc.IndependentSource(
            space=openmc.stats.Box((x_lo, -R_TANK, -H_TANK / 2),
                                   (X_TANK + R_TANK, R_TANK, H_TANK / 2)),
            constraints={"fissionable": True})
        mesh = openmc.RegularMesh()
        mesh.dimension = [12 if half else 24, 12, 10]
        mesh.lower_left = (x_lo, -R_TANK, -H_TANK / 2)
        mesh.upper_right = (X_TANK + R_TANK, R_TANK, H_TANK / 2)
        s.entropy_mesh = mesh
        if sourcepoint:
            s.sourcepoint = {"batches": [s.batches], "separate": True, "write": True}

    def fixed_settings(model, n, sources, multiply):
        s = model.settings
        s.run_mode = "fixed source"
        s.batches = 20
        s.particles = max(n // 20, 100)
        s.source = sources
        s.create_fission_neutrons = bool(multiply)

    print("neutron sector gate: OpenMC", openmc.__version__, "| budget",
          "quick" if args.quick else "full", flush=True)

    if args.resplit:
        for state in STATES:
            na, nb = split_source(os.path.join(work, f"coupled_{state}"),
                                  os.path.join(work, f"src_A_{state}.h5"),
                                  os.path.join(work, f"src_B_{state}.h5"),
                                  os.path.join(work, f"src_all_{state}.h5"),
                                  os.path.join(work, f"src_rawall_{state}.h5"))
            runs[f"coupled_{state}"]["bank_split"] = {"A": na, "B": nb}
            print(f"  resplit coupled_{state}: raw A {na}, raw B {nb} "
                  f"(tilt {nb/(na+nb)-0.5:+.3f}), symmetrised to {na+nb} each",
                  flush=True)
        json.dump(results, open(results_path, "w"), indent=1)

    # -- alone ----------------------------------------------------------------
    for tag in ("A", "B"):
        name = f"alone_{tag}"
        if wanted(name):
            model, parts = build(tank_a=(tag == "A"), tank_b=(tag == "B"))
            eigen_settings(model)
            record(name, model, parts)

    # -- coupled: open, the sheet at four insertions, the blade ---------------
    configs = [("coupled_open", {})]
    configs += [(f"coupled_cd{int(f*100):02d}", {"absorber": "cd", "fraction": f}) for f in (0.25, 0.5, 0.75)]
    configs += [("coupled_cd", {"absorber": "cd", "fraction": 1.0}),
                ("coupled_b4c", {"absorber": "b4c", "fraction": 1.0})]
    for name, kw in configs:
        if wanted(name):
            state = name.split("_", 1)[1]
            keep_bank = state in STATES
            model, parts = build(**kw)
            eigen_settings(model, sourcepoint=keep_bank)
            record(name, model, parts, extra={"absorber": kw.get("absorber"),
                                              "fraction": kw.get("fraction", 0.0)})
            if keep_bank:
                na, nb = split_source(os.path.join(work, name),
                                      os.path.join(work, f"src_A_{state}.h5"),
                                      os.path.join(work, f"src_B_{state}.h5"),
                                      os.path.join(work, f"src_all_{state}.h5"),
                                      os.path.join(work, f"src_rawall_{state}.h5"))
                runs[name]["bank_split"] = {"A": na, "B": nb}
                json.dump(results, open(results_path, "w"), indent=1)

    # -- the half model: the symmetric fundamental mode, by construction ------
    for state in STATES:
        name = f"half_{state}"
        if wanted(name):
            model, parts = build(half=True, **state_kwargs(state))
            eigen_settings(model, sourcepoint=True, half=True)
            record(name, model, parts, extra={"state": state, "half": True})
            na, nb = source_from_half(os.path.join(work, name),
                                      os.path.join(work, f"src_A_{state}.h5"),
                                      os.path.join(work, f"src_B_{state}.h5"),
                                      os.path.join(work, f"src_all_{state}.h5"))
            runs[name]["sites"] = nb
            json.dump(results, open(results_path, "w"), indent=1)

    # -- the fission matrix, and its two controls -----------------------------
    for state in STATES:
        for tag in ("all", "rawall", "A", "B"):
            name = f"coupling_{tag}_{state}"
            if wanted(name):
                src = os.path.join(work, f"src_{tag}_{state}.h5")
                if not os.path.exists(src):
                    raise RuntimeError(f"{src} missing: run half_{state} (or coupled_{state} "
                                       f"for the raw control) first")
                model, parts = build(**state_kwargs(state))
                fixed_settings(model, budget["coupling"], openmc.FileSource(src), multiply=False)
                record(name, model, parts, extra={"state": state, "born_in": tag})

    # -- first generation response to each driver -----------------------------
    for state in STATES:
        for drive in ("cfA", "cfB", "dtB"):
            name = f"firstgen_{drive}_{state}"
            if wanted(name):
                model, parts = build(**state_kwargs(state))
                srcs = [point_source(sgn * X_TANK, kind) for kind, sgn in DRIVES[drive]]
                fixed_settings(model, budget["firstgen"], srcs, multiply=False)
                record(name, model, parts, extra={"state": state, "drive": drive})

    # -- the gate -------------------------------------------------------------
    for state in STATES:
        for drive in ("cfA", "cfB", "cfAB", "dtB"):
            name = f"gate_{drive}_{state}"
            if wanted(name):
                model, parts = build(**state_kwargs(state))
                srcs = [point_source(sgn * X_TANK, kind) for kind, sgn in DRIVES[drive]]
                fixed_settings(model, budget["gate"], srcs, multiply=True)
                record(name, model, parts, spectra=True,
                       extra={"state": state, "drive": drive})

    # -- feedback: the veto, priced -------------------------------------------
    for name, kw in (("feedback_T350_fixed_density", dict(temperature=350.0, expand=False)),
                     ("feedback_T350_expanded", dict(temperature=350.0, expand=True))):
        if wanted(name):
            model, parts = build(**kw)
            eigen_settings(model)
            record(name, model, parts, extra=kw)

    results["provenance"] = {
        "openmc_version": openmc.__version__,
        "cross_sections": os.environ.get("OPENMC_CROSS_SECTIONS"),
        "library": "ENDF/B-VIII.0, official OpenMC HDF5 distribution (openmc.org)",
        "budget": "quick" if args.quick else "full",
        "budget_numbers": budget,
        "wall_clock_minutes": round((time.time() - t_start) / 60, 1),
        "model": {
            "R_tank_cm": R_TANK, "H_tank_cm": H_TANK, "wall_cm": WALL, "gap_cm": GAP,
            "absorbers": ABSORBERS, "absorber_margin_cm": ABS_MARGIN, "reflector_cm": REFL,
            "tank_axis_x_cm": X_TANK, "cf252_watt_a_eV_b_per_eV": CF252_WATT,
            "dt_energy_eV": DT_ENERGY, "solution_atoms_per_b_cm": SOLUTION,
            "water_density_ratio_350K": WATER_RHO[350.0] / WATER_RHO[294.0],
            "energy_edges_eV": ENERGY_EDGES.tolist(),
        },
    }
    json.dump(results, open(results_path, "w"), indent=1)
    print(f"wrote {results_path} ({(time.time() - t_start)/60:.0f} min)")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--quick", action="store_true", help="a tenth of the particles")
    p.add_argument("--only", default="", help="comma separated substrings of run names to (re)run")
    p.add_argument("--workdir", default=os.path.join(HERE, "work"),
                   help="scratch directory for OpenMC inputs and statepoints")
    p.add_argument("--resplit", action="store_true",
                   help="rebuild the per tank sources from fission banks already "
                        "in the workdir, without rerunning the eigenvalue stage")
    args = p.parse_args()
    ensure_data()
    protocol(args)


if __name__ == "__main__":
    main()
