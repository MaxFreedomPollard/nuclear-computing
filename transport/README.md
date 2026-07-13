# /transport: the routine gates, demonstrated

`gate_demos.py` makes the document's "routine" claims empirical in about two seconds of pure Python (numpy only), regenerating `results.md` on each run:

1. **Coincidence AND is a multiplier.** Output rate tracks the exact survival form $r_2(1 - e^{-2\tau_w r_1})$ to 0.4 percent across the full input grid, including the saturation correction the leading order form misses at high rates, and a thresholded readout reproduces the AND truth table exactly.
2. **Absorption NOT.** Thinning survival encodes the complement $1-p$ to four decimal places.
3. **The Green's function is a weight matrix.** A 24 by 24 cell scattering medium with one absorbing block yields a measured 4 by 4 port matrix $\mathcal{G}$; the block suppresses the middle weights (geometry writes the weights, absorbers write inhibition), and superposition holds to 0.6 percent, confirming that transport is linear while cross sections are frozen.
4. **Saturable resonance is the free sigmoid.** The soft threshold $T(\phi)$ matches its model at every drive level: the neuron of the stochastic tier, available with no keystone physics.
5. The degree checker ([`degree_check.py`](degree_check.py) writes [`degree_results.md`](degree_results.md)): the design rule tool of theory Section 7.1. It labels every node's coincidence degree, flags unequal degree comparisons, repairs them with reference stages, and demonstrates the stakes by simulation: the defective comparator inverts its decision at half activity, the repaired one never moves.
6. **Bernstein feed forward universality.** A circuit of thinning, coincidence, and MUX alone evaluates a nonlinear function of its input rate, matching its Bernstein polynomial to counting noise (0.0012) while the polynomial converges to the target as $1/n$ exactly as the theorem in THEORY.md Section 6 requires. Function approximation does not wait on the keystone.

7. The compiler ([`compiler_demo.py`](compiler_demo.py) writes [`compiler_results.md`](compiler_results.md), figure 14): the missing assembler, three ways. The adjoint Jacobian of the whole weight matrix (forward flux times importance, the reactor perturbation formula) is verified against finite differences to $9\times10^{-7}$; adjoint descent then compiles a random target to 0.65 percent, a crossbar compiles any target by exact division, and SPSA trims a sealed unit through the wall using only Poisson counts of its glow (theory Section 11).

For engineering geometries (real cross sections, real materials, coupled neutron and photon transport, the subcritical gate of the theory document) the same measurements should be repeated in OpenMC (openmc.org: open source, ENDF/B data, Python API); these demonstrations are deliberately dependency free so that every claim can be checked anywhere first.

```
python3 gate_demos.py
```
