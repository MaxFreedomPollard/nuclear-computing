#!/usr/bin/env python3
"""
Figure generator for the Nuclear Computing foundational document.
Produces clean, GitHub-renderable SVG (and PNG) figures with real numbers.
No claim is plotted that is not derived in the README text.
"""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.ticker import LogLocator
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- house style -----------------------------------------------------------
INK    = "#16213e"
BLUE   = "#2563eb"
RED    = "#dc2626"
GREEN  = "#16a34a"
AMBER  = "#d97706"
PURPLE = "#7c3aed"
GREY   = "#94a3b8"
GRID   = "#e5e7eb"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.titlecolor": INK,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 130,
    "svg.hashsalt": "nuclear-computer",
})

def save(fig, name):
    for ext in ("svg", "png"):
        kw = {"metadata": {"Date": None}} if ext == "svg" else {}
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), bbox_inches="tight", **kw)
    plt.close(fig)
    print("wrote", name)

# ===========================================================================
# FIG 2. The Poisson precision law:  N >= 2^(2b);  t = N/lambda
# ===========================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))

b = np.arange(1, 17)
N = 2.0**(2*b)
ax1.semilogy(b, N, "-o", color=BLUE, lw=2.2, ms=5)
ax1.set_xlabel("precision  b  (bits)")
ax1.set_ylabel("counts required  $N = rT \\geq 2^{2b}$")
ax1.set_title("Cost of precision in a Poisson medium")
ax1.set_xticks(np.arange(2, 17, 2))
for bb, color in [(8, RED), (16, AMBER)]:
    ax1.annotate(f"{bb} bit\n$N={2**(2*bb):,}$",
                 xy=(bb, 2.0**(2*bb)), xytext=(bb-4.5, 2.0**(2*bb)*6),
                 fontsize=9, color=color, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=color, lw=1.3))

# time to a result vs activity
lams = [(3.7e4, "1 µCi", GREY),
        (3.7e7, "1 mCi", GREEN),
        (3.7e10, "1 Ci", BLUE),
        (1e15, "PBq source", PURPLE)]
bb = np.linspace(1, 16, 200)
Nn = 2.0**(2*bb)
for lam, lab, c in lams:
    ax2.semilogy(bb, Nn/lam, color=c, lw=2.2, label=lab)
ax2.axhline(1.0, color=INK, ls=":", lw=1)
ax2.text(1.2, 1.4, "1 second", fontsize=8, color=INK)
ax2.axhspan(1e-9, 1e-3, color=GREEN, alpha=0.06)
ax2.set_xlabel("precision  b  (bits)")
ax2.set_ylabel("time per gate evaluation  $t = 2^{2b}/\\lambda$  (s)")
ax2.set_title("Throughput is bought with source activity")
ax2.set_ylim(1e-10, 1e6)
ax2.legend(frameon=False, fontsize=9, loc="upper left")
fig.tight_layout()
save(fig, "fig2_precision_law")

# ===========================================================================
# FIG 3. THE KEYSTONE: triggered release gate viability
#   Panel A: trigger efficiency eta = R/(R+lambda_m) vs trigger rate R
#   Panel B: net photon gain  Gamma = beta*eta / C_in  vs cascade beta
# ===========================================================================
fig, (axA, axB) = plt.subplots(1, 2, figsize=(11, 4.5))

R = np.logspace(-10, 6, 400)  # achievable trigger rate (1/s)
iso = [
    ("$^{229m}$Th  (t$_{1/2}$ = 29 min)", math.log(2)/1740.0, BLUE),
    ("$^{93m}$Mo  (t$_{1/2}$ = 6.85 h)",  math.log(2)/(6.85*3600), AMBER),
    ("$^{178m2}$Hf  (t$_{1/2}$ = 31 yr)", math.log(2)/(31*3.15e7), RED),
]
for lab, lm, c in iso:
    eta = R/(R+lm)
    axA.semilogx(R, eta, color=c, lw=2.4, label=lab)
    axA.axvline(lm, color=c, ls=":", lw=1.1, alpha=0.7)
axA.axhline(0.5, color=GREY, ls="--", lw=1)
axA.set_xlabel("driven release rate  $R_{\\rm trig}=\\sigma_{\\rm trig}\\,\\phi_{\\rm ctrl}$  (s$^{-1}$)")
axA.set_ylabel("trigger efficiency  $\\eta = R_{\\rm trig}/(R_{\\rm trig}+\\lambda_m)$")
axA.set_title("A.  Beating the spontaneous leak")
axA.legend(frameon=False, fontsize=8.5, loc="center left")
axA.set_ylim(-0.03, 1.03)
axA.text(3e-9, 0.07, "dotted = spontaneous\ndecay rate $\\lambda_m$",
         fontsize=8, color=GREY)

