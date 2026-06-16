# Nuclear Computing

**A foundational theoretical framework in which radiation - photons, particles, and nuclear populations - is the computational medium itself.**

The radioactive source is not the data and it is not the logic. It is the *metabolism*: a constant Poisson flux that supplies energy, entropy, and a natural clock. The actual computation is performed by the interactions of that radiation with matter and with itself, mediated by field-dependent nuclear and electromagnetic cross-sections. The central engineering problem - and the central theoretical problem - is the **gate**: a physical interaction whose probability or rate depends on the local radiation field in a controllable, nonlinear way.

This repository is the working home of the theory. It will be filled out with detailed derivations, simulation specifications, and reference implementations. For now, this document establishes the purpose, the model, the gate set, and the case for universality.

---

## 1. What this project is

Nuclear Computing proposes a class of computers in which the state and the processor are the same physical object: a coupled radiation field and nuclear population field evolving under transport and kinetics. The goal is not to use radiation as a random number source, a sensor input, or a power supply for conventional electronics. The goal is to show that radiation, shaped by the right physical gates, can perform nontrivial computation *in the field*.

The name "nuclear computer" is shorthand. The focus is on **compute** - what can be computed, and what physical gates are sufficient - not on any particular device implementation. Implementations will follow once the theory is tight.

**Status of this repository**: early-stage, add-only. Future work is tracked through Issues and delivered through Pull Requests.

---

## 2. The role of the constant radioactive source

A constant radioactive source - for example, a long-lived gamma emitter such as Co-60, or a mixed particle/photon source - produces an unpatterned Poisson stream. That stream has three supporting roles and no executive role.

1. **Metabolism**. It supplies the energy budget of the system. Every absorption, excitation, scattering event, and readout photon is ultimately paid for by decays.
2. **Entropy**. The independent-arrival statistics of a Poisson process provide a native source of physical randomness. This is essential for stochastic and sampling modes.
3. **Clock**. The constant mean rate defines a natural time unit. Because the process has independent increments, any time slice can be treated as an independent trial.

The source does not encode data. Data and programs are written into the system by *thinning*, *routing*, *shielding*, and *modulating cross-sections* - by shaping how the radiation interacts, not by changing the source.

---

## 3. State representation

The computational state is carried by two coupled fields:

- **Photon/radiation field**:  
  \[
  \phi(\mathbf r, \Omega, E, t)
  \]
  describing the occupation of photon and particle modes in space, direction, energy, and time.
- **Nuclear population field**:  
  \[
  n_i(\mathbf r, t)
  \]
  describing the fraction of nuclei in each relevant energy level at position \(\mathbf r\).

A logical "1" corresponds to an occupied mode or an excited isomeric nucleus. A logical "0" corresponds to an empty mode or a nucleus in its ground or nonresponsive state. These binary labels are used because the framework must support digital universality (NAND gates, memory, recurrence) as well as analog universality (continuous function approximation). The underlying physics remains probabilistic, so the binary labels are emergent: they are the result of thresholding continuous rates and populations.

A purely analog/probabilistic mode is also possible, in which values are carried directly as occupation numbers or firing probabilities. That mode is the radiation analog of **p-bit** or **thermodynamic computing**; it is a subset of the framework rather than its only operating regime.

---

## 4. Dynamics: the equations of the computer

All computation is the evolution of the coupled fields. The two governing equations are standard radiation transport and nuclear kinetics; what makes them a computer is the nonlinear coupling between them.

**Photon/particle transport** (linear plus field-dependent terms):
\[
\left(\frac{1}{c}\partial_t + \Omega \cdot \nabla\right) \phi
= -\Sigma_t(\phi, n)\,\phi
+ \int \Sigma_s(\Omega', E' \to \Omega, E; \phi)\,\phi'\, d\Omega' dE'
+ q(n)
\]
where \(\Sigma_t\) is the total macroscopic cross-section, \(\Sigma_s\) is the scattering kernel, and \(q(n)\) is emission from nuclear de-excitation.

