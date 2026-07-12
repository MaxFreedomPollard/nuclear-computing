#!/usr/bin/env python3
"""
Isomer screener for the keystone gate criterion.

Screens every nuclear isomer in NUBASE2020 as a candidate memory or
triggered release gate, and evaluates a curated candidate set against the
keystone criterion of the foundational document:

    leak condition          eta = sigma*phi / (sigma*phi + lambda_m) > 1/2
    amplification condition Gamma = beta * eta / C_in > 1

Inputs (cached in gates/data/, downloaded on first run):
  - NUBASE2020 (Kondev, Wang, Huang, Naimi, Audi, Chin. Phys. C45, 030001)
    https://www-nds.iaea.org/amdc/ame2020/nubase_4.mas20.txt
  - IAEA LiveChart decay radiation CSVs (ENSDF derived)
    https://nds.iaea.org/relnsd/v1/data?fields=decay_rads&nuclides=...&rad_types=g

Outputs:
  - gates/isomer_catalog.csv   every isomer with E, t1/2, lambda_m, Jpi, modes
  - gates/candidates.csv       curated candidates with trigger physics
  - gates/candidates.md        the same table, GitHub renderable
  - figures/fig8_isomer_landscape.(svg|png)
"""
import csv
import math
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
FIGS = os.path.join(ROOT, "figures")
os.makedirs(DATA, exist_ok=True)

NUBASE_URL = "https://www-nds.iaea.org/amdc/ame2020/nubase_4.mas20.txt"
LIVECHART = "https://nds.iaea.org/relnsd/v1/data?fields=decay_rads&nuclides={n}&rad_types=g"

YEAR = 31556926.0  # tropical year in seconds, NUBASE convention
UNIT_S = {
    "ys": 1e-24, "zs": 1e-21, "as": 1e-18, "fs": 1e-15, "ps": 1e-12,
    "ns": 1e-9, "us": 1e-6, "ms": 1e-3, "s": 1.0, "m": 60.0, "h": 3600.0,
    "d": 86400.0, "y": YEAR, "ky": 1e3 * YEAR, "My": 1e6 * YEAR,
    "Gy": 1e9 * YEAR, "Ty": 1e12 * YEAR, "Py": 1e15 * YEAR,
    "Ey": 1e18 * YEAR, "Zy": 1e21 * YEAR, "Yy": 1e24 * YEAR,
}


def fetch(url, dest):
    if not os.path.exists(dest):
        print("downloading", url)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            open(dest, "wb").write(resp.read())
    return dest


# ---------------------------------------------------------------------------
# 1. Parse NUBASE2020: every isomer on Earth
# ---------------------------------------------------------------------------
def parse_nubase():
    path = fetch(NUBASE_URL, os.path.join(DATA, "nubase_4.mas20.txt"))
    rows = []
    for line in open(path, encoding="ascii", errors="replace"):
        if line.startswith("#"):
            continue
        A = int(line[0:3])
        zzzi = line[4:8]
        Z, i = int(zzzi[:3]), int(zzzi[3])
        s = line[16:17]
        if i == 0:
            continue                      # ground state
        if s in ("i", "j"):
            continue                      # isobaric analog state, not an isomer
        if s in ("r",):
            continue                      # resonance
        exc = line[42:54].replace("#", " ").strip()
        if not exc:
            continue
        try:
            E_keV = float(exc)
        except ValueError:
            continue
        if E_keV <= 0:
            continue
        t_raw = line[69:78].replace("#", " ").strip()
        unit = line[78:80].strip()
        jpi = line[88:102].strip()
        modes = line[119:209].strip()
        name = line[11:16].strip() + s.strip()
        if t_raw == "stbl":
            t_s = math.inf
        elif t_raw in ("p-unst", "") or unit not in UNIT_S:
            continue
        else:
            try:
                t_s = float(t_raw) * UNIT_S[unit]
            except ValueError:
                continue
        lam = 0.0 if t_s == math.inf else math.log(2) / t_s
        rows.append(dict(nuclide=name, Z=Z, A=A, state_index=i,
                         E_keV=E_keV, t_half_s=t_s, lambda_m_per_s=lam,
                         Jpi=jpi, decay_modes=modes))
    return rows


