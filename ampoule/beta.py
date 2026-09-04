#!/usr/bin/env python3
# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""
The beta spectra of the ampoule's core, ⁹⁰Sr and its daughter ⁹⁰Y, from the
Fermi theory with the shape factor both decays require.

Both are unique first forbidden transitions (0⁺ → 2⁻ and 2⁻ → 0⁺), whose
spectrum is the allowed one times the shape factor p² + q² (electron and
neutrino momenta). The Fermi function is the standard nonrelativistic
Coulomb correction with the relativistic exponent, adequate here to about
a percent, which is far below what the bremsstrahlung yield needs. The
check is the mean energy: the tabulated values are 195.8 keV for ⁹⁰Sr and
933.6 keV for ⁹⁰Y (ICRP 107), and the spectra built here must reproduce
them.

Used by model.py as tabular source distributions; run directly to print
the check.
"""
import math

import numpy as np

ME_KEV = 510.99895                # electron rest energy, keV
ALPHA = 1.0 / 137.035999          # fine structure constant

# endpoint kinetic energy (keV), daughter Z, tabulated mean (keV, ICRP 107)
BRANCHES = {
    "90Sr": dict(Q=546.0, Z=39, mean_ref=195.8),
    "90Y":  dict(Q=2280.1, Z=40, mean_ref=933.6),
}


def fermi_simple(Z, T):
    """The nonrelativistic Fermi function 2πη/(1 − e^(−2πη)) with a first
    order relativistic correction (p/W)^(2(γ−1)); accurate to a percent for
    Z near 40, which is all the yield calculation can use."""
    W = 1.0 + T / ME_KEV
    p = math.sqrt(W * W - 1.0)
    eta = ALPHA * Z * W / p
    gamma = math.sqrt(1.0 - (ALPHA * Z) ** 2)
    f = 2.0 * math.pi * eta / (1.0 - math.exp(-2.0 * math.pi * eta))
    return f * (2.0 * p) ** (2.0 * (gamma - 1.0))


def spectrum(name, n=400):
    """Kinetic energy grid (keV) and normalised probability per bin for the
    named branch, on a linear grid from 0 to the endpoint."""
    b = BRANCHES[name]
    Q, Z = b["Q"], b["Z"]
    T = np.linspace(0.0, Q, n + 1)
    Tm = 0.5 * (T[1:] + T[:-1])
    W = 1.0 + Tm / ME_KEV
    p = np.sqrt(W * W - 1.0)                       # electron momentum, m_e c
    q = (Q - Tm) / ME_KEV                           # neutrino momentum, m_e c
    F = np.array([fermi_simple(Z, t) for t in Tm])
    shape = p * p + q * q                           # unique first forbidden
    N = F * p * W * q * q * shape
    N /= N.sum()
    return T, Tm, N


def mean_energy(name):
    T, Tm, N = spectrum(name)
    return float((Tm * N).sum())


if __name__ == "__main__":
    for name, b in BRANCHES.items():
        m = mean_energy(name)
        print(f"{name}: endpoint {b['Q']:.1f} keV, mean {m:.1f} keV, tabulated {b['mean_ref']:.1f} keV, "
              f"difference {100*(m/b['mean_ref']-1):+.2f} percent")
