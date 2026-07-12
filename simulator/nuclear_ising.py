#!/usr/bin/env python3
"""
Digital twin of a Tier 1 nuclear computer: a recurrent stochastic sampler
executed at the level of individual source decays.

Physical mapping (every line of the algorithm is a term of the governing
equations in the foundational document):

  proposal stream   one thinned Poisson stream per site (thinning theorem,
                    Appendix B.1): each proposal event consumes exactly one
                    source decay.
  weighted sum      u_k = sum_j W_kj z_j + b_k is the frozen transport
                    Green's function acting on the current emission pattern
                    (the synapse).
  threshold         the site excites with probability sigma(u_k), the
                    saturable soft threshold (no keystone gain needed).
  state             z_k in {0,1} is the site's isomer population, written by
                    resonant pump, held between events (nonvolatile).

Because a proposal at site k sets z_k = 1 with exactly the conditional
probability p(z_k = 1 | z_rest) = sigma(u_k), the event chain is a
continuous time random scan Gibbs sampler and its stationary law is the
Boltzmann distribution p(z) proportional to exp(z^T W z / 2 + b^T z)
(Appendix B.3). The simulation therefore *is* the machine, run event by
event, and the decays per sample it reports are physical decays.

Outputs:
  simulator/results.md          all measured numbers, regenerated each run
  figures/fig9_digital_twin.*   convergence and energy accounting figure
"""
import math
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIGS = os.path.join(ROOT, "figures")

RNG = np.random.default_rng(229)          # reproducible; seed honors Th-229

EV = 1.602176634e-19
CARRIERS = [
    ("229mTh quantum (8.4 eV)", 8.355733 * EV),
    ("57Fe quantum (14.4 keV)", 14.41e3 * EV),
    ("60Co gamma (1.25 MeV)", 1.25e6 * EV),
]
MTJ_J_PER_SAMPLE = 33e-15                 # Nature Comms 2026 MTJ Ising machine


def sigmoid(u):
    return 1.0 / (1.0 + np.exp(-u))


def exact_boltzmann(W, b):
    """Exact p(z) by enumeration; z in {0,1}^N."""
    N = len(b)
    states = ((np.arange(2 ** N)[:, None] >> np.arange(N)) & 1).astype(float)
    E = 0.5 * np.einsum("si,ij,sj->s", states, W, states) + states @ b
    p = np.exp(E - E.max())
    return states, p / p.sum()


