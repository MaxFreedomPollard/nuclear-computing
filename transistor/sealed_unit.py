#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
The ampoule, computed.

Derives every number in SEALED.md: the inventory ledger (deposited power
per GBq), the lamp mismatch arithmetic (why a broadband 148 nm excimer
core cannot write the neV wide nuclear line), the aging curves, and the
boundary bandwidth table. Writes sealed_results.md and figure 11.
"""
import math
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Wedge, FancyArrow

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(os.path.dirname(HERE), "figures")

INK, BLUE, RED, GREEN, AMBER, PURPLE, GREY = (
    "#16213e", "#2563eb", "#dc2626", "#16a34a",
    "#d97706", "#7c3aed", "#94a3b8")
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "axes.edgecolor": INK,
    "axes.labelcolor": INK, "text.color": INK, "xtick.color": INK,
    "ytick.color": INK, "axes.titlecolor": INK, "font.size": 11,
    "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.grid": True, "grid.color": "#e5e7eb", "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 130, "svg.hashsalt": "nuclear-computer",
})

EV = 1.602176634e-19
GBQ = 1e9

# isotope, half life (y), emission label, mean energy per decay (eV)
LEDGER = [
    ("3H", 12.3, "beta, 5.7 keV avg", 5.7e3),
    ("63Ni", 100.0, "beta, 17 keV avg", 17.4e3),
    ("90Sr/90Y", 28.8, "beta pair, 1.13 MeV", 1.13e6),
    ("238Pu", 87.7, "alpha, 5.59 MeV", 5.59e6),
    ("241Am", 432.0, "alpha 5.49 + gamma 0.06 MeV", 5.55e6),
]

OUT = []


def say(s=""):
    OUT.append(s)
    print(s)


def ledger():
    say("## The inventory ledger (deposited power per GBq)\n")
    say("| isotope | half life (y) | emission | deposited power per GBq |")
    say("|---|---|---|---|")
    for name, t, label, e in LEDGER:
        p = GBQ * e * EV
        say(f"| {name} | {t:g} | {label} | {p*1e6:.1f} µW |")
    say("")


def lamp_mismatch():
    say("## The lamp mismatch, step by step\n")
    A = 1e9                      # core activity, Bq (1 GBq)
    E_alpha = 5.5e6              # eV per decay deposited in the gas
    eff_vuv = 0.30               # excimer conversion efficiency (generous)
    E_ph = 8.355733              # eV per 148 nm photon
    rate_ph = A * E_alpha * eff_vuv / E_ph
    say(f"- VUV photon production: 1 GBq x 5.5 MeV x 30% / 8.36 eV = "
        f"**{rate_ph:.1e} photons/s**")
    area = 1.0                   # cm^2 through the compute shell
    flux = rate_ph / area
    lam = 148.38e-9
    dlam = 10e-9                 # excimer second continuum width, ~10 nm
    dnu = 3e8 * dlam / lam**2
    spec_flux = flux / dnu
    say(f"- lamp bandwidth: 10 nm at 148 nm = {dnu:.1e} Hz; spectral flux "
        f"= **{spec_flux:.2f} photons/cm2/s/Hz**")
    lam_cm = lam * 100
    gamma_rad = 1.0 / (2 * math.pi * 1740 / math.log(2))   # ~1e-4 Hz
    sigma_int = (lam_cm**2 / (2 * math.pi)) * gamma_rad
    say(f"- nuclear integrated cross section (lambda^2/2pi) x Gamma_rad = "
        f"{lam_cm**2/(2*math.pi):.2e} cm2 x {gamma_rad:.1e} Hz = "
        f"**{sigma_int:.1e} cm2 Hz**")
    R = spec_flux * sigma_int
    per_voxel = R * 1e8
    say(f"- excitation rate per nucleus R = {R:.1e} /s; per voxel of 1e8 "
        f"nuclei = {per_voxel:.1e} /s, i.e. one write quantum per "
        f"**{1/per_voxel/86400:.0f} days**")
    say(f"- verdict: the bandwidth mismatch (lamp {dnu:.0e} Hz / line "
        f"{gamma_rad:.0e} Hz = {dnu/gamma_rad:.0e}) cannot be bought back "
        "with activity. Broadband self pumping of neV lines is dead; the "
        "sealed unit computes in rates, not isomer populations.\n")
    return rate_ph


def nuclear_lamp():
    """The fix (THEORY.md Section 9): nuclear emitters as internal
    narrowline sources. Computes radiogenic feeding, the standing isomer
    population, and the field addressing sensitivities."""
    say("## The nuclear lamp: the fix, computed\n")
    # radiogenic feeding: 233U alpha decay -> 229mTh, ~2% branch
    lam233 = math.log(2) / (1.592e5 * 3.156e7)
    n233 = 1e17
    feed = 0.02 * lam233 * n233
    tau_m = 630.0
    say(f"- radiogenic feeding: lambda(233U) = {lam233:.2e}/s; at "
        f"{n233:.0e} 233U/cm3 and a 2% branch, **{feed:.0f} isomers/s/cm3**")
    say(f"- standing 229mTh population at tau_m = 630 s: "
        f"**{feed*tau_m:.1e} isomers/cm3**, self replenishing, no photons, "
        "no penetrations (unaddressed: a carrier, not a bit)")
    # field addressing sensitivities: 57Fe vs 181Ta
    say("\n| line | Gamma (eV) | Zeeman shift per T (0.1 mu_N) | "
        "linewidths per T | field per linewidth | Doppler per linewidth |")
    say("|---|---|---|---|---|---|")
    MU_N01 = 0.1 * 3.152e-8          # 0.1 nuclear magneton, eV/T
    for name, E, t_half in [("57Fe 14.4 keV", 14.41e3, 98.3e-9),
                            ("181Ta 6.2 keV", 6238.0, 6.05e-6)]:
        gamma = 6.582e-16 / (t_half / math.log(2))
        lw_per_T = MU_N01 / gamma
        v = 3e10 * gamma / E          # cm/s
        say(f"| {name} | {gamma:.2e} | {MU_N01:.1e} eV/T | "
            f"**{lw_per_T:.1f}** | {1000/lw_per_T:.0f} mT | "
            f"{v*1e4:.2f} um/s |")
    say("\n- reading: 57Fe needs tesla scale steering; **181Ta moves a "
        "full linewidth per ~24 mT and per 3.6 um/s**: millitesla "
        "gradients address it, whispers modulate it. Fed by 181W "
        "(121 d), it is the machine's microsecond, field addressed "
        "latch. Known tax: heavy internal conversion and a small recoil "
        "free fraction; the latch is real but photon poor.\n")


def boundary():
    say("## Boundary bandwidth (detected budget 1e7 events/s)\n")
    say("| precision b (bits) | counts per read 2^2b | reads per second |")
    say("|---|---|---|")
    lamB = 1e7
    rows = []
    for b in (4, 6, 8, 10, 12):
        n = 4**b
        rows.append((b, n, lamB / n))
        say(f"| {b} | {n:,} | {lamB/n:,.0f} |")
    say("")
    return rows


def worked_unit():
    say("## The worked 1 GBq 90Sr ampoule\n")
    proposals = 1e6
    say(f"- proposal budget {proposals:.0e}/s across 64 sites at 26 decays "
        f"per independent sample (measured, /simulator): "
        f"**{proposals/26:,.0f} samples/s at birth**")
    for yr in (0, 28.8, 57.6, 86.4):
        f = 2 ** (-yr / 28.8)
        say(f"  - year {yr:.0f}: {f*100:.0f}% of birth throughput, "
            "identical stationary law (aging theorem)")
    say("")


def figure(bw_rows):
    fig, (A, B, C) = plt.subplots(1, 3, figsize=(14.4, 4.9),
                                  gridspec_kw={"width_ratios": [1.25, 1, 1]})

    # ---- panel A: the ampoule cutaway ------------------------------------
    A.set_xlim(0, 100); A.set_ylim(0, 100)
    A.set_aspect("equal")
    A.axis("off")
    A.set_title("A.  The ampoule: five shells, no penetrations", fontsize=11.5)
    cx, cy = 34, 44
    shells = [
        (33, "#dfe3ea"),
        (27.5, "#f3e8d8"),
        (21.5, "#ece5f7"),
        (15, "#e2ecfb"),
    ]
    for r, c in shells:
        A.add_patch(Circle((cx, cy), r, facecolor=c, edgecolor=INK, lw=1.0))
    A.add_patch(Circle((cx, cy), 8, facecolor=AMBER, edgecolor=INK,
                       lw=1.2, alpha=0.85))
    A.text(cx, cy + 1.5, "core", fontsize=7.5, ha="center",
           fontweight="bold", color="white")
    A.text(cx, cy - 3, "148 nm lamp", fontsize=5.8,
           ha="center", color="white")
    # label column fully clear of the rings, one leader per shell
    ang = math.radians(36)
    labels = [
        (86, "shield and shell", INK, 33),
        (71, "the mouth: counts, current,\nspectrum; self powered", AMBER, 27.5),
        (54, "trim layer: weights set by\nfields through the wall", PURPLE, 21.5),
        (38, "compute shell:\nthe problem in a can", BLUE, 15),
    ]
    for ty, s, c, r in labels:
        A.annotate(s, xy=(cx + (r - 2.5) * math.cos(ang),
                          cy + (r - 2.5) * math.sin(ang)),
                   xytext=(71, ty), fontsize=7.4, color=c,
                   ha="left", va="center",
                   arrowprops=dict(arrowstyle="->", color=c, lw=0.9))
    # field lines in (left), glow out (bottom right)
    for yy in (31, 44, 57):
        A.add_patch(FancyArrow(0.5, yy, 5.5, 0, width=0.5, head_width=2.2,
                               head_length=2.2, facecolor=PURPLE,
                               edgecolor="none"))
    A.text(1, 92, "fields in: Zeeman maps,\nDoppler waveforms,\nmagnetic apertures",
           fontsize=7.2, color=PURPLE, ha="left")
    for deg in (-58, -40, -22):
        rad = math.radians(deg)
        x0 = cx + 33.5 * math.cos(rad); y0 = cy + 33.5 * math.sin(rad)
        A.add_patch(FancyArrow(x0, y0, 6.5 * math.cos(rad), 6.5 * math.sin(rad),
                               width=0.5, head_width=2.2, head_length=2.2,
                               facecolor=GREEN, edgecolor="none"))
    A.text(71, 12, "glow out: the answer\nis the spectrum", fontsize=7.2,
           color=GREEN, ha="left")

    # ---- panel B: aging curves -------------------------------------------
    yrs = np.linspace(0, 100, 400)
    for (name, T, _, _), c in zip(LEDGER, (GREY, BLUE, AMBER, PURPLE, GREEN)):
        B.plot(yrs, 2.0 ** (-yrs / T), color=c, lw=2.2,
               label=f"{name} (t½ {T:g} y)")
    B.axhline(0.5, color=GREY, ls="--", lw=1)
    B.set_xlabel("years after sealing")
    B.set_ylabel("throughput fraction  $C(t)/C_0$")
    B.set_title("B.  Aging: speed halves, answers never change")
    B.set_ylim(0, 1.02)
    B.legend(frameon=False, fontsize=7.8)
    B.text(52, 0.53, "half throughput", fontsize=7.5, color=GREY)

    # ---- panel C: the mouth ----------------------------------------------
    bs = [r[0] for r in bw_rows]
    fs = [r[2] for r in bw_rows]
    C.semilogy(bs, fs, "-o", color=GREEN, lw=2.2, ms=6)
    for b, f in zip(bs, fs):
        C.annotate(f"{f:,.0f}/s", xy=(b, f), xytext=(b + 0.15, f * 1.6),
                   fontsize=7.8, color=GREEN)
    C.set_xlabel("read precision  b  (bits)")
    C.set_ylabel("reads per second (detected budget $10^7$/s)")
    C.set_title("C.  The mouth: precision is purchasable")
    C.set_xticks(bs)

    fig.suptitle("Figure 11.  The sealed machine and its boundary",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    for ext in ("svg", "png"):
        kw = {"metadata": {"Date": None}} if ext == "svg" else {}
        fig.savefig(os.path.join(FIGS, f"fig11_sealed_unit.{ext}"),
                    bbox_inches="tight", **kw)
    print("wrote fig11_sealed_unit")


if __name__ == "__main__":
    say("# The ampoule, computed (regenerated by sealed_unit.py)\n")
    ledger()
    lamp_mismatch()
    nuclear_lamp()
    rows = boundary()
    worked_unit()
    open(os.path.join(HERE, "sealed_results.md"), "w").write("\n".join(OUT))
    print("wrote transistor/sealed_results.md")
    figure(rows)
