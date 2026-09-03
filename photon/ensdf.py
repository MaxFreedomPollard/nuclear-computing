#!/usr/bin/env python3
# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""
Level schemes for every nuclide that carries an isomer: fetched once from
the IAEA Live Chart (ENSDF adopted levels and gammas), cached, and packed.

The photon sector keystone search needs, for each isomer bearing nuclide,
the adopted level scheme (energies, spins and parities, half lives) and
the adopted gamma transitions between those levels (energies, relative
intensities, conversion coefficients). The IAEA Live Chart of Nuclides
serves both as CSV from ENSDF:

    https://nds.iaea.org/relnsd/v1/data?fields=levels&nuclides=93mo
    https://nds.iaea.org/relnsd/v1/data?fields=gammas&nuclides=93mo

This script takes the isomer list from NUBASE2020 (already cached in
/gates/data by isomer_screen.py), selects every nuclide with at least one
isomer whose half life is at least T_MIN, fetches both tables for each,
and writes them packed into levels.json.gz, which census.py reads. The raw
CSVs are kept in photon/cache/ (ignored by git) so a rerun costs nothing;
the packed file is committed so that the census reproduces offline.

Run: python3 ensdf.py           (about ten minutes on first use)
"""
import csv
import gzip
import io
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "gates"))
from isomer_screen import parse_nubase  # noqa: E402

CACHE = os.path.join(HERE, "cache")
PACKED = os.path.join(HERE, "levels.json.gz")
LIVECHART = "https://nds.iaea.org/relnsd/v1/data?fields={field}&nuclides={nuclide}"
T_MIN = 1.0          # s: an isomer that holds a bit for a second (the README's own floor)

ELEMENTS = (
    "n H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn "
    "Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce "
    "Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn "
    "Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl "
    "Mc Lv Ts Og").split()


def symbol(Z):
    return ELEMENTS[Z]


def livechart_id(Z, A):
    return f"{A}{symbol(Z).lower()}"


def fetch(field, nuclide, retries=3):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{nuclide}_{field}.csv")
    if os.path.exists(path):
        return open(path, encoding="utf-8", errors="replace").read()
    url = LIVECHART.format(field=field, nuclide=nuclide)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                text = resp.read().decode("utf-8", errors="replace")
            break
        except Exception as e:                       # noqa: BLE001
            if attempt == retries - 1:
                raise
            time.sleep(2.0 * (attempt + 1))
    open(path, "w", encoding="utf-8").write(text)
    time.sleep(0.15)                                 # be polite to the service
    return text


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def unc(value_str, unc_str):
    """An energy's uncertainty in keV: the quoted one, or half the last
    quoted digit when ENSDF gives none, which is what a rounded number
    honestly knows."""
    u = num(unc_str)
    if u is not None and u > 0:
        return u
    v = (value_str or "").strip()
    if "." in v:
        return 0.5 * 10.0 ** (-len(v.split(".")[1]))
    return 0.5


def parse_levels(text):
    """Adopted levels: index, energy (keV), spin parity string, half life (s)
    with its operator ('' exact, '<' or '>' a limit), and the decay modes."""
    out = []
    rows = list(csv.DictReader(io.StringIO(text)))
    for r in rows:
        if r.get("energy_shift", "").strip():
            continue                                  # energy known only relative to an unknown offset
        E = num(r.get("energy"))
        if E is None:
            continue
        out.append({
            "i": int(r["idx"]),
            "E": E,
            "u": unc(r.get("energy"), r.get("unc_e")),
            "jp": (r.get("jp") or "").strip(),
            "t": num(r.get("half_life_sec")),
            "op": (r.get("operator_hl") or "").strip(),
            "dec": [(r.get(f"decay_{k}") or "").strip() for k in (1, 2, 3) if (r.get(f"decay_{k}") or "").strip()],
            "decp": [num(r.get(f"decay_{k}_%")) for k in (1, 2, 3) if (r.get(f"decay_{k}") or "").strip()],
        })
    return out


def parse_gammas(text):
    """Adopted gammas: start and end level indices, energy (keV), relative
    photon intensity, total conversion coefficient, multipolarity."""
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        try:
            a, b = int(r["start_level_idx"]), int(r["end_level_idx"])
        except (KeyError, ValueError):
            continue
        E = num(r.get("energy"))
        if E is None:
            continue
        out.append({
            "a": a, "b": b, "E": E,
            "u": unc(r.get("energy"), r.get("unc_en")),
            "I": num(r.get("relative_intensity")),
            "alpha": num(r.get("tot_conv_coeff")),
            "mult": (r.get("multipolarity") or "").strip(),
        })
    return out


def main():
    isomers = parse_nubase()
    keep = {}
    for r in isomers:
        if r["t_half_s"] >= T_MIN:
            keep.setdefault((r["Z"], r["A"]), []).append(r)
    print(f"NUBASE2020: {len(isomers)} isomers, {sum(len(v) for v in keep.values())} with "
          f"t1/2 >= {T_MIN} s in {len(keep)} nuclides", flush=True)
    packed, failed = {}, []
    t0 = time.time()
    for n, (Z, A) in enumerate(sorted(keep)):
        nid = livechart_id(Z, A)
        try:
            lv = parse_levels(fetch("levels", nid))
            gm = parse_gammas(fetch("gammas", nid))
        except Exception as e:                        # noqa: BLE001
            failed.append((nid, str(e)[:80]))
            continue
        if not lv:
            failed.append((nid, "no levels returned"))
            continue
        packed[nid] = {"Z": Z, "A": A, "levels": lv, "gammas": gm,
                       "isomers": [{"E": r["E_keV"], "t": r["t_half_s"] if r["t_half_s"] != float("inf") else None,
                                    "jp": r["Jpi"], "modes": r["decay_modes"]} for r in keep[(Z, A)]]}
        if (n + 1) % 25 == 0:
            print(f"  {n+1}/{len(keep)} nuclides, {time.time()-t0:.0f} s", flush=True)
    with gzip.open(PACKED, "wt", encoding="utf-8") as f:
        json.dump({"source": "IAEA Live Chart of Nuclides, ENSDF adopted levels and gammas",
                   "t_min_s": T_MIN, "nuclides": packed, "failed": failed}, f)
    nl = sum(len(v["levels"]) for v in packed.values())
    ng = sum(len(v["gammas"]) for v in packed.values())
    print(f"packed {len(packed)} nuclides, {nl} levels, {ng} gammas -> {PACKED} "
          f"({os.path.getsize(PACKED)/1e6:.1f} MB); {len(failed)} failed")
    for nid, why in failed[:20]:
        print("  failed:", nid, why)


if __name__ == "__main__":
    main()
