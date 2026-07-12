#!/usr/bin/env python3
"""
Figure 12: the nuclear transistor datasheet curves.

Panel A: the benchtop multiplier's transfer family (exact, no gain).
Panel B: the crystal cell's write, hold, and read behavior.
Panel C: the neutron gate's gain and switching time versus k, with the
constant gain bandwidth product 1/Lambda.

Companion to device/DEVICE.md; every curve is the equation cited there.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
    "axes.titlesize": 12.5, "axes.titleweight": "bold",
    "axes.grid": True, "grid.color": "#e5e7eb", "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 130, "svg.hashsalt": "nuclear-computer",
})

fig, (A, B, C) = plt.subplots(1, 3, figsize=(14.2, 4.6))

# ---- A: multiplier transfer family ----------------------------------------
alpha = np.linspace(0, 1, 100)
for x2, c in [(0.25, GREY), (0.5, AMBER), (0.75, BLUE), (1.0, GREEN)]:
    A.plot(alpha, alpha * x2, color=c, lw=2.3, label=f"$x_2 = {x2}$")
A.set_xlabel("gate setting  $\\alpha$  (aperture, the input)")
A.set_ylabel("output rate  $r_{\\rm out} / 2\\tau_w \\lambda^2$")
A.set_title("A.  Benchtop transfer: an exact multiplier")
A.legend(frameon=False, fontsize=8.5, title="drive $x_2$", loc="upper left")
A.text(0.42, 0.06, "linear family, no gain:\nthe triode plot of a\n"
       "device that multiplies", fontsize=8, color=INK)

# ---- B: crystal write / hold / read ----------------------------------------
t_w = np.linspace(0, 3, 150)                 # write phase, units of 1/(sigma phi)
t_h = np.linspace(3, 9, 200)                 # hold phase
ratio = 5.0                                  # tau_m / t_write, illustrative
n_w = 1 - np.exp(-t_w)
n_h = n_w[-1] * np.exp(-(t_h - 3) / ratio)
B.plot(t_w, n_w, color=BLUE, lw=2.4, label="write: $1-e^{-\\sigma_p\\phi_p t}$")
B.plot(t_h, n_h, color=PURPLE, lw=2.4, label="hold: $e^{-\\lambda_m t}$")
B.axvspan(0, 3, color=BLUE, alpha=0.04)
B.axvspan(3, 9, color=PURPLE, alpha=0.04)
B.annotate("read: burst $\\propto n_m$,\ndestructive, at any moment",
           xy=(5.6, n_w[-1] * np.exp(-2.6 / ratio)), xytext=(4.6, 0.32),
           fontsize=8, color=GREEN,
           arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.2))
B.text(0.25, 0.92, "GATE on", fontsize=8.5, color=BLUE)
B.text(3.4, 0.92, "GATE off: nonvolatile for $\\sim\\tau_m$", fontsize=8.5,
       color=PURPLE)
B.set_xlabel("time  (units of the write constant $1/\\sigma_p\\phi_p$;"
             " scales per text)")
B.set_ylabel("isomer fraction  $n_m$  (the CHANNEL)")
B.set_title("B.  Crystal cell: write, hold, read")
B.set_ylim(0, 1.02)
B.legend(frameon=False, fontsize=8.5, loc="center right")

# ---- C: neutron gain and the constant GBW ----------------------------------
k = np.linspace(0.5, 0.995, 300)
M = 1 / (1 - k)
C.semilogy(k, M, color=GREEN, lw=2.5, label="gain  $M = 1/(1-k)$")
for Lam, c, lab in [(1e-4, AMBER, "thermal  $\\Lambda=10^{-4}$ s"),
                    (1e-8, BLUE, "fast  $\\Lambda=10^{-8}$ s")]:
    C.semilogy(k, Lam * M, color=c, lw=2.0, ls="--",
               label=f"switch time, {lab}")
C.scatter([0.9], [10], color=GREEN, s=70, zorder=5)
C.annotate("$k=0.9$: gain 10", xy=(0.9, 10), xytext=(0.62, 40),
           fontsize=8.5, color=GREEN,
           arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.1))
C.text(0.52, 2.5e-7,
       "gain × bandwidth = $1/\\Lambda$, a constant:\n"
       "the op amp law, from reactor kinetics\n"
       "(10 kHz thermal, 100 MHz fast)",
       fontsize=8.3, color=INK)
C.set_xlabel("multiplication factor  $k$  (set by the GATE absorber)")
C.set_ylabel("gain (unitless)   /   switching time (s)")
C.set_title("C.  Neutron gate: the op amp tradeoff")
C.legend(frameon=False, fontsize=8, loc="upper left")

fig.suptitle("Figure 12.  Characteristic curves of the nuclear transistor",
             fontsize=13, fontweight="bold", y=1.02)
fig.tight_layout()
for ext in ("svg", "png"):
    kw = {"metadata": {"Date": None}} if ext == "svg" else {}
    fig.savefig(os.path.join(FIGS, f"fig12_datasheet.{ext}"),
                bbox_inches="tight", **kw)
print("wrote fig12_datasheet")