# ---------------------------------------------------------------------------
# 2. Gamma multiplicity per triggered release, from ENSDF decay radiations
# ---------------------------------------------------------------------------
def gamma_multiplicity(nuclide, parent_E_keV, tol=2.0):
    """Photons emitted per decay of the level at parent_E_keV (ENSDF
    intensities per 100 parent decays, internal conversion already
    excluded from the gamma intensity)."""
    dest = os.path.join(DATA, f"decay_g_{nuclide}.csv")
    try:
        fetch(LIVECHART.format(n=nuclide), dest)
        rows = list(csv.DictReader(open(dest)))
    except Exception as e:                                    # offline fallback
        print(f"  [warn] no decay data for {nuclide}: {e}", file=sys.stderr)
        return None
    total = 0.0
    found = False
    for r in rows:
        try:
            pe = float(r["p_energy"])
            inten = float(r["intensity"])
        except (KeyError, ValueError):
            continue
        if abs(pe - parent_E_keV) <= tol:
            total += inten / 100.0
            found = True
    return total if found else None


# ---------------------------------------------------------------------------
# 3. Curated candidates: measured lifetimes meet literature trigger physics.
#    beta_gamma is computed from ENSDF above where an IT branch exists;
#    trigger status and energies carry their citations with them.
# ---------------------------------------------------------------------------
CANDIDATES = [
    dict(key="229mTh", livechart=None, E_keV=0.008355733,
         t_half_s=1740.0, beta_note="single 8.4 eV quantum",
         beta_gamma=1.0, mech="resonant VUV laser (stimulated pump/dump)",
         E_trig_keV=0.008355733, status="PROVEN trigger (laser, 2024)",
         cite="Nature 633, 63 (2024); PRL 132, 182501 (2024)"),
    dict(key="235mU", livechart=None, E_keV=0.0767,
         t_half_s=26 * 60.0, beta_note="internal conversion only",
         beta_gamma=1.0, mech="electronic environment / electronic bridge",
         E_trig_keV=None, status="no demonstrated trigger",
         cite="NUBASE2020; lifetime is chemistry sensitive"),
    dict(key="93mMo", livechart="93mo", E_keV=2424.89,
         t_half_s=6.85 * 3600, beta_note="ENSDF cascade",
         beta_gamma=None, mech="NEEC through the 4.85 keV gateway",
         E_trig_keV=4.85, status="CONTESTED (claim vs theory gap ~1e9)",
         cite="Nature 554, 216 (2018); PRL 122, 212501 (2019); arXiv 2501.05217"),
    dict(key="178m2Hf", livechart="178hf", E_keV=2446.09,
         t_half_s=31 * YEAR, beta_note="ENSDF cascade incl. 1147 keV chain",
         beta_gamma=None, mech="IGE by keV X rays (claimed)",
         E_trig_keV=10.0, status="CONTESTED, unreproduced",
         cite="Collins et al. PRL 82, 695 (1999); refuted PRL 92, 052504"),
    dict(key="180mTa", livechart=None, E_keV=77.1,
         t_half_s=math.inf, beta_note="depletion feeds beta decay, not a cascade",
         beta_gamma=1.0, mech="photoactivation via gateways at and above 1.01 MeV",
         E_trig_keV=1010.0, status="PROVEN trigger, energy uphill",
         cite="Belic et al. PRL 83, 5242 (1999); PRC 65, 035801 (2002)"),
    dict(key="242mAm", livechart=None, E_keV=48.60, E_release_keV=2.02e5,
         t_half_s=141 * YEAR, beta_note="thermal fission: ~3.3 n + ~8 prompt gamma",
         beta_gamma=11.0, mech="thermal neutron induced fission, sigma_f ~ 6.4 kb",
         E_trig_keV=2.5e-8, status="PROVEN trigger (fission channel)",
         cite="ENDF/B-VIII.0 MT=18; nu-bar ~ 3.26"),
    dict(key="177mLu", livechart="177lu", E_keV=970.18,
         t_half_s=160.4 * 86400, beta_note="ENSDF cascade (21.4% IT branch)",
         beta_gamma=None, mech="proposed photodepletion (high K)",
         E_trig_keV=None, status="no demonstrated trigger",
         cite="ENSDF; depletion proposals in literature"),
    dict(key="108mAg", livechart="108ag", E_keV=109.44,
         t_half_s=438 * YEAR, beta_note="ENSDF cascade (mostly EC branch)",
         beta_gamma=None, mech="none demonstrated",
         E_trig_keV=None, status="storage only",
         cite="ENSDF"),
    dict(key="166mHo", livechart="166ho", E_keV=5.98,
         t_half_s=1200 * YEAR, beta_note="beta decay follows",
         beta_gamma=None, mech="none demonstrated",
         E_trig_keV=None, status="storage only",
         cite="ENSDF"),
    dict(key="137mBa", livechart="137ba", E_keV=661.66,
         t_half_s=2.552 * 60, beta_note="the 662 keV line",
         beta_gamma=None, mech="readout reference (Cs-137 generator)",
         E_trig_keV=None, status="readout workhorse",
         cite="ENSDF"),
    dict(key="99mTc", livechart="99tc", E_keV=142.68,
         t_half_s=6.007 * 3600, beta_note="the 140 keV line",
         beta_gamma=None, mech="availability reference (Mo-99 generator)",
         E_trig_keV=None, status="most available isomer on Earth",
         cite="ENSDF"),
    dict(key="57mFe", livechart=None, E_keV=14.41,
         t_half_s=98.3e-9, beta_note="Mossbauer coherence, not memory",
         beta_gamma=1.0, mech="nuclear forward scattering (coherent, directional)",
         E_trig_keV=14.41, status="Tier 2 interconnect reference",
         cite="routine at ESRF ID18 / APS 3-ID"),
]

