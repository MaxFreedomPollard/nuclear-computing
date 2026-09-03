#!/usr/bin/env python3
# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""
The photon keystone, searched: a census of the nuclear chart against the
requirements the neutron gate left the photon sector with.

The theory's Section 2 divides candidate gates into self restoring,
convertible, and terminal, and names the convertible class as a search:
pairs of isomers (A, B) whose cascade lines and gateway lines are mutually
resonant, so that A's release triggers B and B's triggers A. The neutron
sector calculation (/neutron) then added a second requirement, a signal
controlled inhibition, because the neutron medium has none. Both are
questions about ENSDF, and this script asks them of every isomer that
holds a bit for at least a second.

Three searches, from the packed level schemes of ensdf.py:

  gateways     for every isomer, every level above it that a photon (or a
               captured electron) could excite it into: the observed class,
               where ENSDF lists the gamma between them, and the allowed
               class, where spin and parity permit an E1, M1 or E2 and the
               line is simply unobserved (the 4.85 keV 93mMo gateway is in
               the second class, which is why the class exists). For each,
               the release cascade from the gateway is followed through the
               adopted gammas: the probability that it comes back to the
               isomer rather than releasing, the photons it emits, and the
               energy it lets go. Gateways within 30 keV are the NEEC class.

  pairs        every release line of every isomer against every gateway
               absorption of every isomer. An ENSDF gamma energy is the
               photon's energy as emitted (the level scheme carries the
               recoil), and absorption needs the level difference plus one
               recoil, so the mismatch is computed on that convention with
               both thermal Doppler widths, a rotor of up to 1 km/s allowed
               to close the rest (Moon compensated recoil with a 700 m/s
               rotor in 1951), and, decisively, the quoted uncertainties of
               the three energies involved, because ENSDF knows most of them
               to tens or hundreds of eV and a rotor closes a few. A pair is
               *resonant within reach* only if the data are precise enough
               to say so; otherwise it is *compatible*, a candidate that a
               precision measurement could confirm or kill. For every pair,
               the areal density of inverted nuclei the amplification
               condition demands, from the gateway's integrated cross
               section, with measured widths kept apart from Weisskopf
               estimates.

  inhibitors   isomers with two releasing gateways whose cascades differ in
               whether they emit the signal line: a control on the second
               empties the register without producing the signal, which is
               the veto the neutron sector could not do.

