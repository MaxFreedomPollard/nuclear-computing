#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Figure 10: the nuclear transistor at three scales.

One schematic, three physical embodiments, terminals labeled with the same
pinout in every panel (GATE, SOURCE, DRAIN, CHANNEL, BODY). Companion to
transistor/README.md; every number drawn here is derived there or in /gates.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (Rectangle, Circle, FancyArrow,
                                FancyBboxPatch, Polygon)

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(os.path.dirname(HERE), "figures")

INK, BLUE, RED, GREEN, AMBER, PURPLE, GREY = (
    "#16213e", "#2563eb", "#dc2626", "#16a34a",
    "#d97706", "#7c3aed", "#94a3b8")
LIGHT = "#eef4ff"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "text.color": INK, "font.size": 11,
    "svg.hashsalt": "nuclear-computer",
})

FS = 7.6          # label font size
TFS = 8.2         # terminal font size


def term(ax, x, y, name, color, ha="center"):
    ax.text(x, y, name, fontsize=TFS, fontweight="bold", color=color,
            ha=ha, va="center")


def note(ax, x, y, s, color=INK, ha="center", fs=FS):
    ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va="center")


def scalebar(ax, x0, x1, y, label):
    ax.plot([x0, x1], [y, y], color=INK, lw=1.6)
    for x in (x0, x1):
        ax.plot([x, x], [y - 1.2, y + 1.2], color=INK, lw=1.6)
    note(ax, (x0 + x1) / 2, y - 4, label, fs=8)


def panel_frame(ax, title, subtitle):
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.text(50, 97, title, fontsize=11.5, fontweight="bold",
            color=INK, ha="center")
    ax.text(50, 90.5, subtitle, fontsize=8.4, color=GREY, ha="center")


# ---------------------------------------------------------------------------
fig, (A, B, C) = plt.subplots(1, 3, figsize=(14.4, 5.0))

# ============================ PANEL A: benchtop =============================
panel_frame(A, "A.  Benchtop cell (today)",
            "catalog parts, about $350; 385 samples/s measured in simulation")

# source disk
A.add_patch(Circle((10, 55), 5.5, facecolor=AMBER, edgecolor=INK, lw=1.2))
note(A, 10, 44.5, "¹³⁷Cs disk, 1 µCi\n3.7×10⁴ decays/s")
term(A, 10, 66, "SOURCE", AMBER)

# shutter (gate)
A.add_patch(Rectangle((22, 40), 4, 13, facecolor=INK))
A.add_patch(Rectangle((22, 58), 4, 13, facecolor=INK))
A.add_patch(Rectangle((20.5, 30), 7, 6, facecolor="#d7dbe6", edgecolor=INK, lw=0.8))
note(A, 24, 26, "servo")
note(A, 24, 78.5, "tungsten shutter\nthinning α ∈ [0,1]")
term(A, 24, 71, "GATE", BLUE)

# collimator
A.add_patch(Polygon([[32, 62], [48, 58.5], [48, 56], [32, 58]],
                    facecolor=GREY, edgecolor=INK, lw=0.8))
A.add_patch(Polygon([[32, 48], [48, 51.5], [48, 54], [32, 52]],
                    facecolor=GREY, edgecolor=INK, lw=0.8))
note(A, 44.5, 36.5, "collimator (fixed weights $\\mathcal{G}$)")

# beam
A.add_patch(FancyArrow(15.5, 55, 37, 0, width=0.7, head_width=2.6,
                       head_length=2.5, facecolor=AMBER, edgecolor="none",
                       alpha=0.75))

# scintillators
for yy in (47.5, 57):
    A.add_patch(Rectangle((56, yy), 9, 9 if yy == 47.5 else 9,
                          facecolor=LIGHT, edgecolor=BLUE, lw=1.3))
note(A, 68, 41, "2 × EJ-200 cubes\n+ SiPM readout")
term(A, 60.5, 71, "BODY", BLUE)
note(A, 60.5, 76.5, "coincidence window 100 ns")

# channel note
note(A, 40, 66.5, "CHANNEL = rate xλ", PURPLE, fs=TFS)

# output
A.add_patch(FancyArrow(66.5, 56.5, 16, 0, width=0.9, head_width=3.2,
                       head_length=3, facecolor=GREEN, edgecolor="none"))
term(A, 75, 66, "DRAIN", GREEN)
note(A, 75, 48.5, "coincidence\nrate out")

# feedback
A.annotate("", xy=(24, 20), xytext=(84, 52),
           arrowprops=dict(arrowstyle="->", color=GREY, lw=1.1, ls="--",
                           connectionstyle="arc3,rad=0.35"))
note(A, 57, 15.5, "feedback to next cell's aperture (recurrence)", GREY)

scalebar(A, 72, 92, 9, "5 cm")

# ============================ PANEL B: crystal ==============================
panel_frame(B, "B.  Crystal cell (the target)",
            "Th:CaF₂, no wires, no junctions; cells are defined by beams")

# crystal body
B.add_patch(FancyBboxPatch((14, 20), 64, 46,
                           boxstyle="round,pad=1.5,rounding_size=3",
                           facecolor=LIGHT, edgecolor=BLUE, lw=1.5))
