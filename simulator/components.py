#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Proofs of concept for the remaining logical components of a working
computer, each run as a simulation whose physics is already demonstrated
elsewhere in this repository. Four demonstrations:

  1. The adder: scaled addition by scattering MUX, exact in expectation.
  2. The clock: a divide by N counter on the Poisson stream yields Erlang
     ticks with relative jitter 1/sqrt(N): a clock of any desired quality
     purchased from pure randomness by the precision law.
  3. The bistable cell: a self exciting loop through a saturable stage
     holds a written bit if and only if loop gain exceeds one. This is
     the keystone criterion appearing as a memory requirement: below
     Gamma_eff = 1 the bit dies of signal death, above it the cell
     latches. The keystone, quantified as a component.
  4. The telemetry link (the mouth, made a channel): on off keying of a
     valve gated emission line, decoded by an external counter. Bit
     error rate versus integration time, and the resulting bits per
     second, computed for a modest detected budget.

Outputs: simulator/components_results.md and figures/fig13_components.*
"""
import math
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(os.path.dirname(HERE), "figures")
RNG = np.random.default_rng(181)          # seed honors Ta-181

INK, BLUE, RED, GREEN, AMBER, PURPLE, GREY = (
    "#16213e", "#2563eb", "#dc2626", "#16a34a",
    "#d97706", "#7c3aed", "#94a3b8")
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "axes.edgecolor": INK,
    "axes.labelcolor": INK, "text.color": INK, "xtick.color": INK,
    "ytick.color": INK, "axes.titlecolor": INK, "font.size": 11,
    "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.grid": True, "grid.color": "#e5e7eb", "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 130, "svg.hashsalt": "nuclear-computer",
})

OUT = []


def say(s=""):
    OUT.append(s)
    print(s)


# ---------------------------------------------------------------------------
# 1. The adder
# ---------------------------------------------------------------------------
def adder():
    say("## 1. The adder (scattering MUX, exact)\n")
    say("A MUX with select probability 1/2 outputs z = (x + y)/2: scaled "
        "addition, the stochastic computing convention. Measured over "
        "200,000 slices per point:\n")
    say("| x | y | exact (x+y)/2 | measured |")
    say("|---|---|---|---|")
    n = 200_000
    worst = 0.0
    for x, y in [(0.1, 0.3), (0.25, 0.5), (0.5, 0.9), (0.8, 0.8)]:
        sel = RNG.random(n) < 0.5
        z = np.where(sel, RNG.random(n) < x, RNG.random(n) < y).mean()
        worst = max(worst, abs(z - (x + y) / 2))
        say(f"| {x} | {y} | {(x+y)/2:.4f} | {z:.4f} |")
    say(f"\nWorst deviation **{worst:.4f}** (counting noise). Subtraction "
        "is addition with a complemented input; multiplication is the "
        "coincidence gate (verified in /transport); comparison is the "
        "degree checked comparator. That set is an ALU for rate coded "
        "words, and every element is a routine gate.\n")


# ---------------------------------------------------------------------------
# 2. The clock
# ---------------------------------------------------------------------------
def clock():
    say("## 2. The clock (divide by N: precision purchased from randomness)\n")
    say("Every Nth event of a Poisson stream defines a tick. Interarrival "
        "of ticks is Erlang(N): mean N/lambda, relative jitter exactly "
        "1/sqrt(N). Measured over 20,000 ticks per point:\n")
    say("| divide by N | predicted jitter | measured |")
    say("|---|---|---|")
    Ns = [1, 10, 100, 1000, 10000]
    meas = []
    for N in Ns:
        gaps = RNG.exponential(1.0, (20_000, 1)) if N == 1 else \
               RNG.gamma(N, 1.0, 20_000)
        gaps = np.asarray(gaps).ravel()
        cv = gaps.std() / gaps.mean()
        meas.append(cv)
        say(f"| {N} | {1/math.sqrt(N):.4f} | {cv:.4f} |")
    say("\nA machine that wants a 0.1 percent clock spends 10^6 decays "
        "per tick and simply has one: the same precision law that prices "
        "readout prices time. There is no crystal oscillator because "
        "none is needed; the randomness is the metronome, averaged.\n")
    return Ns, meas


# ---------------------------------------------------------------------------
# 3. The bistable cell (the keystone, quantified as a component)
# ---------------------------------------------------------------------------
def bistable():
    say("## 3. The bistable cell (memory needs gain, measured)\n")
    say("A self exciting loop through a saturable stage: x' = Gamma "
        "x/(1+x) per pass, seeded by a SET pulse at pass 5. The fixed "
        "points are 0 and Gamma minus 1; the written bit survives if "
        "and only if loop gain Gamma exceeds one:\n")
    say("| loop gain Gamma | state 40 passes after SET | verdict |")
    say("|---|---|---|")
    trajs = {}
    for G in (0.7, 0.95, 1.05, 1.5, 3.0):
        x, xs = 0.0, []
        for t in range(60):
            if t == 5:
                x += 1.0                      # the SET pulse
            x = G * x / (1.0 + x)
            xs.append(x)
        trajs[G] = xs
        final = xs[44]
        say(f"| {G} | {final:.3f} | "
            f"{'**latched**' if final > 0.05 else 'signal death'} |")
    say("\nBelow Gamma = 1 the bit decays geometrically (signal death); "
        "above it the loop latches at Gamma minus 1 and holds "
        "indefinitely against the saturable ceiling. This is the "
        "amplification condition of the keystone criterion reappearing "
        "as the *memory regeneration* requirement, the same reason DRAM "
        "needs sense amplifiers: **a computer's working memory is an "
        "application of gain**. The isomer registers of the crystal "
        "cell store without gain (they are nonvolatile), so the machine "
        "has memory today; what waits on the keystone is memory the "
        "computation itself can rewrite through a loop.\n")
    return trajs


# ---------------------------------------------------------------------------
# 4. The telemetry link
# ---------------------------------------------------------------------------
def telemetry():
    say("## 4. The telemetry link (the modulated glow)\n")
    say("A valve keys one internal emission line on and off (contrast m "
        "= 0.4, per the valve note); an external counter integrates for "
        "T per symbol and thresholds. Detected budget 10,000 counts per "
        "second on the line. Simulated bit error rate, 20,000 symbols "
        "per point:\n")
    say("| symbol time T | counts per symbol | measured BER | bits/s |")
    say("|---|---|---|---|")
    r1, m = 1e4, 0.4
    r0 = r1 * (1 - m)
    Ts = [0.3e-3, 1e-3, 3e-3, 10e-3, 30e-3]
    bers = []
    for T in Ts:
        n_sym = 20_000
        bits = RNG.random(n_sym) < 0.5
        counts = RNG.poisson(np.where(bits, r1, r0) * T)
        thresh = (r1 + r0) * T / 2
        errs = ((counts > thresh) != bits).mean()
        bers.append(max(errs, 1e-6))
        say(f"| {T*1e3:.1f} ms | {r1*T:.0f}/{r0*T:.0f} | {errs:.2e} "
            f"| {1/T:,.0f} |")
    say("\nAt 30 ms symbols the measured error rate is 10^-4 at 33 bits "
        "per second; pushing to a 10^-9 grade link at this budget and "
        "contrast costs roughly 100 ms per symbol, **ten fully reliable "
        "bits per second through a sealed wall, with no antenna, no "
        "cable, and no emission in any conventional radio band**, "
        "carried by a γ line that passes through steel, soil, and "
        "vacuum. The receiver is any spectrometer; the transmitter is "
        "the machine deciding what its own glow says. Rate scales "
        "linearly with detected budget: 10^6 counts per second on the "
        "line is a kilobit link at the same reliability.\n")
    return Ts, bers


# ---------------------------------------------------------------------------
def figure(Ns, meas, trajs, Ts, bers):
    fig, (A, B, C) = plt.subplots(1, 3, figsize=(14.2, 4.5))

    A.loglog(Ns, [1/math.sqrt(N) for N in Ns], "-", color=GREY, lw=1.6,
             label="theory $1/\\sqrt{N}$")
    A.loglog(Ns, meas, "o", color=BLUE, ms=7, label="measured")
    A.set_xlabel("clock divider  N  (decays per tick)")
    A.set_ylabel("relative tick jitter")
    A.set_title("A.  A clock bought from randomness")
    A.legend(frameon=False, fontsize=9)

    for G, c in [(0.7, RED), (0.95, AMBER), (1.05, GREY), (1.5, BLUE),
                 (3.0, GREEN)]:
        B.plot(trajs[G], color=c, lw=2.2, label=f"$\\Gamma={G}$")
    B.axvline(5, color=GREY, ls=":", lw=1)
    B.text(5.6, 1.75, "SET pulse", fontsize=8, color=GREY)
    B.set_xlabel("loop passes")
    B.set_ylabel("stored signal  x")
    B.set_title("B.  Memory is an application of gain")
    B.legend(frameon=False, fontsize=8.5)

    C.semilogy(np.array(Ts) * 1e3, bers, "-o", color=GREEN, lw=2.2, ms=6)
    C.set_xlabel("symbol time (ms)  at $10^4$ detected counts/s")
    C.set_ylabel("bit error rate (floor = sim resolution)")
    C.set_title("C.  The modulated glow as a data link")
    C.text(8.5, 3e-2, "no antenna, no cable:\nthe machine keys its own\n"
           "emission line through a valve", fontsize=8.3, color=INK)

    fig.suptitle("Figure 13.  The remaining components, demonstrated",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    for ext in ("svg", "png"):
        kw = {"metadata": {"Date": None}} if ext == "svg" else {}
        fig.savefig(os.path.join(FIGS, f"fig13_components.{ext}"),
                    bbox_inches="tight", **kw)
    print("wrote fig13_components")


if __name__ == "__main__":
    say("# Component proofs of concept (regenerated by components.py)\n")
    adder()
    Ns, meas = clock()
    trajs = bistable()
    Ts, bers = telemetry()
    open(os.path.join(HERE, "components_results.md"), "w").write("\n".join(OUT))
    print("wrote simulator/components_results.md")
    figure(Ns, meas, trajs, Ts, bers)
