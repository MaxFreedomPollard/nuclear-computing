# /transport: the routine gates, demonstrated

`gate_demos.py` makes the document's "routine" claims empirical in about two seconds of pure Python (numpy only), regenerating `results.md` on each run:

1. **Coincidence AND is a multiplier.** Output rate tracks the exact survival form $r_2(1 - e^{-2\tau_w r_1})$ to 0.4 percent across the full input grid, including the saturation correction the leading order form misses at high rates, and a thresholded readout reproduces the AND truth table exactly.
2. **Absorption NOT.** Thinning survival encodes the complement $1-p$ to four decimal places.
3. **The Green's function is a weight matrix.** A 24 by 24 cell scattering medium with one absorbing block yields a measured 4 by 4 port matrix $\mathcal{G}$; the block suppresses the middle weights (geometry writes the weights, absorbers write inhibition), and superposition holds to 0.6 percent, confirming that transport is linear while cross sections are frozen.
4. **Saturable resonance is the free sigmoid.** The soft threshold $T(\phi)$ matches its model at every drive level: the neuron of the stochastic tier, available with no keystone physics.
5. **Bernstein feed forward universality.** A circuit of thinning, coincidence, and MUX alone evaluates a nonlinear function of its input rate, matching its Bernstein polynomial to counting noise (0.0012) while the polynomial converges to the target as $1/n$ exactly as the theorem in THEORY.md Section 6 requires. Function approximation does not wait on the keystone.

For engineering geometries (real cross sections, real materials, coupled neutron and photon transport, the subcritical gate of the theory document) the same measurements should be repeated in **OpenMC** (openmc.org: open source, ENDF/B data, Python API); these demonstrations are deliberately dependency free so that every claim can be checked anywhere first.

```
python3 gate_demos.py
```
