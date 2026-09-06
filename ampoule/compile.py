#!/usr/bin/env python3
# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""
The vessel, compiled: the compiler of theory Section 11 run on the measured
Green's function of the ampoule rather than on the toy fabric, and the
timing closure that the compilation forces into the open.

Open Problem 4 asked for the transport level Green's function of a real
geometry and for the compiler to be run on it. /ampoule measured the
64 × 64 matrix; this script takes it as the fabric and does what a compiler
does: it places an instance on the fabric (Way B, apertures), reports what
the fabric cannot do (the crosstalk it adds), and then prices the one thing
the design notes never priced, the photon current on every synapse, because
in a rate coded machine a weight is a rate and the precision law says how
long each rate takes to read. Everything below descends from committed
tallies and the theory's own laws; nothing is fitted.

  the fabric        the measured G, symmetrised, sorted into the lattice's
                    coupling classes, and read as geometry (solid angle)
                    times an interaction probability
  the instance      the digital twin's recipe restricted to the lattice's
                    bonds: an 8 azimuth by 8 height Ising problem, 64 sites,
                    ring bonds and axial bonds, Gaussian couplings, biases
  Way B             apertures T = G*/G_fab on the intended bonds; the
                    unintended couplings the fabric adds anyway, per site;
                    the septum as the only inhibitory lever, at its measured
                    factor
  the law           the 64 site twin run on the intended instance and on the
                    as built one, each checked against the exact Boltzmann
                    law by a transfer matrix over the eight rings (256 row
                    states), which the lattice's topology makes exact
  timing closure    the current on every synapse, I_kj ≤ G_kj r_j, from the
                    measured site rates in plastic and in CsI; the time to
                    read it to 4, 6 and 8 bits; the recurrence loop cadence
                    of the transistor note's control law; the independent
                    samples per second the vessel delivers as built against
                    the 38,462 per second the machine note priced; and the
                    ladder of measured levers between the two

Outputs: ampoule/compile_results.md and figures/fig18_compiled.*; numpy
and matplotlib only, from the committed tallies.json.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIGS = os.path.join(ROOT, "figures")
OUT = []

N_AZ, N_Z = 8, 8
N = N_AZ * N_Z
SEED = 90                     # honours Sr-90, the core
PROPOSAL_BUDGET = 1e6         # per second across the sites, SEALED.md Section 8
DECAYS_PER_SAMPLE = 26        # the twin's measured cost, simulator/results.md
PRICED_SAMPLES = PROPOSAL_BUDGET / DECAYS_PER_SAMPLE          # 38,462 per second, sealed_results.md
BENCHTOP_LOOP_S = 2 ** 8 / 1e4                                # the transistor note: 4 bits at 10⁴ per second
BITS = (4, 6, 8)


def say(s=""):
    OUT.append(s)


def times(x):
    if x < 10:
        return f"{x:.2g}×"
    if x < 1e4:
        return f"{x:,.0f}×"
    return f"{sci(x)}"


def hms(s):
    """A duration in the unit a reader would use."""
    if s < 1:
        return f"{s*1e3:.0f} ms"
    if s < 120:
        return f"{s:.2g} s"
    if s < 7200:
        return f"{s/60:.0f} min"
    if s < 2 * 86400:
        return f"{s/3600:.0f} h"
    if s < 2 * 365.25 * 86400:
        return f"{s/86400:.0f} d"
    return f"{s/(365.25*86400):.1f} y"


def sci(x):
    m, e = f"{x:.1e}".split("e")
    return f"{m}×10{str(int(e)).translate(str.maketrans('0123456789-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻'))}"


def rate(x):
    """Samples per second in the form a reader would write."""
    if x >= 1000:
        return f"{x:,.0f}"
    if x >= 1:
        return f"{x:.3g}"
    return f"{x:.2g}"


# ---------------------------------------------------------------------------
# the lattice
# ---------------------------------------------------------------------------
def coupling_class(j, k):
    iz, ia = divmod(j, N_AZ)
    kz, ka = divmod(k, N_AZ)
    da = min(abs(ka - ia), N_AZ - abs(ka - ia))
    dz = abs(kz - iz)
    if j == k:
        return "self"
    if da == 1 and dz == 0:
        return "ring"
    if da == 0 and dz == 1:
        return "axis"
    if da == 1 and dz == 1:
        return "diagonal"
    return "far"