term(B, 20, 14, "BODY", BLUE)
note(B, 52, 14, "CaF₂ lattice, doped ²²⁹Th at 10¹⁷ to 10¹⁸ cm⁻³", fs=7.2)

# voxel grid: 4 columns x 2 rows, right region left open for the burst
for gx in range(4):
    for gy in range(2):
        B.add_patch(Rectangle((22 + gx * 10, 26 + gy * 13), 7, 9,
                              facecolor="white", edgecolor=GREY, lw=0.6))
# the active voxel (last column, top row)
B.add_patch(Rectangle((52, 39), 7, 9, facecolor=PURPLE, edgecolor=INK,
                      lw=1.2, alpha=0.85))
term(B, 36, 84, "CHANNEL", PURPLE)
note(B, 36, 77.5, "voxel (10 µm)³: 10⁸ nuclei\nn_m = isomer fraction", PURPLE,
     fs=7.2)
B.annotate("", xy=(55.5, 48.5), xytext=(44, 73),
           arrowprops=dict(arrowstyle="->", color=PURPLE, lw=0.9))

# write/trigger beam from the far top left
B.add_patch(Polygon([[4, 84], [52.5, 48], [55, 45], [7, 80]],
                    facecolor=BLUE, edgecolor="none", alpha=0.5))
term(B, 3, 76, "GATE", BLUE, ha="left")
note(B, 3, 70.5, "148.38 nm\nwrite / trigger", BLUE, ha="left")

# fluorescence burst into the open right region
for dx, dy in [(10, 0), (8, -6.5), (9.5, 5.5)]:
    B.add_patch(FancyArrow(59.5, 43, dx, dy, width=0.55, head_width=2.2,
                           head_length=2.2, facecolor=GREEN,
                           edgecolor="none"))
term(B, 69, 57, "DRAIN", GREEN)
note(B, 68, 27.5, "8.4 eV burst ∝ n_m\nto next voxel / boundary", GREEN,
     fs=7.2)

# source bath
for sx, sy in [(9, 51), (84, 66), (88, 45), (8, 33), (85, 12), (28, 9)]:
    B.plot(sx, sy, ".", color=AMBER, ms=5)
term(B, 88, 82, "SOURCE", AMBER)
note(B, 88, 76, "bath: power, clock, entropy", AMBER, ha="right", fs=7.2)

# the empty gain socket
B.add_patch(Circle((32, 53), 4.4, facecolor="none", edgecolor=RED,
                   lw=1.5, ls="--"))
note(B, 26, 61, "gain socket: EMPTY\n(the keystone)", RED, fs=7.2)

scalebar(B, 74, 94, 7, "20 µm")

# ============================ PANEL C: neutron ==============================
panel_frame(C, "C.  Neutron gate (proven)",
            "the same pinout with the gain socket filled, since 1942")

# moderator
C.add_patch(Rectangle((22, 20), 56, 52, facecolor="#eceff5",
                      edgecolor=INK, lw=1.2))
note(C, 50, 14.5, "moderator")
term(C, 33, 14.5, "BODY", BLUE)

# fissile region
C.add_patch(Circle((50, 45), 11, facecolor=GREEN, edgecolor=INK,
                   lw=1.2, alpha=0.55))
note(C, 50, 45, "²³⁵U or ²⁴²ᵐAm\nk = 0.9", fs=8)
note(C, 50, 60.5, "neutron population", PURPLE)
term(C, 50, 65.5, "CHANNEL", PURPLE)

# control rod
C.add_patch(Rectangle((46.5, 72), 7, 24, facecolor=RED, edgecolor=INK, lw=1))
note(C, 63.5, 82, "control absorber,\nprogrammable", RED, ha="left")
term(C, 43, 85, "GATE", RED, ha="right")

# incoming neutrons
for yy in (38, 45, 52):
    C.add_patch(FancyArrow(6, yy, 13, 0, width=0.5, head_width=2,
                           head_length=2.2, facecolor=AMBER, edgecolor="none"))
note(C, 10, 29, "driver + neighbor\nneutrons", AMBER)
term(C, 10, 59, "SOURCE", AMBER)

# multiplied output
for yy, w in [(39, 1.0), (45, 1.0), (51, 1.0)]:
    C.add_patch(FancyArrow(80, yy, 14, 0, width=w, head_width=3.2,
                           head_length=2.6, facecolor=GREEN, edgecolor="none"))
note(C, 87, 30.5, "multiplied leakage\nM = 1/(1−k) = 10", GREEN)
term(C, 87, 59, "DRAIN", GREEN)

scalebar(C, 72, 92, 6, "0.5 m")

fig.suptitle("Figure 10.  One schematic, three scales: the nuclear transistor",
             fontsize=13, fontweight="bold", color=INK, y=1.01)
fig.tight_layout()
for ext in ("svg", "png"):
    kw = {"metadata": {"Date": None}} if ext == "svg" else {}
    fig.savefig(os.path.join(FIGS, f"fig10_nuclear_transistor.{ext}"),
                bbox_inches="tight", **kw)
print("wrote fig10_nuclear_transistor")
