# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""The instruments, checked against things that are not themselves: the beta
spectra against their tabulated means, the transfer matrix against brute
force enumeration, the sampler against its exact law, the degree checker
against the theorem, the adjoint Jacobian against finite differences, and
the committed fission matrix against the committed eigenvalue."""
import json
import os

import numpy as np
import pytest

from conftest import ROOT, load_script


def test_beta_spectra_reproduce_the_icrp_107_mean_energies():
    beta = load_script("ampoule/beta.py")
    for name, b in beta.BRANCHES.items():
        m = beta.mean_energy(name)
        assert abs(m / b["mean_ref"] - 1) < 0.03, f"{name}: {m:.1f} keV against {b['mean_ref']} keV"   # the script's own stated accuracy, about a percent, and far inside what the yield needs


def test_transfer_matrix_marginals_match_brute_force_on_two_rings():
    c = load_script("ampoule/compile.py")
    c.N_Z, c.N = 2, 16                     # the exact law reads the lattice size from the module
    rng = np.random.default_rng(7)
    W = np.zeros((16, 16))
    for j in range(16):
        for k in range(j + 1, 16):
            if c.coupling_class(j, k) in ("ring", "axis"):
                W[j, k] = W[k, j] = rng.normal(0, 1.4)
    b = rng.normal(0, 0.5, 16)
    logZ, marg, mean_E = c.exact_law(W, b)
    states = ((np.arange(2 ** 16)[:, None] >> np.arange(16)) & 1).astype(float)
    E = 0.5 * np.einsum("si,ij,sj->s", states, W, states) + states @ b
    p = np.exp(E - E.max())
    Z = p.sum()
    p /= Z
    assert abs(logZ - (np.log(Z) + E.max())) < 1e-9
    assert np.abs(states.T @ p - marg).max() < 1e-9
    assert abs(mean_E - (E * p).sum()) < 1e-5


def test_the_sampler_converges_to_its_exact_boltzmann_law():
    twin = load_script("simulator/nuclear_ising.py")
    rng = np.random.default_rng(3)
    N = 5
    A = rng.normal(0, 1.2, (N, N))
    W = np.triu(A, 1)
    W = W + W.T
    b = rng.normal(0, 0.4, N)
    emp, p_exact, ckpts, kls, tvs, _ = twin.run_chain(W, b, 300_000)
    assert kls[-1] < 2e-3, f"KL divergence {kls[-1]:.2e} after {ckpts[-1]:,} decays"


def test_the_degree_checker_flags_and_repairs_an_inhomogeneous_comparison():
    dc = load_script("transport/degree_check.py")
    left = dc.AND(dc.THIN(0.8), dc.THIN(0.9))
    right = dc.THIN(0.5)
    dA, dB, flags = dc.check_comparator(left, right)
    assert (dA, dB) == (2, 1) and flags
    fixed = dc.homogenize(right, dA)
    dA2, dB2, flags2 = dc.check_comparator(left, fixed)
    assert dA2 == dB2 == 2 and not flags2
    # the theorem: a like degree comparison is invariant under global scaling of the activity
    for lam in (1e5, 5e4, 2.5e4):
        assert (dc.rate(left, lam) > dc.rate(fixed, lam)) == (dc.rate(left, 1e5) > dc.rate(fixed, 1e5))


def test_the_adjoint_jacobian_matches_finite_differences():
    cd = load_script("transport/compiler_demo.py")
    rng = np.random.default_rng(11)
    s0 = rng.uniform(0.96, 0.999, cd.V)
    G0, phi0, psi0 = cd.transport(s0)
    adj = cd.jacobian_entry(phi0, psi0, 1, 2)
    h = 1e-4
    for v in rng.choice(cd.V, 4, replace=False):
        sp = s0.copy(); sp[v] += h
        sm = s0.copy(); sm[v] -= h
        fd = (cd.transport(sp)[0][1, 2] - cd.transport(sm)[0][1, 2]) / (2 * h)
        assert abs(adj[v] - fd) < 1e-7 * max(abs(fd), 1e-3)


def test_the_committed_fission_matrix_reproduces_the_committed_eigenvalue():
    """Avery's coupling: the dominant eigenvalue of K must land within a few
    hundred pcm of the transport k of the pair, in every absorber state."""
    doc = json.load(open(os.path.join(ROOT, "neutron/tallies.json")))
    runs = doc["runs"]
    for state, coupled in (("open", "coupled_open"), ("cd", "coupled_cd"), ("b4c", "coupled_b4c")):
        K = np.zeros((2, 2))
        for j, tag in enumerate("AB"):
            r = runs[f"coupling_{tag}_{state}"]
            for i, out in enumerate("AB"):
                K[i, j] = r["regions"][out]["nu-fission"][0]
        lam = np.linalg.eigvals(K).real.max()
        k = runs[coupled]["k"][0] if isinstance(runs[coupled]["k"], list) else runs[coupled]["k"]
        assert abs(lam - k) < 0.004, f"{state}: eigenvalue {lam:.4f} against k {k:.4f}"
        assert lam < 1 and k < 1, "everything is subcritical"


def test_the_ampoule_synapse_is_symmetric_and_below_the_solid_angle_ceiling():
    doc = json.load(open(os.path.join(ROOT, "ampoule/tallies.json")))
    G = np.array(doc["runs"]["synapse_open"]["G"])
    c = load_script("ampoule/compile.py")
    lay = doc["provenance"]["site_layout"]
    d_ring = 2 * lay["radius_cm"] * np.sin(np.pi / 8)
    omega_ring = 0.04 / (4 * np.pi * d_ring ** 2)
    ring = G[c.CLASS == "ring"]
    assert 0 < ring.mean() < omega_ring, "a coupling cannot exceed the solid angle of the receiving face"
    big = 0.5 * (G + G.T) > 1e-5
    asym = np.abs(G - G.T)[big] / (0.5 * (G + G.T))[big]
    assert np.median(asym) < 0.5