CLASS = np.array([[coupling_class(j, k) for j in range(N)] for k in range(N)])   # CLASS[k, j]
INTENDED = (CLASS == "ring") | (CLASS == "axis")
UNINTENDED = (CLASS == "diagonal") | (CLASS == "far")


def instance(seed=SEED, sigma=1.4, bias=0.5):
    """The twin's recipe (simulator/nuclear_ising.py) on the lattice's bonds."""
    rng = np.random.default_rng(seed)
    W = np.zeros((N, N))
    for j in range(N):
        for k in range(j + 1, N):
            if INTENDED[k, j]:
                W[j, k] = W[k, j] = rng.normal(0, sigma)
    b = rng.normal(0, bias, N)
    return W, b


# ---------------------------------------------------------------------------
# the exact law: a transfer matrix over the rings, along the axis
# ---------------------------------------------------------------------------
ROWS = ((np.arange(2 ** N_AZ)[:, None] >> np.arange(N_AZ)) & 1).astype(float)   # 256 row states


def _lse0(M):
    m = M.max(axis=0)
    return m + np.log(np.exp(M - m[None, :]).sum(axis=0))


def _lse1(M):
    m = M.max(axis=1)
    return m + np.log(np.exp(M - m[:, None]).sum(axis=1))


def exact_law(W, b):
    """log Z, the exact site marginals ⟨z_k⟩ and the exact mean of
    E = ½ zᵀWz + bᵀz under p ∝ exp(E), for any W whose bonds stay within a
    ring or between adjacent rings (the lattice instance does)."""
    def sites(z):
        return [z * N_AZ + a for a in range(N_AZ)]

    def logZ_marg(scale):
        logw = [scale * (0.5 * np.einsum("si,ij,sj->s", ROWS, W[np.ix_(sites(z), sites(z))], ROWS)
                         + ROWS @ b[sites(z)]) for z in range(N_Z)]
        T = [scale * (ROWS @ W[np.ix_(sites(z), sites(z + 1))] @ ROWS.T) for z in range(N_Z - 1)]
        al = [None] * N_Z
        al[0] = logw[0].copy()
        for z in range(1, N_Z):
            al[z] = _lse0(al[z - 1][:, None] + T[z - 1] + logw[z][None, :])
        be = [None] * N_Z
        be[-1] = np.zeros(2 ** N_AZ)
        for z in range(N_Z - 2, -1, -1):
            be[z] = _lse1(T[z] + logw[z + 1][None, :] + be[z + 1][None, :])
        logZ = _lse0(al[-1][:, None])[0]
        marg = np.zeros(N)
        for z in range(N_Z):
            p = np.exp(al[z] + be[z] - logZ)
            marg[sites(z)] = ROWS.T @ p
        return logZ, marg

    logZ, marg = logZ_marg(1.0)
    h = 1e-4
    mean_E = (logZ_marg(1 + h)[0] - logZ_marg(1 - h)[0]) / (2 * h)     # d log Z / d scale
    return logZ, marg, mean_E


# ---------------------------------------------------------------------------
# the twin at 64 sites
# ---------------------------------------------------------------------------
def sigmoid(u):
    return 1.0 / (1.0 + np.exp(-u))


def run_chain(W, b, n_events, seed):
    """The machine, one proposal per event (simulator/nuclear_ising.py)."""
    rng = np.random.default_rng(seed)
    z = rng.integers(0, 2, N).astype(float)
    sites = rng.integers(0, N, n_events)
    urand = rng.random(n_events)
    burn = n_events // 5
    msum = np.zeros(N)
    E = 0.5 * z @ W @ z + b @ z
    etrace = np.empty(n_events - burn)
    for t in range(n_events):
        k = sites[t]
        u = W[k] @ z + b[k]
        new = 1.0 if urand[t] < sigmoid(u) else 0.0
        if new != z[k]:
            E += (new - z[k]) * u                     # W_kk = 0
            z[k] = new
        if t >= burn:
            msum += z
            etrace[t - burn] = E
    return msum / (n_events - burn), etrace


def integrated_autocorr(x, c=6.0):
    """Sokal's adaptive window, in events (simulator/nuclear_ising.py)."""
    x = np.asarray(x) - np.mean(x)
    n = len(x)
    f = np.fft.rfft(x, 2 * n)
    acf = np.fft.irfft(f * np.conjugate(f))[:n].real
    acf /= acf[0]
    tau = 1.0
    for m in range(1, n):
        tau += 2.0 * acf[m]
        if m >= c * tau:
            break
    return max(tau, 1.0)