**Nuclear kinetics** (the gate layer):
\[
\dot n_m = \sigma_p \phi \cdot n_g - \bigl[\lambda_m + R_{\text{trig}}(\phi_{\text{ctrl}}, n)\bigr] n_m
\]
where \(n_m\) is the population of the metastable isomer, \(n_g\) the ground-state population, \(\sigma_p\) the pump cross-section, \(\lambda_m\) the spontaneous decay rate, and \(R_{\text{trig}}\) the field-triggered release rate. The emitted output is
\[
q \;\propto\; \text{branching} \cdot R_{\text{trig}}(\phi_{\text{ctrl}})\, n_m.
\]

The linear transport operator has a Green's function \(\mathcal G\) that acts as a **weighted-sum/synapse** machine. The nonlinear terms \(\Sigma_t(\phi,n)\) and \(R_{\text{trig}}(\phi)\) are the **gates**.

---

## 5. The gate (the crux of the theory)

A gate is any physical interaction whose rate depends on the local radiation field. The universal primitive has the form
\[
\phi_{\text{out}} = g\left(\sum_j w_j \phi_j\right),
\]
where \(g\) is sigmoidal or hard-thresholded and the weights \(w_j\) are realized by geometry, material composition, resonant absorption, or scattering.

The viability of Nuclear Computing depends on whether a sufficiently rich gate set can be engineered from radiation-matter interactions. The candidate gates below are chosen from real physics. Some are routine; some are frontier experiments. The theory treats all of them as physical hypotheses to be confirmed, not as finished hardware.

### 5.1 AND / multiply (coincidence gate)

Two independent Poisson streams with rates \(\lambda_1\) and \(\lambda_2\) are routed to the same small volume with a resolving time \(\sigma\) (a coincidence aperture). The probability that at least one joint event occurs in an interval \(\Delta t\) is
\[
P_{\text{AND}} = 1 - \exp(-\lambda_1 \lambda_2 \sigma \,\Delta t),
\]
so the output rate is
\[
\lambda_{\text{out}} = \lambda_1 \lambda_2 \sigma.
\]

If values \(x, y \in [0,1]\) are encoded by thinning the source to rates \(x\lambda\) and \(y\lambda\), the output rate is proportional to \(xy\). This is a physical stochastic AND gate. Gamma-gamma coincidence counting is the routine experimental realization.

### 5.2 MUX / add (scattering gate)

Weighted addition is implemented by the linear part of transport. A photon that can be scattered into one of several modes, or routed through a spatial split, produces an output stream whose rate is a convex combination of input rates. The Green's function \(\mathcal G\) of the Boltzmann operator is the continuous analog of a weight matrix. Signed weights can be obtained by push-pull pairs: an excitatory mode on resonance and an inhibitory mode slightly detuned.

### 5.3 NOT / complement (absorption gate)

Logical complement is obtained by detuned or off-resonant absorption. A strong absorber placed in a stream removes a fraction \(p\) of the photons; the surviving stream encodes \(1-p\). By making \(p\) depend on another field, one obtains a controlled NOT.

### 5.4 Threshold / neuron gate (NEEC, IGE, saturable resonance)

The hardest and most powerful gate is a threshold gate with gain. The leading physical candidates are:

- **Nuclear excitation by electron capture (NEEC)** and its inverse **NEET**: a free electron is captured into an atomic shell while its kinetic energy excites the nucleus. NEEC can deplete a long-lived isomer by lifting it to a short-lived gateway state, releasing a cascade of high-energy photons. The rate depends on the local electron/photon flux that creates vacancies, so it is field-controllable. Gunst *et al.*, *Phys. Rev. Lett.* **112**, 082501 (2014), showed that NEEC-triggered isomer depletion can be orders of magnitude more efficient than direct photoexcitation at an XFEL.
- **Induced gamma emission (IGE)**: a resonant gamma photon stimulates emission from a nuclear isomer. Triggered release from isomers such as \(^{178}\mathrm{Hf}^{m2}\), \(^{180}\mathrm{Ta}^{m}\), and \(^{93m}\mathrm{Mo}\) has been studied for decades. The isomer acts as a stored-energy cell; the control photon is the trigger.
- **Saturable resonance**: a material with a resonant cross-section that bleaches at high flux gives a soft sigmoid transmission \(T(\phi) = T_0 + (1-T_0)\,\phi/(\phi+\phi_{\text{sat}})\). It is a weaker gate but easier to arrange than isomeric triggering.

