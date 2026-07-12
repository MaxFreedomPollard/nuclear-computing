# /simulator: the digital twin

`nuclear_ising.py` is a Tier 1 nuclear computer executed decay by decay in software. Every step of the algorithm is a term of the governing equations: proposal events are thinned Poisson streams (one source decay each), the weighted sum $u_k = \sum_j W_{kj} z_j + b_k$ is the frozen transport Green's function, the excitation probability $\sigma(u_k)$ is the saturable soft threshold, and the state $z_k$ is an isomer population. No keystone gain is assumed anywhere; this is the machine Phase A of the roadmap proposes to build, run in simulation first.

It measures, and writes to `results.md` on every run:

- **Correctness.** The empirical distribution over all $2^8$ states against the exact Boltzmann law by enumeration: KL divergence falls as $1/N$ to a few times $10^{-4}$ after two million decays. The medium samples the distribution its geometry defines; this is the detailed balance argument of Appendix B.3 made empirical.
- **Sampling cost.** Integrated autocorrelation time of about 26 decays per independent sample on a frustrated 8 site instance, and a median of 173 decays to reach the true ground state in annealed optimization mode.
- **Energy economics.** Decays per sample times energy per quantum, per carrier, against the 33 fJ/sample of the magnetic tunnel junction Ising machine (Nature Communications 2026): about 945 times cheaper at the 8.4 eV ²²⁹Th transition, about 2 times costlier at 14.4 keV, about 158 times costlier at 1.25 MeV. The carrier decides the economics; the architecture is the same.

This settles the *simulation* half of kill criterion A affirmatively: a native radiation sampler matches probabilistic silicon sample for sample, and beats it on energy iff the low energy transition carries the traffic. The remaining half of Phase A is hardware.

Run it (about 10 seconds):

```
python3 nuclear_ising.py
```

Requires `numpy`; `matplotlib` for the figure.