# ---------------------------------------------------------------------------
def main():
    doc = json.load(open(os.path.join(HERE, "tallies.json")))
    runs, prov = doc["runs"], doc["provenance"]
    G_raw = np.array(runs["synapse_open"]["G"])
    G_std = np.array(runs["synapse_open"]["std"])
    G_sep = np.array(runs["synapse_septum"]["G"])
    r_pl = np.array(runs["source"]["sites"]["total"][0])            # interactions per second per site, plastic
    r_cs = np.array(runs["source_csi"]["sites"]["total"][0])        # the same with CsI cells
    csi_ratio = r_cs.sum() / r_pl.sum()
    lay = prov["site_layout"]
    radius = lay["radius_cm"]
    dz = abs(lay["z_cm"][1] - lay["z_cm"][0])
    cell = 0.2                                                       # cm, the 2 mm cell of the build note

    say("# The vessel, compiled (regenerated by compile.py from tallies.json)\n")
    say("The compiler of theory Section 11, run on the Green's function that /ampoule measured instead of "
        "on the toy fabric of transport/compiler_demo.py, and the timing closure the compilation forces "
        "into the open. Every number descends from the committed tallies, the twin's measured cost per "
        "sample, and the precision law; the instance is the twin's recipe on the lattice's bonds.\n")

    # ---- 0. the fabric ----------------------------------------------------
    say("## 0. The fabric: the measured G, sorted into the lattice's coupling classes\n")
    G = 0.5 * (G_raw + G_raw.T)
    np.fill_diagonal(G, np.diag(G_raw))
    asym = np.abs(G_raw - G_raw.T) / np.maximum(0.5 * (G_raw + G_raw.T), 1e-12)
    big = 0.5 * (G_raw + G_raw.T) > 1e-5
    rel = G_std / np.maximum(G_raw, 1e-12)
    ring_rel = np.median(rel[CLASS == "ring"])
    say("Detailed balance needs a symmetric weight matrix, and a photon that crosses from j to k is as likely "
        "as one crossing from k to j in a mirror symmetric lattice, so the measured matrix is symmetrised; "
        f"the two triangles differ by a median {np.median(asym[big]):.0%} where the coupling exceeds 10⁻⁵, which "
        f"is the {ring_rel:.0%} counting uncertainty of a nearest neighbour entry taken twice. The classes:\n")
    say("| class | pairs | mean G_kj | solid angle Ω/4π of a 2 mm face at that distance | G ÷ (Ω/4π): the interaction probability it implies |")
    say("|---|---|---|---|---|")
    d_ring = 2 * radius * math.sin(math.pi / N_AZ)
    d_axis = dz
    d_diag = math.hypot(d_ring, d_axis)
    omega = {"ring": cell * cell / (4 * math.pi * d_ring ** 2),
             "axis": cell * cell / (4 * math.pi * d_axis ** 2),
             "diagonal": cell * cell / (4 * math.pi * d_diag ** 2)}
    means = {}
    for c in ("self", "ring", "axis", "diagonal", "far"):
        vals = G[CLASS == c]
        means[c] = float(vals.mean())
        om = omega.get(c)
        say(f"| {c} | {len(vals)} | {means[c]:.2e} | " + (f"{om:.2e}" if om else "") + " | "
            + (f"{means[c]/om:.3f}" if om else "") + " |")
    say("")
    p_int = np.mean([means["ring"] / omega["ring"], means["axis"] / omega["axis"]])
    say(f"The fabric is geometry. A nearest neighbour coupling is the solid angle a 2 mm face subtends at "
        f"{d_ring:.1f} cm around the ring or {d_axis:.0f} cm along the axis, times a {p_int:.1%} chance that the "
        f"photon interacts in 2 mm of plastic, and the two classes give the same probability to a few percent. "
        f"With CsI cells the sites interact {times(csi_ratio)} as often (the source stage, results.md), so the "
        f"receiving end of every coupling rises by that factor and the interaction probability becomes "
        f"{min(p_int*csi_ratio, 1):.2f}: CsI takes the receiver to its ceiling, one interaction per photon "
        "that enters, and what remains of a coupling after that is solid angle alone.\n")

    # ---- 1. Way B: the instance on the fabric -----------------------------
    say("## 1. Way B: the instance placed on the fabric by apertures\n")
    W, b = instance()
    n_bonds = int(INTENDED.sum() // 2)
    say(f"The instance is the digital twin's recipe restricted to the lattice's bonds: {N} sites, {n_bonds} bonds "
        f"({int((CLASS == 'ring').sum()//2)} around the rings, {int((CLASS == 'axis').sum()//2)} along the axis), "
        f"Gaussian couplings of standard deviation 1.4 and biases of 0.5, seed {SEED}. Way B compiles it by "
        "division: an intended bond of magnitude |W_kj| rides the fabric's coupling G_kj through an aperture "
        "T_kj = |W_kj| / (s G_kj) ≤ 1, where s, the weights per unit coupling, is set by the bond that needs "
        "the fabric wide open, and the sign is a choice of excitatory or inhibitory channel (theory Section 5.3).\n")
    ring_pairs = (CLASS == "ring")
    s_scale = np.max(np.abs(W[ring_pairs]) / G[ring_pairs])          # weights per unit G: the tightest ring bond opens fully
    T = np.zeros((N, N))
    T[INTENDED] = np.abs(W[INTENDED]) / (s_scale * G[INTENDED])
    say(f"- apertures on the {n_bonds} intended bonds: median transmission {np.median(T[INTENDED]):.2f}, all at or below 1 "
        f"by construction; the ring bond that sets the scale is fully open and the axial bonds, on a coupling "
        f"{means['axis']/means['ring']:.1f}× stronger, sit mostly closed")
    Wab = W.copy()
    Wab[UNINTENDED] = s_scale * G[UNINTENDED]        # what the fabric adds anyway, all excitatory
    per_site_in = np.array([G[k, INTENDED[k]].sum() for k in range(N)])
    per_site_un = np.array([G[k, UNINTENDED[k]].sum() for k in range(N)])
    ratio = per_site_un / per_site_in
    w_in = np.array([np.abs(W[k, INTENDED[k]]).sum() for k in range(N)])
    w_un = np.array([Wab[k, UNINTENDED[k]].sum() for k in range(N)])
    say(f"- what the fabric adds that the instance did not ask for: every site also receives the {int(UNINTENDED[0].sum())} "
        f"couplings of the diagonal and far classes, all excitatory and none behind an aperture, and in coupling "
        f"units they sum to **{ratio.mean():.2f}×** its intended fan in (from {ratio.min():.2f}× to {ratio.max():.2f}× "
        "across the sites). In weight units the imbalance is worse, because Way B closes most intended bonds "
        f"to their targets while the unintended couplings stay wide open: a site's unintended weight sums to "
        f"{w_un.mean():.1f} against an intended magnitude of {w_in.mean():.1f}, **{(w_un/w_in).mean():.1f}×** the "
        "instance, and no choice of scale improves it, since the scale is already the smallest that fits the "
        "strongest bond")
    # the septum as the only inhibitory lever
    srcs = runs["synapse_septum"]["sources"]
    blocked, control = [], []
    for j in srcs:
        _, ia = divmod(j, N_AZ)
        if ia != 0:
            continue
        for kz in range(N_Z):
            k1, k7 = kz * N_AZ + 1, kz * N_AZ + 7
            if G_raw[k1, j] > 0:
                blocked.append(G_sep[k1, j] / G_raw[k1, j])
            if G_raw[k7, j] > 0:
                control.append(G_sep[k7, j] / G_raw[k7, j])
    septum = float(np.mean(blocked))
    say(f"- the only lever against a coupling is the lead septum, measured at {septum:.2f} of the open value across "
        f"the plane it sits in and {np.mean(control):.2f} on the unshielded side; a septum between two sectors halves "
        "the far couplings that cross that plane and halves the intended ring bond that crosses it too, which is "
        "the silence demand of the toy fabric (compiler_results.md) met in glass: the paths overlap, so nothing "
        "in this vessel silences a pair without also dimming its neighbours\n")

    # ---- 2. the law: intended and as built, against the exact one ---------
    say("## 2. The law the vessel samples: intended, as built, and exact\n")
    logZ, marg, mean_E = exact_law(W, b)
    n_events = 4_000_000
    m_int, etr = run_chain(W, b, n_events, SEED)
    tau = integrated_autocorr(etr)
    sweeps = tau / N
    rms_int = float(np.sqrt(((m_int - marg) ** 2).mean()))
    m_ab, etr_ab = run_chain(Wab, b, n_events, SEED + 1)
    # the collar pass: the compiler knows the target law exactly, so it can subtract the mean of the
    # crosstalk from every site's bias (the collar opening is the bias) and leave only its fluctuation
    b_collar = b - np.array([(Wab[k] - W[k]) @ marg for k in range(N)])
    m_col, etr_col = run_chain(Wab, b_collar, n_events, SEED + 2)
    rms_col = float(np.sqrt(((m_col - marg) ** 2).mean()))
    max_col = float(np.abs(m_col - marg).max())
    # the fluctuation the collar cannot remove, against the drive the instance wanted, site by site
    var = marg * (1 - marg)
    fluct = np.sqrt(((Wab - W) ** 2) @ var)            # std of the crosstalk term at each site
    drive = np.sqrt((W ** 2) @ var)                     # std of the intended weighted sum at each site
    say("The lattice has a topology the twin's 8 site instance did not: each ring of 8 couples only to the "
        "next, so the exact Boltzmann law is a transfer matrix over 256 row states along the axis, and the "
        "64 site machine can be checked against its exact law the way the 8 site one was checked against "
        "enumeration.\n")
    say("| run | what the sites see | mean energy | site marginals against the exact law (rms over 64 sites) | worst site |")
    say("|---|---|---|---|---|")
    say(f"| exact (transfer matrix) | the intended instance | {mean_E:.3f} | | |")
    say(f"| twin, {n_events:,} proposals | the intended instance | {etr.mean():.3f} | {rms_int:.4f} | {np.abs(m_int - marg).max():.4f} |")
    say(f"| twin, {n_events:,} proposals | the instance plus the fabric's crosstalk | {etr_ab.mean():.1f} | mean marginal {m_ab.mean():.2f} against {marg.mean():.2f}: saturated | |")
    say(f"| twin, {n_events:,} proposals | the same, with the mean crosstalk taken out of every bias by the collar | {etr_col.mean():.3f} | **{rms_col:.3f}** | **{max_col:.3f}** |")
    say("")
    say(f"- the sampler at 64 sites reproduces its exact law to the counting noise of the run ({rms_int:.4f} rms on "
        f"marginals that span 0 to 1), with an integrated autocorrelation time of **{tau:.0f} proposals, "
        f"{sweeps:.1f} sweeps** of the lattice: the twin's 26 decays per sample at 8 sites were "
        f"{26/8:.1f} sweeps, so the cost of an independent sample in sweeps is unchanged by an eightfold "
        "larger machine")
    say(f"- the same sampler on the as built weights, the instance plus what the fabric adds, does not sample a "
        f"perturbed version of the intended law; it saturates. {int(UNINTENDED[0].sum())} open couplings of mean weight "
        f"{Wab[UNINTENDED].mean():.2f} drive every site to a mean occupancy of {m_ab.mean():.2f} where the instance "
        f"wanted {marg.mean():.2f}, and the energy runs to {etr_ab.mean():.0f} against {mean_E:.1f}. "
        "Way B places the instance and the fabric buries it")
    say(f"- the compiler has one more pass, and it is the collar. The crosstalk is a sum of many weak couplings, so "
        "most of it is a constant the compiler can predict from the target law it already knows exactly, and a "
        "constant drive is a bias, which is the collar opening. Subtracting the mean crosstalk from every site's "
        f"bias leaves only its fluctuation, and that fluctuation is the verdict: site by site, treating the sites as independent, it has a standard "
        f"deviation of {fluct.mean():.1f} in weight units against {drive.mean():.1f} for the drive the instance "
        f"wanted, **{(fluct/drive).mean():.1f}×** the signal, so the sampled marginals still miss the intended law by "
        f"{rms_col:.2f} rms and {max_col:.2f} at the worst site. What the collar cannot remove is what a diffusive "
        "shell costs a nearest neighbour instance after the best compilation available to it, and the rest of "
        "the way is collimation, not arithmetic\n")

    # ---- 3. timing closure ------------------------------------------------
    say("## 3. Timing closure: every weight is a photon rate\n")
    say("A rate coded machine does not hold a weight, it counts one. The current on the synapse from j to k "
        "is at most I_kj = G_kj r_j: the site's interaction rate r_j is the most it can send (one photon out "
        "per interaction, the ceiling; the true fraction is the scatter share of the cell material, below "
        "one), and G_kj is the fraction that arrives and interacts. The precision law then prices the read: "
        "b bits of a rate cost 2^2b counts. With plastic cells the currents use the measured rates as they "
        f"are; with CsI cells the sender interacts {times(csi_ratio)} as often and the receiver catches "
        f"{times(csi_ratio)} as much, both measured, so a CsI coupling carries {times(csi_ratio**2)} the current.\n")
    rows = []
    for label, r, recv in (("plastic cells", r_pl, 1.0), ("CsI cells", r_cs, csi_ratio)):
        I = G * r[None, :] * recv                                    # I[k, j] photons per second from j interacting in k
        ring_I = float(I[CLASS == "ring"].mean())
        axis_I = float(I[CLASS == "axis"].mean())
        fanin = np.array([I[k, np.arange(N) != k].sum() for k in range(N)])
        rows.append((label, ring_I, axis_I, float(fanin.mean()), float(fanin.min())))
    say("| cells | ring bond current (photons/s) | axial bond current | fan in per site, mean (min) | "
        + " | ".join(f"read the fan in to {bb} bits" for bb in BITS) + " |")
    say("|---|---|---|---|" + "---|" * len(BITS))
    for label, ring_I, axis_I, fan_m, fan_min in rows:
        say(f"| {label} | {ring_I:.3g} | {axis_I:.3g} | {fan_m:.3g} ({fan_min:.3g}) | "
            + " | ".join(hms(2 ** (2 * bb) / fan_m) for bb in BITS) + " |")
    say("")
    _, ring_pl, _, fan_pl, _ = rows[0]
    _, ring_cs, _, fan_cs, _ = rows[1]
    say(f"- a nearest neighbour bond carries **{ring_pl:.3g} photons per second** with plastic cells and "
        f"**{ring_cs:.3g}** with CsI: one photon every {hms(1/ring_pl)} and every {hms(1/ring_cs)}. Reading that "
        f"single weight to 4 bits takes {hms(2**8/ring_pl)} and {hms(2**8/ring_cs)}; to 8 bits, "
        f"{hms(2**16/ring_pl)} and {hms(2**16/ring_cs)}")
    say(f"- the recurrence loop of the transistor note (count the fan in for T_loop = 2^2b / r, then reset the "
        f"aperture to σ(u)) runs at T_loop = {hms(2**8/fan_cs)} per site at 4 bits with CsI cells and "
        f"{hms(2**8/fan_pl)} with plastic, against the benchtop cell's {hms(BENCHTOP_LOOP_S)}: the sealed vessel "
        f"updates a site {times((2**8/fan_cs)/BENCHTOP_LOOP_S)} more slowly than the cell you could build "
        "this month, because the cell's input is a direct beam and the vessel's is scattered light\n")

    # the throughput as built
    say("### The sample rate as built\n")
    say("Every site integrates its fan in for one loop time and re sets its aperture; a sweep of the twin is "
        f"one loop time of the vessel; an independent sample costs {sweeps:.1f} sweeps (Section 2). The machine "
        f"note priced the vessel from its proposal budget alone, 10⁶ proposals per second at "
        f"{DECAYS_PER_SAMPLE} decays per sample, {PRICED_SAMPLES:,.0f} independent samples per second. The "
        "proposal budget is met with CsI cells (results.md). The synapse budget was never priced, and it binds.\n")
    say("| cells | bits | loop time | independent samples per second, as built | against the priced 38,462 |")
    say("|---|---|---|---|---|")
    asbuilt = {}
    for label, _, _, fan_m, _ in rows:
        for bb in BITS:
            T_loop = 2 ** (2 * bb) / fan_m
            spr = 1.0 / (sweeps * T_loop)
            asbuilt[(label, bb)] = spr
            say(f"| {label} | {bb} | {hms(T_loop)} | {rate(spr)} | {times(PRICED_SAMPLES/spr)} short |")
    say("")
    short_cs4 = PRICED_SAMPLES / asbuilt[("CsI cells", 4)]
    short_pl4 = PRICED_SAMPLES / asbuilt[("plastic cells", 4)]
    say(f"The vessel as built draws about **{rate(asbuilt[('CsI cells', 4)])} independent samples per second** with "
        f"CsI cells at 4 bit weights, {sci(short_cs4)} short of the figure the machine note printed, and "
        f"{rate(asbuilt[('plastic cells', 4)])} per second with plastic, {sci(short_pl4)} short. The currents are ceilings, "
        "so every rate in the table is a ceiling too. It is proposal "
        "rich and synapse poor: a gigabecquerel makes a million proposals a second and delivers a few "
        "hundred synapse photons a second to each site, and the sampler runs at the pace of the second "
        "number. The 26 decays per sample of the twin counted proposals and assumed the weighted sum was "
        "known at each one; in the vessel the weighted sum is the slow part.\n")

    # ---- 4. the ladder --------------------------------------------------
    say("## 4. The ladder: measured levers between the vessel as built and the vessel as priced\n")
    omega_touch = 1.0 / 6.0                                   # a face of a cube touching its neighbour
    geom = omega_touch / omega["ring"]
    ladder = [("as built, plastic cells, 4 bits", asbuilt[("plastic cells", 4)], "the measured fabric and rates"),
              ("CsI cells at both ends", asbuilt[("CsI cells", 4)], f"{times(csi_ratio)} measured on each end; the receiver at its ceiling"),
              ("cells packed face to face", asbuilt[("CsI cells", 4)] * geom,
               f"solid angle from {sci(omega['ring'])} to 1/6 of 4π: {times(geom)} by geometry"),
              ("a terabecquerel core (industrial licence)", asbuilt[("CsI cells", 4)] * geom * 1e3,
               "activity ×1,000: the source row of the ENIAC ledger, SCALING.md"),
              ("priced in the machine note", PRICED_SAMPLES, "the proposal budget at 26 decays per sample")]
    say("| rung | independent samples per second | the lever |")
    say("|---|---|---|")
    for name, r_, lever in ladder:
        say(f"| {name} | {rate(r_)} | {lever} |")
    say("")
    say(f"Two of the four rungs are already measured in this repository and the other two are geometry and "
        f"licensing: with CsI cells packed face to face and a terabecquerel core the vessel reaches up to "
        f"{ladder[3][1]:,.0f} samples per second at 4 bit weights, {ladder[3][1]/PRICED_SAMPLES:.1f}× the "
        "priced figure at the ceiling of the currents, so the machine note's number is within reach of catalogue "
        "levers, on an industrial licence, at 4 bits, with no new physics, and within the factor of a few that "
        "the scatter share of CsI takes off the ceiling. At 8 bits every rung is 256× lower. What the ladder does not contain is a "
        "way to run a nearest neighbour instance without the crosstalk of Section 1: packing the cells "
        "closer raises every coupling class together. The clean synapse wants collimation, the sight "
        "lines of the build note's channel plates, which this vessel's transport did not include and "
        "which the next one should.\n")

    say("## 5. What is not compiled here\n")
    say("Way C, the trim through the wall by SPSA on Poisson counts of the glow, is not run on this vessel "
        "because its observable is not there: the boundary ring reads 24 paddles and 4 CZT pixels, 28 "
        "channels for 64 collar openings and 64 site rates, so the loss the trimmer needs is under "
        "determined by a factor of two before any noise. The toy fabric had a port per weight; the vessel "
        "does not. Giving the mouth enough distinguishable channels to see the shell it is trimming is "
        "the boundary theory's ceiling (theory Section 8.1) turned into a design requirement, and it "
        "belongs to the next vessel.\n")
    say("*The compiler places the instance on the measured fabric and finds the fabric adds as much coupling "
        "as it was asked for; the timing closure finds that every weight is a photon current of order one "
        "per second, so the sealed vessel samples at a fraction of a sample per second where it was priced "
        "at tens of thousands; and the ladder finds the priced figure two measured levers and two "
        "catalogue levers away. Every one of those sentences is a number above.*")

    open(os.path.join(HERE, "compile_results.md"), "w").write("\n".join(OUT) + "\n")
    print("\n".join(OUT[-8:]))
    print("wrote ampoule/compile_results.md")
    figure(G, means, omega, p_int, csi_ratio, marg, m_int, m_ab, m_col, rows, asbuilt, ladder, sweeps)


# ---------------------------------------------------------------------------
def figure(G, means, omega, p_int, csi_ratio, marg, m_int, m_ab, m_col, rows, asbuilt, ladder, sweeps):
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
    fig, ((A, B), (C, D)) = plt.subplots(2, 2, figsize=(13.4, 9.4))

    # A: the fabric is geometry
    classes = ["ring", "axis", "diagonal"]
    om = np.array([omega[c] for c in classes])
    gm = np.array([means[c] for c in classes])
    A.loglog(om, gm, "o", color=BLUE, ms=9, zorder=5, label="measured G, plastic cells")
    A.loglog(om, gm * csi_ratio, "D", color=AMBER, ms=8, zorder=5, label=f"with CsI cells ({csi_ratio:.0f}× measured)")
    xx = np.logspace(-4.2, -0.5, 50)
    A.loglog(xx, xx * p_int, "--", color=BLUE, lw=1.4, label=f"Ω/4π × {p_int:.1%} (2 mm of plastic)")
    A.loglog(xx, xx, "-", color=GREY, lw=1.4, label="Ω/4π: one interaction per photon, the ceiling")
    for c, x, y in zip(classes, om, gm):
        A.annotate(c, xy=(x, y), xytext=(x * 1.25, y * 0.55), fontsize=9, color=INK)
    A.axvline(1 / 6, color=GREEN, ls=":", lw=1.3)
    A.text(1 / 6 * 0.9, 2e-5, "a face of a cell\ntouching its neighbour", color=GREEN, fontsize=8, ha="right")
    A.set_xlabel("solid angle of the receiving face, Ω/4π")
    A.set_ylabel("coupling G_kj (interactions per photon born)")
    A.set_title("A.  The fabric is solid angle times an interaction probability")
    A.legend(frameon=False, fontsize=8, loc="upper left")

    # B: the law, intended vs as built
    B.plot([0, 1], [0, 1], "-", color=GREY, lw=1.2)
    B.plot(marg, m_int, "o", color=GREEN, ms=5, alpha=0.8, label="the intended instance, sampled")
    B.plot(marg, m_ab, "s", color=RED, ms=5, alpha=0.7, label="plus the fabric's crosstalk: saturated")
    B.plot(marg, m_col, "^", color=AMBER, ms=6, alpha=0.8, label="the same, mean crosstalk taken out by the collar")
    B.set_xlim(0, 1); B.set_ylim(0, 1.06)
    B.set_xlabel("exact site marginal ⟨z_k⟩ of the intended law (transfer matrix)")
    B.set_ylabel("marginal the 64 site twin sampled")
    B.set_title(f"B.  The law sampled at 64 sites ({sweeps:.1f} sweeps per independent sample)")
    B.legend(frameon=False, fontsize=8.5, loc="upper left")

    # C: timing closure
    bits = np.arange(2, 11)
    for (label, ring_I, axis_I, fan_m, _), ls in zip(rows, ("--", "-")):
        col = GREY if label.startswith("plastic") else INK
        C.semilogy(bits, 2.0 ** (2 * bits) / fan_m, ls, color=BLUE, lw=2.0, label=f"the fan in of a site, {label}")
        C.semilogy(bits, 2.0 ** (2 * bits) / ring_I, ls, color=RED, lw=2.0, label=f"one ring bond, {label}")
    C.axhline(BENCHTOP_LOOP_S, color=GREEN, ls=":", lw=1.4)
    C.text(2.1, BENCHTOP_LOOP_S * 1.4, "the benchtop cell's loop, 26 ms", color=GREEN, fontsize=8.5)
    for y, lab in ((60, "a minute"), (3600, "an hour"), (86400, "a day"), (365.25 * 86400, "a year")):
        C.axhline(y, color=GREY, lw=0.6)
        C.text(10.2, y * 1.25, lab, color=GREY, fontsize=7.5, ha="right")
    C.set_xlabel("bits of precision in the weight")
    C.set_ylabel("time to read it, 2^2b counts at the synapse current (s)")
    C.set_title("C.  Timing closure: every weight is a photon rate")
    C.legend(frameon=False, fontsize=7.6, loc="upper left")
    C.set_xlim(2, 10.3)

    # D: the ladder
    names = [r[0] for r in ladder]
    vals = [r[1] for r in ladder]
    cols = [RED, AMBER, BLUE, GREEN, GREY]
    y = np.arange(len(vals))[::-1]
    D.barh(y, vals, color=cols, height=0.6)
    D.set_xscale("log")
    D.set_yticks(y); D.set_yticklabels(names, fontsize=8.5)
    for yy, v in zip(y, vals):
        D.text(v * 1.4, yy, f"{rate(v)} /s", va="center", fontsize=8.5)
    D.set_xlim(min(vals) / 5, max(vals) * 60)
    D.set_xlabel("independent samples per second (4 bit weights)")
    D.set_title("D.  The ladder from the vessel as built to the vessel as priced")

    fig.suptitle("Figure 18.  The vessel, compiled", fontsize=13, fontweight="bold", y=1.0)
    fig.tight_layout()
    for ext in ("svg", "png"):
        kw = {"metadata": {"Date": None}} if ext == "svg" else {}
        fig.savefig(os.path.join(FIGS, f"fig18_compiled.{ext}"), bbox_inches="tight", **kw)
    plt.close(fig)
    print("wrote fig18_compiled")


if __name__ == "__main__":
    main()