# Panel B: gain criterion
beta = np.linspace(1, 40, 200)
Cin = 1.0
for eta_fixed, c, ls in [(0.99, GREEN, "-"), (0.5, AMBER, "--"), (0.1, RED, ":")]:
    axB.plot(beta, beta*eta_fixed/Cin, color=c, lw=2.4, ls=ls,
             label=f"$\\eta={eta_fixed}$")
axB.axhline(1.0, color=INK, lw=1.6)
axB.fill_between(beta, 1.0, 1e3, color=GREEN, alpha=0.05)
axB.text(1.2, 20.5, "amplifying gate  $\\Gamma>1$", color=GREEN, fontsize=9.5, fontweight="bold")
axB.text(24, 0.45, "lossy  $\\Gamma<1$", color=RED, fontsize=9)
# candidate markers (beta values computed from ENSDF in gates/)
axB.scatter([1], [0.99], color=BLUE, zorder=5, s=70)
axB.annotate("$^{229m}$Th\n($\\beta\\!\\approx\\!1$: a qubit/memory,\nnot an amplifier)",
             xy=(1, 0.99), xytext=(4, 2.4), fontsize=8, color=BLUE,
             arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.2))
axB.scatter([12.39], [12.39*0.5], color=RED, zorder=5, s=70)
axB.annotate("$^{178m2}$Hf\n($\\beta=12.4$ photon cascade,\n2.4 MeV stored, unproven trigger)",
             xy=(12.39, 6.2), xytext=(14.5, 12.9), fontsize=8, color=RED,
             arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
axB.scatter([2.87], [2.87*0.5], color=AMBER, zorder=5, s=70)
axB.annotate("$^{93m}$Mo\n($\\beta=2.87$, NEEC contested)",
             xy=(2.87, 1.44), xytext=(5.5, 0.35), fontsize=8, color=AMBER,
             arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.2))
axB.scatter([11], [11*0.9997], color=GREEN, zorder=6, s=130, marker="*")
axB.annotate("$^{242m}$Am (n,f)  PROVEN\n$\\eta=0.9997$ at reactor flux, $\\Gamma\\approx11$:\nboth inequalities met (see /gates)",
             xy=(11, 11), xytext=(21.5, 7.3), fontsize=8, color=GREEN,
             fontweight="bold",
             arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.4))
axB.set_xlabel("cascade multiplicity  $\\beta$  (output photons per release)")
axB.set_ylabel("net photon gain  $\\Gamma = \\beta\\,\\eta / C_{\\rm in}$")
axB.set_title("B.  The amplification criterion")
axB.set_ylim(0, 22)
axB.legend(frameon=False, fontsize=9, loc="upper right", title="trigger eff.")
fig.tight_layout()
save(fig, "fig3_keystone_gate")

# ===========================================================================
# FIG 4. Throughput law: f_gate ~ lambda / 2^(2b)
# ===========================================================================
fig, ax = plt.subplots(figsize=(7.2, 4.6))
lam = np.logspace(4, 18, 300)
for bbits, c in [(4, GREEN), (8, BLUE), (12, AMBER), (16, RED)]:
    ax.loglog(lam, lam/2.0**(2*bbits), color=c, lw=2.3, label=f"{bbits} bit outputs")
ax.axhline(1, color=INK, ls=":", lw=1)
ax.text(2e4, 1.6, "1 gate eval / s", fontsize=8)
for x, lab in [(3.7e7, "1 mCi"), (3.7e10, "1 Ci"), (1e14, "industrial\n$^{60}$Co"), (1e18, "research\nreactor flux")]:
    ax.axvline(x, color=GREY, ls="--", lw=0.9, alpha=0.7)
    ax.text(x*1.1, 2e-6, lab, rotation=90, va="bottom", fontsize=7.5, color=GREY)
ax.set_xlabel("source activity / event budget  $\\lambda$  (decays s$^{-1}$)")
ax.set_ylabel("sustained gate evaluation rate  $f_{\\rm gate}\\approx \\lambda/2^{2b}$  (s$^{-1}$)")
ax.set_title("Throughput law of a coincidence gate network")
ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.set_ylim(1e-7, 1e14)
fig.tight_layout()
save(fig, "fig4_throughput")

# ===========================================================================
# FIG 5. Energy per operation (the honesty figure) + ops per decay reframe
# ===========================================================================
fig, ax = plt.subplots(figsize=(8.2, 4.6))
items = [
    ("Landauer limit (300 K)", 2.9e-21, GREEN),
    ("CMOS switch (modern)",   1e-16,   GREEN),
    ("MTJ probabilistic bit (33 fJ)", 3.3e-14, BLUE),
    ("IR / optical photon (1 eV)", 1.6e-19, BLUE),
    ("$^{229m}$Th quantum (8.4 eV)", 1.34e-18, PURPLE),
    ("keV X ray gate (10 keV)", 1.6e-15, AMBER),
    ("MeV γ gate (1 MeV)",     1.6e-13, RED),
]
labels = [i[0] for i in items]
vals   = [i[1] for i in items]
cols   = [i[2] for i in items]
y = np.arange(len(items))[::-1]
ax.barh(y, vals, color=cols, alpha=0.85, height=0.62)
ax.set_xscale("log")
ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=9.5)
ax.set_xlabel("energy per elementary operation / quantum  (joule, log scale)")
ax.set_title("Energy honesty: high energy quanta are not cheap logic")
ax.set_xlim(1e-22, 1e-11)
for yy, v in zip(y, vals):
    ax.text(v*1.4, yy, f"{v:.0e} J", va="center", fontsize=8, color=INK)