A concrete, room-temperature candidate is the **Th-229 nuclear isomer**. The transition from the ground nuclear state to the metastable state is only ~8.4 eV; Tiedau *et al.*, *Phys. Rev. Lett.* **132**, 182501 (2024), demonstrated direct laser excitation of this transition in Th-doped CaF\(_2\) crystals using tabletop VUV lasers. In the language of Nuclear Computing, the isomer population is a membrane potential; resonant pump is excitatory input; triggered de-excitation is a spike; the isomer lifetime is short-term memory. A room-temperature nuclear neuron is not a fantasy; it is an experimental frontier.

---

## 6. Universality

The gate set above is sufficient for two kinds of universality.

### 6.1 Analog universality

A layer of weighted sums (linear transport, \(\mathcal G\)) followed by a sigmoidal threshold (a saturating or LIF-like gate) is a universal function approximator. For a leaky integrate-and-fire unit driven by Poisson input, the membrane potential becomes an Ornstein-Uhlenbeck process. The first-passage firing rate is given by the **Siegert formula**, a smooth sigmoidal function of the effective input. By the theorems of Cybenko and Hornik, a single hidden layer of such units can approximate any continuous function on a compact set to arbitrary accuracy.

### 6.2 Digital universality

NAND can be constructed from a coincidence gate followed by a high-threshold veto: output is HIGH unless both inputs are simultaneously HIGH. Persistent memory is realized through bistable states, either mutually exciting nuclear/photonic modes or two stable isomeric populations. The Poisson source supplies a clock. NAND + memory + clock is functionally complete and yields Turing-completeness.

---

## 7. Stochastic and sampling computation

In addition to deterministic digital and analog modes, the framework naturally supports stochastic computation.

- **Poisson thinning**: a value \(x\) is encoded as a rate \(x\lambda\). The stream is a sequence of Bernoulli trials when viewed in time slices short enough that multiple events are unlikely.
- **AND = multiply**, via coincidence.
- **MUX = scaled add**, via routing.
- **NOT = complement**, via absorption.

A recurrent arrangement of these gates, with local acceptance probabilities \(\sigma(u_k)\) where \(u_k = \sum_j W_{kj} z_j + b_k\), obeys detailed balance and converges to a stationary distribution
\[
p(\mathbf z) \propto \exp\!\left(\frac{1}{2}\mathbf z^T W \mathbf z + \mathbf b^T \mathbf z\right).
\]
That is a physical Boltzmann machine and a physical Ising sampler.

The precision of any rate estimate is bounded by Poisson statistics. The relative standard deviation of a rate estimate from \(rT\) observed counts is \(1/\sqrt{rT}\). To obtain \(b\) bits of precision requires
\[
rT \ge 2^{2b}.
\]
For example, 8-bit precision requires \(rT \ge 65{,}536\) counts.

---

## 8. Complexity and physical limits

The theory is honest about what it can and cannot claim.

- **Tier 0 - Timing only**: Using decay times as random bits is not computation. It is the service that Fourmilab's HotBits provided until its retirement in 2023: a true random number generator. It sits in BPP and offers no computational advantage over a good pseudorandom source.
- **Tier 1 - Stochastic/p-bit gates**: Coincidence gates and Boltzmann sampling can give practical advantages in Monte Carlo, Bayesian inference, and combinatorial optimization because the randomness and the nonlinearity are native to the medium. They remain in BPP (assuming P = BPP) but may be faster or more energy-efficient for the right problem class.
- **Tier 2 - Quantum degrees of freedom**: The same substrate can host quantum behavior: entangled gamma pairs from positron annihilation, Mössbauer coherence at room temperature, and nuclear spin qubits controlled by gamma or RF fields. This tier reaches BQP - the same class as conventional quantum computers - but potentially with better engineering: no cryogenics, intrinsic radiation hardness, and self-replenishing qubits from the source.