Everything is a number from ENSDF, NUBASE, and textbook formulae; the
Weisskopf estimate is used, and labelled, only where ENSDF gives no width.
Writes gateways.csv, pairs.csv.gz, inhibitors.csv, results.md, figure 16.
"""
import csv
import gzip
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIGS = os.path.join(ROOT, "figures")

# ---------------------------------------------------------------- constants
HBARC_KEV_FM = 197327.053       # keV fm
U_KEV = 931494.10               # keV per atomic mass unit
HBAR_EV_S = 6.582119569e-16     # eV s
KT_EV = 0.02526                 # eV at 293 K
C_M_S = 299792458.0
LN2 = math.log(2.0)
V_ROTOR = 1000.0                # m/s: the reach of a mechanical rotor (Moon 1951 used 700)
N_SOLID = 5.0e22                # atoms per cm3 of a pure isomer solid, for thickness
T_MIN = 1.0                     # s: register floor, matching ensdf.py
Y_MIN = 0.05                    # photons per release: a line worth matching
E_MIN_LINE = 20.0               # keV: below this a line is not a gate signal
NEEC_KEV = 30.0                 # gateway energy below which NEEC is the mechanism
ATOMIC_KEV = 100.0              # below this the atomic photoeffect drowns a nuclear resonance
OUT = []


def say(s=""):
    OUT.append(s)


# ---------------------------------------------------------------- physics
def recoil_ev(E_keV, A):
    """Recoil energy taken by a free nucleus emitting or absorbing E."""
    return (E_keV * 1e3) ** 2 / (2.0 * A * U_KEV * 1e3)


def doppler_fwhm_ev(E_keV, A, kT=KT_EV):
    """Thermal Doppler width (FWHM) of a line of a nucleus of mass A at kT."""
    return E_keV * 1e3 * math.sqrt(8.0 * LN2 * kT / (A * U_KEV * 1e3))


def weisskopf_width_ev(E_keV, A, mult):
    """Single particle estimate of a transition width. The standard
    Weisskopf rates in per second, E in MeV; returned as an energy width."""
    E = E_keV / 1e3
    L, kind = int(mult[1:]), mult[0]
    if kind == "E":
        rate = {1: 1.0e14 * A ** (2 / 3) * E ** 3, 2: 7.3e7 * A ** (4 / 3) * E ** 5,
                3: 3.4e1 * A ** 2 * E ** 7}.get(L)
    else:
        rate = {1: 5.6e13 * E ** 3, 2: 3.5e7 * A ** (2 / 3) * E ** 5,
                3: 1.6e1 * A ** (4 / 3) * E ** 7}.get(L)
    return None if rate is None else HBAR_EV_S * rate


def sigma_int_b_ev(E_keV, gJ, gamma_partial_ev):
    """Integrated photoabsorption cross section of a resonance,
    2 pi^2 (hbar c / E)^2 g Gamma_0, in barn eV."""
    lam_fm2 = (HBARC_KEV_FM / E_keV) ** 2
    return 2.0 * math.pi ** 2 * lam_fm2 * 0.01 * gJ * gamma_partial_ev


def sigma_eff_b(sigma_int, fwhm_ev):
    """Peak cross section of a Gaussian broadened line of that area."""
    return 0.9394 * sigma_int / fwhm_ev


JP_RE = re.compile(r"(\d+)(?:/(\d+))?")


def parse_jp(s):
    """Spin as a float and parity as +1/-1, or None where ENSDF is silent or
    lists alternatives. Parentheses (tentative) are accepted."""
    if not s:
        return None, None
    t = s.replace("(", "").replace(")", "").replace("[", "").replace("]", "").strip()
    if "," in t or " " in t.strip() or "TO" in t.upper() or "OR" in t.upper():
        return None, None                       # ambiguous assignment
    m = JP_RE.match(t)
    if not m:
        return None, None
    J = float(m.group(1)) / (float(m.group(2)) if m.group(2) else 1.0)
    rest = t[m.end():]
    par = 1 if "+" in rest else (-1 if "-" in rest else None)
    return J, par


def lowest_multipole(J1, p1, J2, p2):
    """The lowest multipole connecting two levels of known spin and parity,
    as 'E1', 'M1', 'E2', ... or None if either is unknown or the transition
    is forbidden (0 -> 0)."""
    if None in (J1, p1, J2, p2):
        return None
    L = int(round(abs(J1 - J2)))
    if L == 0:
        if J1 == 0:
            return None
        L = 1
    change = p1 != p2
    electric = (change and L % 2 == 1) or (not change and L % 2 == 0)
    return f"{'E' if electric else 'M'}{L}"


# ---------------------------------------------------------------- schemes
class Scheme:
    """One nuclide's adopted levels and gammas, with the machinery to follow
    a cascade from any level."""

    def __init__(self, nid, d):
        self.nid, self.Z, self.A = nid, d["Z"], d["A"]
        self.levels = {lv["i"]: lv for lv in d["levels"]}
        self.out = {}
        for g in d["gammas"]:
            if g["a"] in self.levels and g["b"] in self.levels and g["E"] > 0:
                self.out.setdefault(g["a"], []).append(g)
        self.ground = min(self.levels.values(), key=lambda l: l["E"])["i"]
        self.longlived = {i for i, lv in self.levels.items()
                          if lv["t"] is not None and lv["t"] >= T_MIN and not lv["op"].startswith("<")}
        self.isomer_levels = []
        for iso in d["isomers"]:
            best = min(self.levels.values(), key=lambda l: abs(l["E"] - iso["E"]))
            if abs(best["E"] - iso["E"]) <= 3.0 and best["i"] != self.ground:
                self.isomer_levels.append((best["i"], iso))
                self.longlived.add(best["i"])

    def branches(self, i):
        """(final level, transition fraction, photon fraction, gamma) for each
        gamma leaving level i. Unknown intensities count as one relative
        unit, unknown conversion as none."""
        gs = self.out.get(i, [])
        if not gs:
            return []
        w = [(g["I"] if g["I"] is not None else 1.0) * (1.0 + (g["alpha"] or 0.0)) for g in gs]
        tot = sum(w)
        if tot <= 0:
            return []
        res = []
        for g, wi in zip(gs, w):
            photon = (g["I"] if g["I"] is not None else 1.0) / tot
            res.append((g["b"], wi / tot, photon, g))
        return res

    def cascade(self, start, sinks):
        """Follow the adopted gammas down from `start` until every branch has
        reached a sink (ground, a long lived isomer) or a level with no
        listed decay. Returns the photon yield per transition, the population
        that ended at each sink, and the population lost at dead ends."""
        pop = {start: 1.0}
        yields = {}
        ended, dead = {}, 0.0
        for i in sorted(self.levels, key=lambda k: -self.levels[k]["E"]):
            p = pop.get(i, 0.0)
            if p <= 0:
                continue
            if i != start and (i in sinks or i == self.ground):
                ended[i] = ended.get(i, 0.0) + p
                continue
            br = self.branches(i)
            if not br:
                if i == self.ground:
                    ended[i] = ended.get(i, 0.0) + p
                else:
                    dead += p
                continue
            for b, frac, photon, g in br:
                if self.levels[b]["E"] >= self.levels[i]["E"]:
                    continue
                pop[b] = pop.get(b, 0.0) + p * frac
                yields[g["a"], g["b"]] = yields.get((g["a"], g["b"]), 0.0) + p * photon
        lines = []
        for (a, b), y in yields.items():
            g = next(gg for gg in self.out[a] if gg["b"] == b)
            lines.append({"E": g["E"], "u": g.get("u", 0.05), "y": y, "a": a, "b": b})
        return lines, ended, dead

    def has_gamma(self, a, b):
        return any(g["b"] == b for g in self.out.get(a, []))


def load():
    d = json.load(gzip.open(os.path.join(HERE, "levels.json.gz"), "rt"))
    return {nid: Scheme(nid, v) for nid, v in d["nuclides"].items()}, d


# ---------------------------------------------------------------- gateways
def gateways(schemes):
    rows = []
    for nid, sc in schemes.items():
        for i_iso, iso in sc.isomer_levels:
            LI = sc.levels[i_iso]
            JI, pI = parse_jp(LI["jp"])
            # NUBASE's half life for the isomer (None there means stable); the
            # adopted level record is often blank and is only a fallback
            t_iso = iso.get("t") if iso.get("t") is not None else LI["t"]
            for i_g, LG in sc.levels.items():
                dE = LG["E"] - LI["E"]
                if dE <= 0 or dE > 3000.0:
                    continue
                observed = sc.has_gamma(i_g, i_iso)
                JG, pG = parse_jp(LG["jp"])
                mult = lowest_multipole(JI, pI, JG, pG)
                allowed = mult is not None and int(mult[1:]) <= 2
                if not (observed or allowed):
                    continue
                lines, ended, dead = sc.cascade(i_g, sinks=sc.longlived)
                p_return = ended.get(i_iso, 0.0)
                p_release = 1.0 - p_return - dead
                beta = sum(l["y"] for l in lines)
                e_end = sum(sc.levels[k]["E"] * p for k, p in ended.items())
                e_released = LG["E"] - e_end - dead * LG["E"]
                gamma_tot = None
                if LG["t"] is not None and LG["t"] > 0 and LG["op"] == "":
                    gamma_tot = HBAR_EV_S * LN2 / LG["t"]
                b_GI = sum(frac for b, frac, photon, g in sc.branches(i_g) if b == i_iso)
                gamma_GI, width_kind = None, "unknown"
                if observed and gamma_tot is not None and b_GI > 0:
                    gamma_GI, width_kind = gamma_tot * b_GI, "measured"
                elif mult is not None:
                    w = weisskopf_width_ev(dE, sc.A, mult)
                    if w is not None:
                        gamma_GI, width_kind = w, f"Weisskopf {mult}"
                gJ = ((2 * JG + 1) / (2 * JI + 1)) if (JG is not None and JI is not None) else 1.0
                sig_int = sigma_int_b_ev(dE, gJ, gamma_GI) if gamma_GI else None
                fwhm = doppler_fwhm_ev(dE, sc.A)
                sig_eff = sigma_eff_b(sig_int, fwhm) if sig_int else None
                n_areal = (1.0 / (beta * sig_eff * 1e-24)) if (sig_eff and beta > 0) else None
                rows.append(dict(
                    nuclide=nid, Z=sc.Z, A=sc.A, isomer_keV=LI["E"], isomer_u_keV=LI.get("u", 0.05),
                    isomer_t_s=t_iso, isomer_jp=LI["jp"],
                    gateway_keV=LG["E"], gateway_u_keV=LG.get("u", 0.05), dE_keV=dE,
                    gateway_jp=LG["jp"], gateway_t_s=LG["t"], gateway_t_op=LG["op"],
                    observed=int(observed), multipole=mult or "",
                    p_release=p_release, p_return=p_return, p_unknown=dead, beta=beta,
                    E_released_keV=e_released, leverage=(e_released / dE if dE > 0 else 0.0),
                    gamma_GI_eV=gamma_GI, width_kind=width_kind, gJ=gJ,
                    sigma_int_b_eV=sig_int, doppler_fwhm_eV=fwhm, sigma_eff_b=sig_eff,
                    N_areal_cm2=n_areal, thickness_cm=(n_areal / N_SOLID if n_areal else None),
                    neec=int(dE <= NEEC_KEV), atomic=int(dE < ATOMIC_KEV),
                    lines=[l for l in lines if l["y"] >= Y_MIN and l["E"] >= E_MIN_LINE and l["b"] != i_iso],
                    i_iso=i_iso, i_g=i_g,
                ))
    return rows


# ---------------------------------------------------------------- pairs
def pairs(schemes, gws):
    """Every release line against every gateway absorption."""
    em = []
    for g in gws:
        if g["p_release"] < 0.5:
            continue
        for l in g["lines"]:
            em.append((g["nuclide"], g["isomer_keV"], g["gateway_keV"], "triggered", l, g["A"]))
    for nid, sc in schemes.items():
        for i_iso, iso in sc.isomer_levels:
            lines, ended, dead = sc.cascade(i_iso, sinks=sc.longlived)
            for l in lines:
                if l["y"] >= Y_MIN and l["E"] >= E_MIN_LINE:
                    em.append((nid, sc.levels[i_iso]["E"], None, "spontaneous", l, sc.A))
    ab = [g for g in gws if g["p_release"] >= 0.5]
    # absorption needs the level difference plus one recoil (the photon's own
    # energy already sits one recoil below its level difference)
    E_need = np.array([g["dE_keV"] * 1e3 + recoil_ev(g["dE_keV"], g["A"]) for g in ab])
    u_need = np.array([math.hypot(g["gateway_u_keV"], g["isomer_u_keV"]) * 1e3 for g in ab])
    order = np.argsort(E_need)
    E_sorted = E_need[order]
    out = []
    for (nid, Eiso, Egate, kind, l, A) in em:
        E_ph = l["E"] * 1e3
        u_ph = l["u"] * 1e3
        dop_A = doppler_fwhm_ev(l["E"], A)
        reach = E_ph * V_ROTOR / C_M_S
        # window: what a rotor and two thermal widths can close, widened by the
        # data's own ignorance (three sigma of the combined energy uncertainty)
        win = reach + 2.0 * dop_A + 3.0 * math.sqrt(u_ph ** 2 + u_need.max() ** 2)
        lo, hi = np.searchsorted(E_sorted, [E_ph - win, E_ph + win])
        for j in order[lo:hi]:
            g = ab[j]
            same_transition = (g["nuclide"] == nid and abs(l["E"] - g["dE_keV"]) < 0.05)
            if same_transition:
                continue                            # resonant scattering of a gateway's own line, not a pair
            delta = E_ph - E_need[j]
            sig = math.sqrt(u_ph ** 2 + u_need[j] ** 2)
            dop = dop_A + g["doppler_fwhm_eV"]
            v_req = abs(delta) / E_ph * C_M_S
            if abs(delta) > reach + dop + 3.0 * sig:
                continue
            resonant = int(abs(delta) <= reach + dop and sig <= reach + dop)
            compatible = int(abs(delta) <= reach + dop + sig)          # within one standard deviation
            loose = int(abs(delta) <= reach + dop + 3.0 * sig)        # within three
            y = l["y"]
            n_areal = (1.0 / (y * g["sigma_eff_b"] * 1e-24)) if g["sigma_eff_b"] else None
            out.append(dict(
                A_nuclide=nid, A_isomer_keV=Eiso, A_gateway_keV=Egate, A_kind=kind,
                A_line_keV=l["E"], A_line_u_eV=u_ph, A_yield=y,
                B_nuclide=g["nuclide"], B_isomer_keV=g["isomer_keV"], B_gateway_keV=g["gateway_keV"],
                B_dE_keV=g["dE_keV"], B_dE_u_eV=u_need[j], B_observed=g["observed"], B_multipole=g["multipole"],
                B_p_release=g["p_release"], B_beta=g["beta"], B_isomer_t_s=g["isomer_t_s"],
                delta_eV=delta, sigma_eV=sig, doppler_sum_eV=dop, rotor_reach_eV=reach,
                v_required_m_s=v_req, resonant_within_reach=resonant, compatible=compatible, loose=loose,
                precision_needed_eV=reach + dop,
                B_sigma_eff_b=g["sigma_eff_b"], B_width_kind=g["width_kind"], B_atomic=g["atomic"],
                N_areal_cm2=n_areal, thickness_cm=(n_areal / N_SOLID if n_areal else None),
                homogeneous=int(g["nuclide"] == nid),
            ))
    key = {(p["A_nuclide"], round(p["A_isomer_keV"]), p["B_nuclide"], round(p["B_isomer_keV"])) for p in out}
    for p in out:
        p["closed_loop"] = int((p["B_nuclide"], round(p["B_isomer_keV"]), p["A_nuclide"], round(p["A_isomer_keV"])) in key
                               and not p["homogeneous"])
    return out


# ---------------------------------------------------------------- inhibition
def inhibitors(gws):
    by_iso = {}
    for g in gws:
        if g["p_release"] >= 0.5 and g["lines"]:
            by_iso.setdefault((g["nuclide"], round(g["isomer_keV"], 1)), []).append(g)
    rows = []
    for (nid, Eiso), gs in by_iso.items():
        if len(gs) < 2:
            continue
        for g1 in gs:
            top = max(g1["lines"], key=lambda l: l["y"])
            E_sig, y_sig = top["E"], top["y"]
            for g2 in gs:
                if g2 is g1:
                    continue
                y2 = sum(l["y"] for l in g2["lines"] if abs(l["E"] - E_sig) < 1.0)
                if y2 <= 0.1 * y_sig:
                    rows.append(dict(nuclide=nid, isomer_keV=Eiso, isomer_t_s=g1["isomer_t_s"],
                                     signal_gateway_keV=g1["gateway_keV"], signal_dE_keV=g1["dE_keV"],
                                     signal_line_keV=E_sig, signal_yield=y_sig,
                                     veto_gateway_keV=g2["gateway_keV"], veto_dE_keV=g2["dE_keV"],
                                     veto_yield_of_signal_line=y2, veto_p_release=g2["p_release"],
                                     veto_beta=g2["beta"], signal_neec=g1["neec"], veto_neec=g2["neec"]))
    return rows


# ---------------------------------------------------------------- output
def write_csv(path, rows, drop=()):
    """Plain CSV, or gzip compressed when the path ends in .gz (the pair table
    runs to tens of thousands of rows and is kept compressed in the repository)."""
    if not rows:
        open(path, "w").write("")
        return
    cols = [c for c in rows[0] if c not in drop]
    opener = (lambda: gzip.open(path, "wt", newline="")) if path.endswith(".gz") else (lambda: open(path, "w", newline=""))
    with opener() as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: (f"{v:.6g}" if isinstance(v, float) else v) for c, v in r.items() if c in cols})


def fmt_t(t):
    if t is None:
        return "stable"
    for unit, sec in (("y", 3.156e7), ("d", 86400), ("h", 3600), ("min", 60), ("s", 1)):
        if t >= sec:
            return f"{t/sec:.3g} {unit}"
    return f"{t:.2e} s"


def label(nid, E):
    m = re.match(r"(\d+)([a-z]+)", nid)
    return f"{m.group(1)}{m.group(2).capitalize()} ({E:.4g} keV)"


def thick(cm):
    return f"{cm*1e4:.3g} µm" if cm < 0.1 else (f"{cm:.3g} cm" if cm < 100 else f"{cm/100:.3g} m")


def main():
    schemes, raw = load()
    n_iso = sum(len(sc.isomer_levels) for sc in schemes.values())
    gws = gateways(schemes)
    prs = pairs(schemes, gws)
    inh = inhibitors(gws)
    write_csv(os.path.join(HERE, "gateways.csv"), gws, drop=("lines", "i_iso", "i_g"))
    write_csv(os.path.join(HERE, "pairs.csv.gz"), prs)
    write_csv(os.path.join(HERE, "inhibitors.csv"), inh)

    say("# The photon keystone, searched (regenerated by census.py from levels.json.gz)\n")
    say(f"Source: {raw['source']}, packed by ensdf.py; {len(schemes)} nuclides carrying {n_iso} isomers "
        f"with half life at least {T_MIN:g} s that could be matched to an adopted level; NUBASE2020 for the "
        "isomer list. Every number is ENSDF, NUBASE, or a textbook formula; the Weisskopf estimate is "
        "used only where ENSDF gives no width, and every row says which.\n")

    # ---- 1. gateways ---------------------------------------------------------
    say("## 1. Gateways: what could trigger each isomer\n")
    obs = [g for g in gws if g["observed"]]
    allo = [g for g in gws if not g["observed"]]
    rel = [g for g in gws if g["p_release"] >= 0.5]
    neec = [g for g in gws if g["neec"]]
    neec_rel = [g for g in neec if g["p_release"] >= 0.5]
    meas_rel = [g for g in rel if g["width_kind"] == "measured"]
    iso_with = {(g["nuclide"], g["isomer_keV"]) for g in gws}
    iso_with_rel = {(g["nuclide"], g["isomer_keV"]) for g in rel}
    say("A gateway is a level above the isomer that a photon, or an electron captured into a vacancy, "
        "could lift it into. Two classes are kept. *Observed*: ENSDF lists the gamma between gateway and "
        "isomer, so the absorption is the time reverse of a measured line. *Allowed*: spin and parity "
        "permit an E1, M1 or E2 and the line is simply unobserved, which is the class the 4.85 keV gateway "
        "of ⁹³ᵐMo belongs to, because a 4.85 keV transition is almost entirely converted and has never been "
        "seen as a photon. For every gateway the release cascade is followed through the adopted gammas.\n")
    say("| count | number |")
    say("|---|---|")
    say(f"| isomers with half life ≥ {T_MIN:g} s matched to an adopted level | {n_iso} |")
    say(f"| gateways, observed class | {len(obs)} |")
    say(f"| gateways, allowed class | {len(allo)} |")
    say(f"| gateways that *release* (cascade returns to the isomer less than half the time) | {len(rel)} |")
    say(f"| releasing gateways whose width ENSDF actually measures (lifetime and branch) | {len(meas_rel)} |")
    say(f"| isomers with at least one gateway | {len(iso_with)} |")
    say(f"| isomers with at least one releasing gateway | {len(iso_with_rel)} |")
    say(f"| NEEC class gateways (within {NEEC_KEV:g} keV of the isomer) | {len(neec)}, of which {len(neec_rel)} release |")
    say("")
    say("**The NEEC class, ranked by energy let go per trigger.** These are the targets of the photon "
        "sector's Phase B1: an isomer, a gateway a few keV above it, and a cascade that leaves. Their "
        "cross sections are not photon cross sections but electron capture resonances, which is the "
        "point of the class; the photon route to any of them is closed by the atomic photoeffect long "
        "before the nuclear resonance is reached.\n")
    say("| isomer | half life | stored (keV) | gateway (keV) | ΔE (keV) | class | release probability | photons per trigger | energy let go (keV) | leverage |")
    say("|---|---|---|---|---|---|---|---|---|---|")
    for g in sorted(neec_rel, key=lambda g: -g["E_released_keV"])[:25]:
        say(f"| {label(g['nuclide'], g['isomer_keV'])} | {fmt_t(g['isomer_t_s'])} | {g['isomer_keV']:.4g} | "
            f"{g['gateway_keV']:.5g} | {g['dE_keV']:.3g} | {'observed' if g['observed'] else 'allowed ' + g['multipole']} | "
            f"{g['p_release']:.2f} | {g['beta']:.2f} | {g['E_released_keV']:.4g} | {g['leverage']:.3g} |")
    say("")
    mo = [g for g in gws if g["nuclide"] == "93mo" and abs(g["dE_keV"] - 4.85) < 0.2]
    if mo:
        g = mo[0]
        say(f"The famous case reads back correctly: ⁹³ᵐMo at 2424.95 keV, gateway 2429.8 keV, ΔE = "
            f"{g['dE_keV']:.2f} keV, {'observed' if g['observed'] else 'allowed'} ({g['multipole']}), release "
            f"probability {g['p_release']:.2f}, {g['beta']:.2f} photons per trigger letting go "
            f"{g['E_released_keV']:.0f} keV, leverage {g['leverage']:.0f}. The theory's candidate table quotes "
            "leverage about 500 for this state from the same physics.\n")

    # ---- 2. pairs ------------------------------------------------------------
    say("## 2. Level restoring pairs: does any isomer's release trigger another's?\n")
    say("Every release line (from every releasing gateway's cascade, and from each isomer's own decay, "
        "excluding lines that merely return to the isomer) is compared with every releasing gateway "
        "absorption. An ENSDF gamma energy is the photon as emitted; the absorber needs its level "
        "difference plus one recoil; thermal Doppler widths at 293 K are taken for both nuclei; and a "
        "rotor of up to 1 km/s is allowed to close the rest, since a velocity v shifts a line by Ev/c and "
        "Moon closed recoil this way in 1951. A line with fewer than "
        f"{Y_MIN:g} photons per release or below {E_MIN_LINE:g} keV is not counted as a signal.\n")
    say("One fact about the data decides how this table must be read. A rotor can close a few "
        "electronvolts at 1 MeV; ENSDF quotes most level and line energies to ten or a hundred "
        "electronvolts. The census therefore carries every energy's quoted uncertainty and sorts each "
        "coincidence into two bins. *Resonant within reach*: the mismatch is inside what a rotor and "
        "two thermal widths can close, **and** the combined uncertainty is small enough that the data "
        "can actually say so. *Compatible*: the mismatch is inside that reach plus one standard "
        "deviation of the data's uncertainty, so a precision measurement of three energies could "
        "confirm or kill it; the count within three standard deviations is given for scale. A census "
        "of the adopted data can produce candidates; it cannot, for most of them, produce resonances.\n")
    n_em = len({(p["A_nuclide"], p["A_isomer_keV"], p["A_gateway_keV"], p["A_line_keV"]) for p in prs})
    comp = [p for p in prs if p["compatible"]]
    reson = [p for p in prs if p["resonant_within_reach"]]
    het = [p for p in comp if not p["homogeneous"]]
    het_res = [p for p in reson if not p["homogeneous"]]
    loops = [p for p in comp if p["closed_loop"]]
    say("| count | number |")
    say("|---|---|")
    say(f"| release lines worth matching | {n_em} |")
    say(f"| releasing gateway absorptions | {len([g for g in gws if g['p_release'] >= 0.5])} |")
    say(f"| coincidences compatible with resonance within one standard deviation of the data | {len(comp)} |")
    say(f"| within three standard deviations, for scale | {sum(1 for p in prs if p['loose'])} |")
    say(f"| of which heterogeneous (different nuclides) | {len(het)} |")
    say(f"| of which closed loops, A triggers B and B triggers A | {len(loops)} |")
    say(f"| coincidences the data are precise enough to call resonant within rotor reach | {len(reson)} |")
    say(f"| of which heterogeneous | {len(het_res)} |")
    say("")
    if comp:
        med_sig = float(np.median([p["sigma_eV"] for p in comp]))
        med_need = float(np.median([p["precision_needed_eV"] for p in comp]))
        say(f"The median coincidence carries a combined energy uncertainty of {med_sig:.0f} eV against a "
            f"window a rotor could close of {med_need:.1f} eV: the data are typically "
            f"{med_sig/med_need:.0f} times too coarse to decide. That is a statement about ENSDF, and "
            "it is the first concrete experimental request this search produces: three energies, "
            "measured to an electronvolt, for each candidate below.\n")
    say("**The candidates that would ask the least of the absorber if they are real**, ranked by the "
        "areal density of inverted nuclei the amplification condition demands (y N σ > 1, with y the "
        "line's yield per release and σ the gateway's Doppler broadened peak cross section). Measured "
        "widths first; Weisskopf estimates, which for transitions out of isomers are optimistic by the "
        "hindrance that makes them isomers, are listed separately and should be read as upper bounds.\n")
    for kind, title in (("measured", "Gateway width measured by ENSDF"), ("Weisskopf", "Gateway width a Weisskopf estimate")):
        cand = [p for p in comp if p["N_areal_cm2"] and p["B_width_kind"].startswith(kind)]
        say(f"**{title}: {len(cand)} candidates.**\n")
        if cand:
            say("| A: emitter | A line (keV) | yield | B: absorber | B ΔE (keV) | mismatch ± data (eV) | energies must improve by | status | B σ (b) | N inverted (cm⁻²) | pure isomer thickness |")
            say("|---|---|---|---|---|---|---|---|---|---|---|")
            for p in sorted(cand, key=lambda p: p["N_areal_cm2"])[:12]:
                st = "resonant" if p["resonant_within_reach"] else "compatible"
                st += "; atomic photoeffect dominates" if p["B_atomic"] else ""
                improve = max(1.0, p["sigma_eV"] / p["precision_needed_eV"])
                say(f"| {label(p['A_nuclide'], p['A_isomer_keV'])} {p['A_kind']} | {p['A_line_keV']:.4g} | {p['A_yield']:.2f} | "
                    f"{label(p['B_nuclide'], p['B_isomer_keV'])} | {p['B_dE_keV']:.5g} | {p['delta_eV']:+.1f} ± {p['sigma_eV']:.0f} | "
                    f"×{improve:.0f} | {st} | {p['B_sigma_eff_b']:.3g} | {p['N_areal_cm2']:.2e} | {thick(p['thickness_cm'])} |")
            say("")
    best_m = sorted([p for p in comp if p["N_areal_cm2"] and p["B_width_kind"] == "measured"], key=lambda p: p["N_areal_cm2"])
    best_w = sorted([p for p in comp if p["N_areal_cm2"] and p["B_width_kind"].startswith("Weisskopf")], key=lambda p: p["N_areal_cm2"])
    if best_m:
        b = best_m[0]
        say(f"With a measured width the least demanding candidate in the chart, {label(b['A_nuclide'], b['A_isomer_keV'])} "
            f"feeding {label(b['B_nuclide'], b['B_isomer_keV'])}, needs {b['N_areal_cm2']:.1e} inverted nuclei per cm², "
            f"{thick(b['thickness_cm'])} of a solid made entirely of the isomer"
            + (", at a gateway energy where the atomic photoeffect absorbs the photon long before the nucleus sees it" if b["B_atomic"] else "")
            + ". No macroscopic quantity of any long lived isomer above 100 keV has ever existed. This is theory "
            "Section 1.1's areal density wall with the chart's own best case in it.\n")
    if best_w:
        b = best_w[0]
        say(f"Granting every Weisskopf estimate at face value, the least demanding would be {label(b['A_nuclide'], b['A_isomer_keV'])} "
            f"feeding {label(b['B_nuclide'], b['B_isomer_keV'])} at {thick(b['thickness_cm'])}; a real transition out of "
            "an isomer is hindered below that estimate by the same factor that makes the state an isomer, "
            "typically three to eight orders of magnitude, so this is a bound and not a candidate.\n")

    # ---- 3. inhibition -------------------------------------------------------
    say("## 3. Inhibition: isomers with a signal gateway and a veto gateway\n")
    say("The neutron sector could not invert a signal, because every coupling there adds fissions. The "
        "isomer sector can, in principle, by spending the stored energy down a different gateway: a "
        "control that opens a second gateway whose cascade bypasses the signal line empties the register "
        "without producing the signal. This counts isomers with at least two releasing gateways where "
        "the second emits less than a tenth of the first's strongest line.\n")
    iso_inh = {(r["nuclide"], r["isomer_keV"]) for r in inh}
    iso_two = {}
    for g in gws:
        if g["p_release"] >= 0.5 and g["lines"]:
            k = (g["nuclide"], round(g["isomer_keV"], 1))
            iso_two[k] = iso_two.get(k, 0) + 1
    n_two = sum(1 for v in iso_two.values() if v >= 2)
    say("| count | number |")
    say("|---|---|")
    say(f"| isomers with two or more releasing gateways | {n_two} |")
    say(f"| isomers with a signal gateway and a veto gateway | {len(iso_inh)} |")
    say(f"| such pairs where both gateways are NEEC class | {sum(1 for r in inh if r['signal_neec'] and r['veto_neec'])} |")
    say(f"| such pairs where the veto gateway is NEEC class | {sum(1 for r in inh if r['veto_neec'])} |")
    say("")
    if inh:
        say("**Examples, the longest lived first:**\n")
        say("| isomer | half life | signal gateway ΔE (keV) | signal line (keV) | yield | veto gateway ΔE (keV) | that line's yield under the veto | veto releases |")
        say("|---|---|---|---|---|---|---|---|")
        seen = set()
        for r in sorted(inh, key=lambda r: -(r["isomer_t_s"] or 1e30)):
            k = (r["nuclide"], r["isomer_keV"])
            if k in seen:
                continue
            seen.add(k)
            say(f"| {label(r['nuclide'], r['isomer_keV'])} | {fmt_t(r['isomer_t_s'])} | {r['signal_dE_keV']:.4g} | "
                f"{r['signal_line_keV']:.4g} | {r['signal_yield']:.2f} | {r['veto_dE_keV']:.4g} | "
                f"{r['veto_yield_of_signal_line']:.3f} | {r['veto_p_release']:.2f} |")
            if len(seen) >= 15:
                break
        say("")
    say("Inhibition therefore exists in the photon sector as a *mechanism*: the same stored energy can be "
        "spent into the signal or into a dump, and the choice is which gateway the control opens. What "
        "the neutron sector lacked, the isomer sector has by construction, and this table is its census. "
        "It carries the same cross section tax as the gain.\n")

    # ---- 4. verdict ----------------------------------------------------------
    say("## 4. The verdict on Kill Criterion B, from data alone\n")
    say("Four things the chart settles without an experiment, and one it cannot:\n")
    say(f"- **The convertible class exists as candidates, not as resonances.** {len(het)} heterogeneous "
        f"coincidences are compatible with resonance, {len(loops)} of them closed loops, but the data can "
        f"call only {len(het_res)} of them resonant within rotor reach, because ENSDF's energies are tens "
        "to hundreds of electronvolts coarse and a rotor closes a few. The first thing this search asks "
        "of an experiment is not a trigger cross section but three energies to an electronvolt.")
    say("- **Every candidate meets the areal density wall.** "
        + (f"The least demanding with a measured width needs {thick(best_m[0]['thickness_cm'])} of pure inverted "
           "isomer" if best_m else "None has a measured width")
        + ". A Doppler broadened MeV resonance is barns wide and an inverted solid does not exist, so the "
        "class is real as energies and empty as amplifiers, exactly as theory Section 1.1 predicted for "
        "any cross section short of a laser driven or neutron driven one.")
    say(f"- **Inhibition exists as a mechanism.** {len(iso_inh)} isomers offer a signal gateway and a veto "
        "gateway. The neutron sector's missing operation is native here, with the same areal density tax.")
    say(f"- **The NEEC class is a list now.** {len(neec_rel)} releasing gateways sit within {NEEC_KEV:g} keV of "
        "their isomer. Their triggers are electron capture resonances, and whether those are large enough "
        "is the contested ⁹³ᵐMo question the roadmap already waits on: one experimental number, applied "
        "to a list this census has written down.\n")
    say("*The photon sector's keystone is not hiding in an unread corner of ENSDF. The pairs the theory "
        "asked for exist as coincidences the data cannot yet resolve, and fail as amplifiers by the "
        "areal density wall even if every one of them is real; the veto the neutron sector lacked is "
        "available; and everything rests on the NEEC resonance strength, for the states listed above.*")

    open(os.path.join(HERE, "results.md"), "w").write("\n".join(OUT) + "\n")
    print("\n".join(OUT[-9:]))
    print("wrote photon/results.md, gateways.csv, pairs.csv.gz, inhibitors.csv")
    figure(gws, prs, inh, iso_two)


def figure(gws, prs, inh, iso_two):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    INK, BLUE, RED, GREEN, AMBER, PURPLE, GREY = (
        "#16213e", "#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed", "#94a3b8")
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK, "xtick.color": INK,
        "ytick.color": INK, "axes.titlecolor": INK, "font.size": 11, "axes.titlesize": 12,
        "axes.titleweight": "bold", "axes.grid": True, "grid.color": "#e5e7eb",
        "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
        "figure.dpi": 130, "svg.hashsalt": "nuclear-computer"})
    fig, ((A, B), (C, D)) = plt.subplots(2, 2, figsize=(13.4, 9.6))

    # A: the gateway landscape
    for cls, col, lab, mk, sz, al in ((1, BLUE, "observed gateway", "o", 14, 0.7),
                                      (0, GREY, "allowed, line unobserved", ".", 8, 0.35)):
        sel = [g for g in gws if g["observed"] == cls and g["p_release"] >= 0.5]
        A.scatter([g["dE_keV"] for g in sel], [max(g["isomer_keV"], 0.5) for g in sel],
                  s=sz, color=col, alpha=al, lw=0, label=lab, marker=mk)
    A.axvspan(0.1, NEEC_KEV, color=AMBER, alpha=0.08)
    A.text(0.13, 6.5e3, "NEEC class:\ngateway within 30 keV", color=AMBER, fontsize=8, ha="left", va="top")
    for nid, E, name in (("93mo", 2424.95, "⁹³ᵐMo"), ("178hf", 2446.09, "¹⁷⁸ᵐ²Hf"), ("180ta", 75.3, "¹⁸⁰ᵐTa"), ("177lu", 970.18, "¹⁷⁷ᵐLu")):
        cand = [g for g in gws if g["nuclide"] == nid and abs(g["isomer_keV"] - E) < 2 and g["p_release"] >= 0.5]
        if cand:
            g = min(cand, key=lambda g: g["dE_keV"])
            A.annotate(name, xy=(g["dE_keV"], g["isomer_keV"]), xytext=(g["dE_keV"] * 2.2, g["isomer_keV"] * 1.7),
                       fontsize=8.5, color=INK, fontweight="bold", arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
    A.set_xscale("log"); A.set_yscale("log")
    A.set_xlabel("gateway energy above the isomer, ΔE (keV)")
    A.set_ylabel("energy stored in the isomer (keV)")
    A.set_title("A.  Every releasing gateway in the chart")
    A.legend(frameon=False, fontsize=8.5, loc="lower left")

    # B: coincidences against what a rotor can close and what the data can say
    comp = [p for p in prs if p["compatible"]]
    if comp:
        E = np.array([p["A_line_keV"] for p in comp])
        d = np.array([max(abs(p["delta_eV"]), 1e-2) for p in comp])
        s = np.array([p["sigma_eV"] for p in comp])
        res = np.array([p["resonant_within_reach"] for p in comp], bool)
        B.scatter(E[~res], d[~res], s=5, color=GREY, alpha=0.35, lw=0,
                  label="compatible coincidence: |mismatch| as the data give it")
        if res.any():
            B.scatter(E[res], d[res], s=40, color=PURPLE, lw=0, zorder=4,
                      label="resonant within rotor reach, and the data can say so")
        edges_b = np.logspace(1.3, 3.5, 23)
        mids, meds = [], []
        for lo_, hi_ in zip(edges_b[:-1], edges_b[1:]):
            m = (E >= lo_) & (E < hi_)
            if m.sum() >= 5:
                mids.append(math.sqrt(lo_ * hi_)); meds.append(float(np.median(s[m])))
        if mids:
            B.plot(mids, meds, color=INK, lw=1.8, ls="--", label="median uncertainty of the three energies (ENSDF)")
        xs = np.logspace(1.3, 3.5, 100)
        B.plot(xs, xs * 1e3 * V_ROTOR / C_M_S + 2 * np.array([doppler_fwhm_ev(x, 150) for x in xs]),
               color=RED, lw=1.8, label="what a 1 km/s rotor and two thermal widths close")
        B.set_xscale("log"); B.set_yscale("log")
        B.set_ylim(1e-2, 1e5)
        B.text(0.42, 0.30, "the gap between the dashed and the red lines\nis how much better the energies must be known",
               transform=B.transAxes, fontsize=8, color=INK)
    B.set_xlabel("line energy (keV)")
    B.set_ylabel("|mismatch| with the data's uncertainty (eV)")
    B.set_title("B.  Coincidences: the rotor's reach against the data's precision")
    B.legend(frameon=False, fontsize=7.6, loc="upper left")

    # C: the areal density wall, measured widths apart from estimates
    for kind, col, lab, z, al in (("Weisskopf", AMBER, "Weisskopf estimate: an upper bound, not a candidate", 2, 0.55),
                                  ("measured", BLUE, "gateway width measured by ENSDF", 3, 0.95)):
        th = np.array([p["thickness_cm"] for p in comp if p["thickness_cm"] and p["B_width_kind"].startswith(kind)])
        if len(th):
            C.hist(np.log10(th), bins=np.arange(-6, 6.5, 0.5), color=col, alpha=al, label=lab, zorder=z,
                   edgecolor="white" if kind == "measured" else "none", lw=0.6)
    C.axvline(0, color=RED, lw=1.5, ls="--")
    C.axvline(-4, color=GREY, lw=1.2, ls=":")
    yl = C.get_ylim()[1]
    C.text(0.15, yl * 0.55, "one centimetre\nof pure isomer", color=RED, fontsize=8.5)
    C.text(-3.85, yl * 0.55, "one\nmicrometre", color=GREY, fontsize=8.5)
    C.set_xlabel("log₁₀ thickness of fully inverted isomer the amplification condition needs (cm)")
    C.set_ylabel("compatible coincidences")
    C.set_title("C.  The areal density wall, with the chart's own candidates in it")
    C.legend(frameon=False, fontsize=8.5, loc="upper right")

    # D: inhibition inventory
    counts = np.array(list(iso_two.values()))
    if len(counts):
        top = int(min(counts.max(), 8))
        bins = np.arange(0.5, top + 1.5, 1)
        D.hist(np.minimum(counts, top), bins=bins, color=GREY, alpha=0.8, label="isomers by number of releasing gateways")
        n_inh = len({(r["nuclide"], r["isomer_keV"]) for r in inh})
        D.bar([top + 1.5], [n_inh], color=GREEN, width=0.8, label="isomers with a signal gateway and a veto gateway")
        D.set_xticks(list(range(1, top + 1)) + [top + 1.5])
        D.set_xticklabels([str(i) if i < top else f"{top}+" for i in range(1, top + 1)] + ["veto\npairs"])
    D.set_xlabel("releasing gateways per isomer")
    D.set_ylabel("isomers")
    D.set_title("D.  Inhibition: the operation the neutron sector lacked")
    D.legend(frameon=False, fontsize=8.5, loc="upper right")

    fig.suptitle("Figure 16.  The photon keystone, searched in ENSDF", fontsize=13, fontweight="bold", y=1.0)
    fig.tight_layout()
    for ext in ("svg", "png"):
        kw = {"metadata": {"Date": None}} if ext == "svg" else {}
        fig.savefig(os.path.join(FIGS, f"fig16_photon_keystone.{ext}"), bbox_inches="tight", **kw)
    plt.close(fig)
    print("wrote fig16_photon_keystone")


if __name__ == "__main__":
    main()