ax.axvspan(1e-22, 1e-15, color=GREEN, alpha=0.05)
ax.text(2e-20, len(items)-0.4, "sane logic regime → use the 8.4 eV transition,\nnot MeV quanta, for dense computation",
        fontsize=8.5, color=INK)
fig.tight_layout()
save(fig, "fig5_energy")

# ===========================================================================
# FIG 6. Technology Readiness vs Centrality (the thesis in one chart)
# ===========================================================================
fig, ax = plt.subplots(figsize=(8.6, 5.6))
comp = [
    # name, readiness(0-10), centrality(0-10), color, dx, dy
    ("Poisson source: power / clock / entropy", 9.7, 5.5, GREEN, 0.15, 0.25),
    ("Linear transport “synapse” (Green's fn)", 9.0, 6.8, GREEN, 0.15, 0.2),
    ("Coincidence AND (γγ)", 9.8, 8.0, GREEN, -3.6, 0.1),
    ("Absorption NOT / scattering MUX", 9.0, 5.2, GREEN, -4.7, -0.45),
    ("$^{229}$Th isomer memory (laser R/W)", 6.8, 7.0, BLUE, -4.0, 0.35),
    ("Mossbauer γ quantum optics", 5.6, 6.0, BLUE, 0.18, 0.0),
    ("Entangled annihilation γ (Tier 2)", 4.6, 5.2, PURPLE, 0.18, -0.1),
    ("TRIGGERED RELEASE GATE\n(NEEC / IGE): THE KEYSTONE", 2.0, 9.7, RED, -1.7, -1.3),
]
for name, rx, cy, c, dx, dy in comp:
    s = 520 if "KEYSTONE" in name else 230
    ax.scatter(rx, cy, s=s, color=c, alpha=0.85, edgecolor="white", lw=1.5, zorder=5)
    fw = "bold" if "KEYSTONE" in name else "normal"
    ax.annotate(name, xy=(rx, cy), xytext=(rx+dx, cy+dy), fontsize=8.4,
                color=c, fontweight=fw, zorder=6)
ax.scatter([2.0], [9.7], s=1400, facecolor="none", edgecolor=RED, lw=1.6, ls="--", zorder=4)
ax.set_xlabel("experimental readiness  →  (established physics)")
ax.set_ylabel("centrality to the theory  →")
ax.set_title("Where the theory lives or dies")
ax.set_xlim(0, 11.5)
ax.set_ylim(4, 11)
ax.axvspan(0, 4, color=RED, alpha=0.04)
ax.text(0.3, 4.25, "unconfirmed / contested", fontsize=8, color=RED)
ax.axvspan(8.5, 11.5, color=GREEN, alpha=0.05)
ax.text(8.7, 4.25, "routine in any nuclear lab", fontsize=8, color=GREEN)
fig.tight_layout()
save(fig, "fig6_readiness")

# ===========================================================================
# FIG 7. Emergent sigmoid: Siegert first passage firing rate (the neuron)
# ===========================================================================
erf = np.vectorize(math.erf)
tau_m, t_ref = 10e-3, 2e-3
Vth, Vr, sig = 15.0, 0.0, 4.0
mus = np.linspace(0, 22, 240)
nus = []
for mu in mus:
    lo, hi = (Vr-mu)/sig, (Vth-mu)/sig
    u = np.linspace(lo, hi, 600)
    integ = np.trapz(np.exp(u**2)*(1+erf(u)), u)
    nu = 1.0/(t_ref + tau_m*math.sqrt(math.pi)*integ)
    nus.append(nu)
nus = np.array(nus)
fig, ax = plt.subplots(figsize=(7.0, 4.4))
ax.plot(mus, nus, color=PURPLE, lw=2.6)
ax.fill_between(mus, 0, nus, color=PURPLE, alpha=0.07)
ax.axvline(Vth, color=GREY, ls="--", lw=1)
ax.text(Vth+0.3, 5, "threshold $V_{\\rm th}$", fontsize=9, color=GREY)
ax.set_xlabel("mean drive  $\\mu$  (set by weighted photon flux  $\\Sigma_j w_j\\phi_j$)")
ax.set_ylabel("output spike rate  $\\nu = \\Phi(\\mu,\\sigma)$  (Hz)")
ax.set_title("The activation is not designed, it emerges (Siegert)")
ax.set_ylim(0, max(nus)*1.08)
fig.tight_layout()
save(fig, "fig7_siegert")

print("All figures generated.")