The ceiling is the **extended Church-Turing thesis as applied to quantum mechanics**: no physically realizable machine exceeds BQP. Nuclear Computing does not claim to go beyond quantum computation; it claims a different, and in some respects simpler, physical path to the same frontier.

---

## 9. Honest experimental status

- **Coincidence gates**: routine. Gamma-gamma coincidence is a standard nuclear-instrumentation technique.
- **Saturable/scattering gates**: routine at optical energies; harder but plausible for hard X-rays and gammas.
- **NEEC/IGE triggered release**: theoretically well established, experimentally difficult, and actively pursued. It is the central unsolved engineering hypothesis of the framework.
- **Th-229 laser control**: demonstrated at room temperature in doped crystals (Tiedau *et al.*, 2024). The transition energy is now known to high precision: \(148.3821(5)\) nm, \(2020.409(7)\) THz. This gives a concrete, near-term target for the first nuclear neuron.

---

## 10. The one-line architecture

Source (bias) \(\to\) structured medium (\(\mathcal G\) synapses) \(\to\) field-dependent cross-sections (NEEC / IGE / saturable gates) \(\to\) network relaxes to fixed point or samples \(p \propto e^{E}\). Radiation particles perform the logic through their interactions. The isomer is the native memory element. The photon field is the bus. The radioactive source is the metabolism.

---

## 11. Roadmap and repository structure (future, add-only)

Planned additions, all through Issues paired with Pull Requests:

- `theory/`: full derivations of the gate rate equations and universality proofs.
- `gates/`: candidate material systems, cross-section tables, and design notes.
- `simulations/`: Monte Carlo specs and reference implementations of the core dynamics.
- `references.bib`: curated literature list with verified bibliographic data.

---

## References

1. J. Gunst *et al.*, "Dominant Secondary Nuclear Photoexcitation with the X-Ray Free-Electron Laser," *Phys. Rev. Lett.* **112**, 082501 (2014). [https://doi.org/10.1103/PhysRevLett.112.082501](https://doi.org/10.1103/PhysRevLett.112.082501)
2. J. Tiedau *et al.*, "Laser Excitation of the Th-229 Nucleus," *Phys. Rev. Lett.* **132**, 182501 (2024). [https://doi.org/10.1103/PhysRevLett.132.182501](https://doi.org/10.1103/PhysRevLett.132.182501)
3. "Induced gamma emission," Wikipedia. [https://en.wikipedia.org/wiki/Induced_gamma_emission](https://en.wikipedia.org/wiki/Induced_gamma_emission)
4. "Nuclear excitation by electron capture," APS Physics Viewpoint, February 24, 2014. [https://physics.aps.org/articles/v7/20](https://physics.aps.org/articles/v7/20)
5. Fourmilab HotBits archive. [https://www.fourmilab.ch/hotbits/](https://www.fourmilab.ch/hotbits/)
6. K. Y. Camsari, R. Faria, B. M. Sutton, and S. Datta, "Stochastic p-bits for invertible logic," *Phys. Rev. X* **7**, 031014 (2017).
7. G. Cybenko, "Approximation by superpositions of a sigmoidal function," *Math. Control Signals Syst.* **2**, 303 (1989).
8. K. Hornik, M. Stinchcombe, and H. White, "Multilayer feedforward networks are universal approximators," *Neural Networks* **2**, 359 (1989).
9. R. F. Pawula, "A modified Siegert's formula," *Phys. Rev. E* **49**, 4747 (1994), and standard treatments of the leaky integrate-and-fire neuron.
10. Mössbauer effect and room-temperature recoilless gamma resonance: standard references in nuclear spectroscopy.
11. Entangled gamma pairs from positron annihilation: standard references in gamma-gamma angular correlation experiments.

---

*Radiation is the computer when the gate is the radiation-controlled nuclear release.*