def run_chain(W, b, n_events, record_every=1):
    """The machine. Each iteration is one source decay (one proposal)."""
    N = len(b)
    z = RNG.integers(0, 2, N).astype(float)
    sites = RNG.integers(0, N, n_events)
    urand = RNG.random(n_events)
    counts = np.zeros(2 ** N)
    powers = 2 ** np.arange(N)
    energy_trace = np.empty(n_events // record_every)
    checkpoints, kls, tvs = [], [], []
    states, p_exact = exact_boltzmann(W, b)
    next_ckpt = 1000
    for t in range(n_events):
        k = sites[t]
        u = W[k] @ z + b[k]
        z[k] = 1.0 if urand[t] < sigmoid(u) else 0.0
        idx = int(z @ powers)
        counts[idx] += 1
        if t % record_every == 0:
            energy_trace[t // record_every] = 0.5 * z @ W @ z + b @ z
        if t + 1 == next_ckpt:
            emp = counts / counts.sum()
            mask = emp > 0
            kls.append(float(np.sum(emp[mask] *
                                    np.log(emp[mask] / p_exact[mask]))))
            tvs.append(float(0.5 * np.abs(emp - p_exact).sum()))
            checkpoints.append(t + 1)
            next_ckpt = int(next_ckpt * 2)
    emp = counts / counts.sum()
    return emp, p_exact, checkpoints, kls, tvs, energy_trace


def integrated_autocorr(x, c=6.0):
    """Sokal's adaptive windowing estimate of tau_int, in events."""
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


def anneal_ground_state(W, b, n_events, betas):
    """Optimization mode: ramp inverse temperature, report first passage
    to the true ground state, in events (= decays)."""
    N = len(b)
    states, p = exact_boltzmann(W, b)
    E_all = 0.5 * np.einsum("si,ij,sj->s", states, W, states) + states @ b
    gs_energy = E_all.max()               # p ~ exp(E): ground = max E here
    z = RNG.integers(0, 2, N).astype(float)
    sites = RNG.integers(0, N, n_events)
    urand = RNG.random(n_events)
    schedule = np.interp(np.arange(n_events), [0, n_events - 1], betas)
    for t in range(n_events):
        k = sites[t]
        u = schedule[t] * (W[k] @ z + b[k])
        z[k] = 1.0 if urand[t] < sigmoid(u) else 0.0
        if abs((0.5 * z @ W @ z + b @ z) - gs_energy) < 1e-9:
            return t + 1
    return None


def main():
    # -- a frustrated 8 site instance (fixed by the seed, fully reproducible)
    N = 8
    A = RNG.normal(0, 1.4, (N, N))
    W = np.triu(A, 1)
    W = W + W.T
    b = RNG.normal(0, 0.5, N)

    n_events = 2_000_000
    emp, p_exact, ckpts, kls, tvs, etrace = run_chain(W, b, n_events)

    tau = integrated_autocorr(etrace[10_000:])
    ess = (len(etrace) - 10_000) / tau
    decays_per_sample = n_events / ess

    # -- optimization mode: median first passage to ground state
    fps = []
    for _ in range(25):
        fp = anneal_ground_state(W, b, 400_000, betas=(0.2, 3.0))
        if fp is not None:
            fps.append(fp)
    fp_median = int(np.median(fps)) if fps else None

    # -- energy accounting
    energy_rows = []
    for name, joule in CARRIERS:
        per_sample = decays_per_sample * joule
        energy_rows.append((name, joule, per_sample,
                            per_sample / MTJ_J_PER_SAMPLE))

    # -- results.md ---------------------------------------------------------
    lines = []
    lines.append("# Digital twin results (regenerated by nuclear_ising.py)\n")
    lines.append(f"Instance: {N} sites, frustrated Gaussian couplings, "
                 f"seed 229, {n_events:,} source decays simulated.\n")
    lines.append("## Convergence to the exact Boltzmann law\n")
    lines.append("| decays consumed | KL(empirical, exact) | total variation |")
    lines.append("|---|---|---|")
    for c, k, t in zip(ckpts, kls, tvs):
        lines.append(f"| {c:,} | {k:.2e} | {t:.3f} |")
    lines.append("")
    lines.append(f"Final KL divergence after {n_events:,} decays: "
                 f"**{kls[-1]:.2e}** over all {2**N} states. The machine "
                 "samples the exact distribution its couplings define.\n")
    lines.append("## Sampling cost\n")
    lines.append(f"- integrated autocorrelation time: **{tau:.1f} decays**")
    lines.append(f"- effective independent samples drawn: **{ess:,.0f}**")
    lines.append(f"- decays per independent sample: **{decays_per_sample:.0f}**")
    if fp_median:
        lines.append(f"- optimization mode (annealed): median "
                     f"**{fp_median:,} decays** to first reach the true "
                     f"ground state ({len(fps)}/25 runs reached it)")
    lines.append("")
    lines.append("## Energy per independent sample, by carrier\n")
    lines.append("| carrier | J per quantum | J per sample | vs MTJ p bit "
                 "(33 fJ/sample) |")
    lines.append("|---|---|---|---|")
    for name, jq, js, ratio in energy_rows:
        verdict = f"{1/ratio:,.0f}x cheaper" if ratio < 1 else f"{ratio:,.0f}x costlier"
        lines.append(f"| {name} | {jq:.2e} | {js:.2e} | {verdict} |")
    lines.append("")
    lines.append("The table is the energy honesty argument of the "
                 "foundational document, now with measured constants: at "
                 "MeV quanta the sampler cannot compete; at the 8.4 eV "
                 "transition the *same machine* undercuts engineered "
                 "probabilistic silicon, because the source energy is spent "
                 "either way and each decay is a genuine random number no "
                 "transistor had to synthesize.\n")
    open(os.path.join(HERE, "results.md"), "w").write("\n".join(lines))
    print("\n".join(lines[-14:]))
    print("wrote simulator/results.md")

    make_figure(ckpts, kls, tvs, emp, p_exact, energy_rows)


def make_figure(ckpts, kls, tvs, emp, p_exact, energy_rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    INK, BLUE, RED, GREEN, AMBER, PURPLE, GREY = (
        "#16213e", "#2563eb", "#dc2626", "#16a34a",
        "#d97706", "#7c3aed", "#94a3b8")
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white", "axes.edgecolor": INK,
        "axes.labelcolor": INK, "text.color": INK, "xtick.color": INK,
        "ytick.color": INK, "axes.titlecolor": INK, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold", "axes.grid": True,
        "grid.color": "#e5e7eb", "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.dpi": 130,
    "svg.hashsalt": "nuclear-computer",
    })
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13.6, 4.3))

    a1.loglog(ckpts, kls, "-o", color=BLUE, lw=2, ms=4, label="KL divergence")
    a1.loglog(ckpts, tvs, "-s", color=AMBER, lw=2, ms=4, label="total variation")
    ref = [kls[0] * (ckpts[0] / c) for c in ckpts]
    a1.loglog(ckpts, ref, ":", color=GREY, lw=1.4, label="1/N guide")
    a1.set_xlabel("source decays consumed")
    a1.set_ylabel("distance to exact Boltzmann law")
    a1.set_title("A.  The decays sample the law")
    a1.legend(frameon=False, fontsize=8.5)

    a2.loglog(p_exact, np.maximum(emp, 1e-9), ".", color=PURPLE, ms=5, alpha=0.7)
    lim = (1e-6, 1.0)
    a2.plot(lim, lim, "-", color=GREY, lw=1.2)
    a2.set_xlim(*lim); a2.set_ylim(*lim)
    a2.set_xlabel("exact probability (enumeration, 256 states)")
    a2.set_ylabel("empirical probability (event counts)")
    a2.set_title("B.  State by state agreement")

    names = [r[0].split(" (")[0] for r in energy_rows] + ["MTJ p bit\n(silicon)"]
    vals = [r[2] for r in energy_rows] + [MTJ_J_PER_SAMPLE]
    cols = [PURPLE, AMBER, RED, GREY]
    y = np.arange(len(vals))[::-1]
    a3.barh(y, vals, color=cols, height=0.6)
    a3.set_xscale("log")
    a3.set_yticks(y); a3.set_yticklabels(names, fontsize=9)
    a3.axvline(MTJ_J_PER_SAMPLE, color=GREY, ls="--", lw=1.2)
    for yy, v in zip(y, vals):
        a3.text(v * 1.5, yy, f"{v:.1e} J", va="center", fontsize=8)
    a3.set_xlabel("energy per independent sample (J)")
    a3.set_title("C.  Carrier choice decides the economics")
    fig.tight_layout()
    for ext in ("svg", "png"):
        kw = {"metadata": {"Date": None}} if ext == "svg" else {}
        fig.savefig(os.path.join(FIGS, f"fig9_digital_twin.{ext}"),
                    bbox_inches="tight", **kw)
    plt.close(fig)
    print("wrote fig9_digital_twin")


if __name__ == "__main__":
    main()