# Reference gain gates that are not isomers: the proven keystone at scale.
REFERENCE_GATES = [
    dict(key="235U (n_th, f)", E_keV=2.02e5,
         t_half_s=7.04e8 * YEAR, beta_gamma=9.4,
         beta_note="nu-bar 2.43 neutrons + ~7 prompt gamma",
         mech="thermal neutron induced fission, sigma_f = 585 b",
         E_trig_keV=2.5e-8, status="PROVEN, tabulated to 4 digits",
         cite="ENDF/B-VIII.0"),
    dict(key="9Be (n, 2n)", E_keV=None,
         t_half_s=math.inf, beta_gamma=2.0,
         beta_note="2 neutrons out per fast neutron in",
         mech="threshold reaction, E_n > 1.85 MeV, sigma ~ 0.5 b",
         E_trig_keV=1850.0, status="PROVEN (standard reflector physics)",
         cite="ENDF/B-VIII.0"),
]


def build():
    isomers = parse_nubase()
    print(f"NUBASE2020: {len(isomers)} isomeric states parsed")

    with open(os.path.join(HERE, "isomer_catalog.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(isomers[0].keys()))
        w.writeheader()
        for r in isomers:
            r = dict(r)
            if r["t_half_s"] == math.inf:
                r["t_half_s"] = "stable"
            w.writerow(r)

    n_1s = sum(1 for r in isomers if r["t_half_s"] >= 1.0)
    n_1d = sum(1 for r in isomers if r["t_half_s"] >= 86400.0)
    n_hot = sum(1 for r in isomers
                if r["t_half_s"] >= 86400.0 and r["E_keV"] >= 100.0)
    print(f"  half life >= 1 s      : {n_1s}   (usable as registers)")
    print(f"  half life >= 1 day    : {n_1d}   (nonvolatile storage)")
    print(f"  >= 1 day and >= 100 keV: {n_hot}  (stored energy for gain)")

    # multiplicities from ENSDF where an IT branch exists
    for c in CANDIDATES:
        if c["beta_gamma"] is None and c["livechart"]:
            m = gamma_multiplicity(c["livechart"], c["E_keV"])
            if c["key"] == "178m2Hf" and m is not None:
                m_chain = gamma_multiplicity(c["livechart"], 1147.416) or 0.0
                m += m_chain          # the m2 release also drains the m1 band
            c["beta_gamma"] = round(m, 2) if m is not None else None

    # leverage = energy released per trigger quantum spent (the release is
    # the stored excitation unless a larger channel opens, e.g. fission)
    for c in CANDIDATES + REFERENCE_GATES:
        E_rel = c.get("E_release_keV") or c.get("E_keV")
        if c.get("E_trig_keV") and E_rel:
            c["leverage"] = round(E_rel / c["E_trig_keV"], 3)
        else:
            c["leverage"] = None

    cols = ["key", "E_keV", "t_half_s", "beta_gamma", "beta_note",
            "mech", "E_trig_keV", "leverage", "status", "cite"]
    with open(os.path.join(HERE, "candidates.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for c in CANDIDATES + REFERENCE_GATES:
            r = dict(c)
            if r["t_half_s"] == math.inf:
                r["t_half_s"] = "stable"
            w.writerow(r)

    # GitHub renderable table
    def fmt_t(t):
        if t == math.inf:
            return "stable"
        for unit, sec in [("y", YEAR), ("d", 86400), ("h", 3600),
                          ("min", 60), ("s", 1), ("ms", 1e-3),
                          ("us", 1e-6), ("ns", 1e-9)]:
            if t >= sec:
                return f"{t/sec:.3g} {unit}"
        return f"{t:.2e} s"

    with open(os.path.join(HERE, "candidates.md"), "w") as f:
        f.write("| state | E stored | t1/2 | lambda_m (1/s) | beta (gamma/release)"
                " | trigger mechanism | E trigger | leverage | status |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for c in CANDIDATES + REFERENCE_GATES:
            lam = ("0" if c["t_half_s"] == math.inf
                   else f"{math.log(2)/c['t_half_s']:.2e}")
            E = f"{c['E_keV']:.6g} keV" if c.get("E_keV") else "(binding energy)"
            Et = f"{c['E_trig_keV']:.4g} keV" if c.get("E_trig_keV") else ""
            lev = f"{c['leverage']:g}" if c.get("leverage") else ""
            beta = f"{c['beta_gamma']:g}" if c.get("beta_gamma") else "?"
            f.write(f"| {c['key']} | {E} | {fmt_t(c['t_half_s'])} | {lam} "
                    f"| {beta} | {c['mech']} | {Et} | {lev} | {c['status']} |\n")
    print("wrote isomer_catalog.csv, candidates.csv, candidates.md")

    make_figure(isomers)
    return isomers


# ---------------------------------------------------------------------------
# 4. The isomer landscape figure
# ---------------------------------------------------------------------------
def make_figure(isomers):
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
    })
    STABLE_X = 1e19            # plotting position for stable isomers
    xs, ys = [], []
    for r in isomers:
        t = min(r["t_half_s"], STABLE_X) if r["t_half_s"] != math.inf else STABLE_X
        xs.append(t)
        ys.append(r["E_keV"])
    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    ax.scatter(xs, ys, s=7, color=GREY, alpha=0.35, lw=0,
               label=f"all {len(isomers)} NUBASE2020 isomers")
    marks = [
        ("²²⁹ᵐTh", 1740, 0.008356, BLUE, "laser proven, β≈1"),
        ("²³⁵ᵐU", 26 * 60, 0.0767, BLUE, "76.7 eV, IC only"),
        ("⁹³ᵐMo", 6.85 * 3600, 2424.89, AMBER, "NEEC contested"),
        ("¹⁷⁸ᵐ²Hf", 31 * YEAR, 2446.09, RED, "β≈12.4, trigger unproven"),
        ("¹⁸⁰ᵐTa", STABLE_X, 77.1, GREEN, "photodepletion proven"),
        ("²⁴²ᵐAm", 141 * YEAR, 48.6, PURPLE, "fission trigger proven"),
        ("⁹⁹ᵐTc", 6.007 * 3600, 142.68, GREY, ""),
        ("¹⁷⁷ᵐLu", 160.4 * 86400, 970.18, GREY, ""),
    ]
    for name, t, E, c, note in marks:
        ax.scatter([t], [E], s=90, color=c, zorder=5,
                   edgecolor="white", lw=1.2)
        label = f"{name}" + (f"\n{note}" if note else "")
        ax.annotate(label, xy=(t, E), xytext=(t * 3.5, E * 1.5),
                    fontsize=8, color=c, fontweight="bold")
    ax.axvspan(1.0, STABLE_X * 3, ymin=0, ymax=1, color=GREEN, alpha=0.03)
    ax.axvline(1.0, color=GREEN, ls="--", lw=1)
    ax.text(2.2, 2.2e4, "holds a bit for >= 1 s", fontsize=8.5, color=GREEN)
    ax.axhline(100, color=AMBER, ls=":", lw=1)
    ax.text(3e-9, 130, "stored energy >= 100 keV: amplifier fuel",
            fontsize=8.5, color=AMBER)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e-9, STABLE_X * 40)
    ax.set_ylim(3e-3, 4e4)
    ax.set_xlabel("isomer half life  (s;  right edge = stable)")
    ax.set_ylabel("stored excitation energy  (keV)")
    ax.set_title("Every isomer on Earth, as a candidate register or gate")
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    fig.tight_layout()
    for ext in ("svg", "png"):
        fig.savefig(os.path.join(FIGS, f"fig8_isomer_landscape.{ext}"),
                    bbox_inches="tight")
    plt.close(fig)
    print("wrote fig8_isomer_landscape")


if __name__ == "__main__":
    build()
