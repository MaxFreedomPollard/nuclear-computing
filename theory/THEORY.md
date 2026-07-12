# Theory supplement: derivations and the engineering form of the keystone

This document carries the full derivations behind the foundational README and extends the keystone criterion from its per nucleus form to the form an engineer or a referee would actually test: areal densities, collection losses, cascadability, reset accounting, and the one sector of nuclear physics where every keystone quantity is already a library constant. Notation follows Appendix A of the README throughout.

---

## 1. The keystone criterion in engineering form

The README states the criterion per nucleus: $\eta = \sigma_{\text{trig}}\phi_{\text{ctrl}} / (\sigma_{\text{trig}}\phi_{\text{ctrl}} + \lambda_m) > \tfrac12$ and $\Gamma = \beta\eta/C_{\text{in}} > 1$. Real gates are slabs, not single nuclei, and the per nucleus form hides the two loss channels that dominate any laboratory attempt. Both are made explicit here.

### 1.1 Slab gain and the areal density requirement

Let a gate be a slab of isomer bearing material with areal number density $N_A$ (excited nuclei per cm²) facing a control beam. A single control quantum crossing the slab triggers a release with probability

$$ P_1 \;=\; 1 - e^{-N_A \sigma_{\text{trig}}} \;\approx\; N_A \sigma_{\text{trig}} \quad (\text{optically thin}), $$

so the photon number gain per control quantum, before any losses, is

$$ \Gamma_{\text{slab}} \;=\; \beta \left(1 - e^{-N_A \sigma_{\text{trig}}}\right) \;\approx\; \beta\, N_A\, \sigma_{\text{trig}}. $$

The amplification condition $\Gamma_{\text{slab}} > 1$ therefore sets a **required areal density**

$$ \boxed{\; N_A \;>\; \frac{1}{\beta\,\sigma_{\text{trig}}} \;} $$

in the thin limit. The scale of the problem follows immediately. For ¹⁷⁸ᵐ²Hf with its measured $\beta = 12.39$ (see `/gates`), a cross section of one barn would demand $N_A > 8.1\times10^{22}$ excited nuclei per cm², about two centimeters of *pure, fully inverted* solid hafnium isomer; no macroscopic quantity of ¹⁷⁸ᵐ²Hf has ever existed. A millibarn cross section demands a thousand times more. Only two escapes exist: a resonantly enormous $\sigma_{\text{trig}}$ (the ²²⁹Th optical transition reaches effective resonant cross sections many orders above geometric, which is why lasers can drive single nuclei), or a channel whose cross section is already hundreds of barns (Section 4).

### 1.2 Self absorption

The released quanta must leave the slab. If the output line has attenuation coefficient $\mu_{\text{out}}$ in the host, a release at depth $x$ escapes toward the collector with probability $e^{-\mu_{\text{out}} x}$, and the slab average multiplies the gain by

$$ f_{\text{esc}} \;=\; \frac{1 - e^{-\mu_{\text{out}} L}}{\mu_{\text{out}} L}, $$

which punishes exactly the thick slabs that Section 1.1 demands. Gain per unit thickness rises while escape falls; the product has an interior optimum, and honest candidate evaluation must quote $\Gamma$ at that optimum, not at either limit.

### 1.3 Collection: the fan out tax

Spontaneous and cascade emission is isotropic; the next gate subtends a solid angle $\Omega$. The gain that survives routing is

$$ \boxed{\; \Gamma_{\text{eff}} \;=\; \Gamma_{\text{slab}}\; f_{\text{esc}}\; \frac{\Omega}{4\pi}\; \eta_{\text{tr}} \;} $$

with $\eta_{\text{tr}}$ the transport efficiency of the interconnect. A measured $\beta$ of 12 with one percent collection is a net loss of 0.12: **isotropy, not multiplicity, is the first thing that kills naive cascade designs.** Three known answers, in increasing power:

1. **Geometry**: near $4\pi$ enclosure of the emitter by the successor gate (concentric shells), buying $\Omega/4\pi \to 1$ at the price of addressing.
2. **Coherent forward emission**: in nuclear forward scattering of Mössbauer transitions the excited ensemble radiates as a collective exciton, *directionally*, into the incident beam mode; this is routine at synchrotron nuclear resonance beamlines and is the physical solution to interconnect directionality at 14.4 keV (⁵⁷Fe) and its relatives. The stochastic tier does not need it; the cascaded amplifier tier almost certainly does.
3. **A self restoring medium** in which the "next gate" is the same medium everywhere, so there is no routing loss at all. That is Section 4.

### 1.4 The rate condition: the third inequality

For long lived isomers the leak condition flatters the candidate: with $t_{1/2} = 31$ y, any perceptible drive beats $\lambda_m$. What a computer needs is not merely to beat the leak but to fire on the machine's clock:

$$ \boxed{\; R_{\text{trig}} = \sigma_{\text{trig}}\,\phi_{\text{ctrl}} \;\gtrsim\; f_{\text{gate}} \;} $$

At a synchrotron nuclear resonance beamline ($\phi \sim 10^{16}$ cm⁻² s⁻¹, see `/gates/experiment_menu.md`), a one barn cross section fires a given nucleus once per $10^8$ seconds. The keystone criterion is therefore three inequalities, of which the published two (leak, amplification) are the *existence* conditions and this one is the *usefulness* condition. It is the binding constraint for every long lived candidate in the table.

---

## 2. Level restoration: what makes a gate cascadable

Electronics quietly relies on a property so basic it is rarely named: a transistor's output levels are set by the supply rails, not by its input levels, so stages can be chained indefinitely and noise does not accumulate. The nuclear analog deserves a name and a place in the theory.

**Definition.** A triggered release gate is *level restoring* if its output quanta are of the kind and energy that trigger further gates of the same design, with the released stored energy, not the input, setting the output scale.

Three classes exhaust the candidates:

- **Self restoring.** Fission: output neutrons are born fast (about 2 MeV, set by the fission barrier physics) *regardless of the energy of the triggering neutron*, and after moderation they are again ideal triggers. The output token is the input token. The loop closes with no conversion stage, which is precisely why a chain reaction exists at all.
- **Convertible.** Isomer cascades emit fixed lines differing from their trigger line. A homogeneous chain is impossible, but a *heterogeneous* pair (gate A's strongest cascade line chosen to be resonant with gate B's gateway, and vice versa) restores levels by design, the way CMOS pairs complementary devices. This is an open design problem stated precisely: find isomer pairs (A, B) in ENSDF with mutually resonant cascade and gateway lines. The `/gates` catalog is the search space.
- **Terminal.** ¹⁸⁰ᵐTa releases 77 keV against a trigger costing at least 1.01 MeV. No arrangement of terminal gates can cascade; they are readouts, not logic. Photon number gain without level restoration is bookkeeping, not amplification: the energy ledger must also close, $\beta \bar E_{\text{out}} > C_{\text{in}} E_{\text{trig}}$, with $\bar E_{\text{out}}$ usable at the next stage.

**Consequence.** The keystone search is not for any $(\eta > \tfrac12,\ \Gamma > 1)$ pair; it is for such a pair *within one of the first two classes*. This tightens kill criterion B honestly: a gain gate that cannot drive its successor kills the amplifier tier just as dead.

---

## 3. Corrections to the throughput ledger

### 3.1 Reset accounting

A fired gate is an emptied register: the isomer must be re pumped before the gate can fire again. If the pump transition has cross section $\sigma_p$ under pump flux $\phi_p$, the rewrite takes $t_{\text{reset}} \sim (\sigma_p \phi_p)^{-1}$ and consumes $C_{\text{reset}}$ pump quanta per stored excitation (inclusive of pump inefficiency). The full cost of one gate evaluation at $b$ bit output precision is then

$$ C_{\text{eval}} \;=\; C_{\text{in}} \;+\; C_{\text{reset}} \;+\; 2^{2b}\ (\text{readout counts}), $$

and the sustained rate of a pipelined gate is bounded by both the trigger and the pump:

$$ f_{\text{gate}} \;\leq\; \min\!\big(R_{\text{trig}},\ \sigma_p \phi_p\big). $$

Ops per decay, the document's figure of merit, must be quoted against $C_{\text{eval}}$, not against $C_{\text{in}}$ alone. For the stochastic tier the correction is benign (the sampler's proposals do not empty registers); for the amplifier tier it typically doubles the cost.

### 3.2 The pile up ceiling

Any physical interaction site or detector has a resolving time $\tau_d$; above rate $\sim 1/\tau_d$ per site, events merge and information is destroyed rather than gained. A machine of activity $\lambda$ must therefore spread its traffic over at least

$$ n_{\text{sites}} \;\gtrsim\; \lambda\,\tau_d $$

independent interaction sites. This converts the throughput law from a promise into a floor plan: activity buys throughput only when matched by parallelism, which the in memory character of the substrate (every nucleus is a site) is naturally suited to supply.

---

## 4. The proven keystone at reactor scale

Apply the three inequalities of Sections 1 and 2, with no new physics, to the fissile nucleus.

- **Storage.** ²³⁵U stores about 202 MeV per nucleus behind a fission barrier; $t_{1/2} = 7.04\times10^8$ y, so $\lambda_m = 3.1\times10^{-17}$ s⁻¹ and the leak condition is satisfied by any perceptible drive.
- **Trigger.** Thermal neutron capture, $\sigma_f = 585$ b, tabulated to four significant figures in ENDF/B. At an ordinary thermal flux of $10^{14}$ n cm⁻² s⁻¹, $R_{\text{trig}} = 5.85\times10^{-8}$ s⁻¹ per nucleus, and $\eta \approx 1$ identically; the *rate* condition is met not per nucleus but per gate, because a gate contains of order $10^{22}$ nuclei.
- **Multiplicity and gain.** $\bar\nu = 2.43$ neutrons plus about 7 prompt photons per fission; per neutron *absorbed*, $\bar\nu\,\sigma_f/(\sigma_f + \sigma_\gamma) \approx 2.1 > 1$.
- **Level restoration.** Self restoring, Section 2: fission neutrons are born at the same spectrum whatever triggered the fission.

Every keystone inequality is satisfied simultaneously, by library data, with margins measured in orders of magnitude (`/gates/experiment_menu.md`). The same holds for ²⁴²ᵐAm, which is literally an *isomer* whose trigger channel (thermal fission, $\sigma_f \approx 6.4$ kb) is proven, closing the loop with the candidate table: the one isomer row where trigger, flux, and multiplicity are all measured is the one whose release channel is fission. And ⁹Be(n,2n) supplies a proven $\beta = 2$ gate with no fissile material, though it is only convertible, not self restoring (its outputs degrade in energy toward threshold).

**The gate network already has its mathematics.** A subcritical multiplying region with multiplication factor $k < 1$ amplifies an injected neutron population by $M = 1/(1-k)$: a threshold amplifier whose gain is set by composition and geometry. Coupled region kinetics, in which region $i$ feeds region $j$ with coupling coefficients $k_{ij}$, was worked out by Avery in 1958 for coupled reactor cores; it is formally the Green's function synapse of this theory with gain on the diagonal. Local absorbers (control elements) program thresholds and vetoes; a two region arrangement in which region B fires only on the coincidence of region A's leakage with an external drive is an AND with gain; adding a veto absorber yields NAND. Prompt neutron generation times set the clock: about $10^{-4}$ s in thermal systems and about $10^{-8}$ s in fast ones. All of this remains strictly subcritical ($k < 1$ everywhere, always, with gain $1/(1-k)$ bounded and externally driven); it is standard reactor kinetics rearranged into computational language.

**What this does and does not claim.** It does not claim a practical computer: a neutron gate is centimeters to meters of moderated or fast assembly, wrapped in licensing, shielding, and fissile material control that place it outside individual reach, and its energy per operation is grotesque by Section 5 of the README. It claims something more important for the theory: **existence**. The model of computation defined by the two governing equations is physically complete at one scale, with 1940s physics; nature has run self restoring triggered release networks (natural reactors at Oklo, two billion years ago) without human help. The keystone program is therefore a *miniaturization* program, from meter scale neutron gates toward crystal scale photon gates, and not a search for whether the model can exist at all. A theory whose central risk is "can this be shrunk" is in a categorically stronger position than one whose central risk is "can this exist."

The simulation counterpart is specified in the README roadmap (Phase B2): reproduce the two region NAND in OpenMC with ENDF data, all inputs public, all outputs subcritical. It requires no laboratory and settles the architecture questions (coupling matrices, absorber programming, clock rates) that the isomer sector will inherit when its own gate arrives.

---

## 5. Derivations

### 5.1 Independent streams from one source (thinning)

For a Poisson process $N(t)$ of rate $\lambda$, increments over disjoint intervals are independent by definition, so time slicing yields independent streams. Marking each event independently with probability $\alpha$ (an aperture of transmission $\alpha$) yields a process whose count in $[0,t]$ is $\mathrm{Binomial}(N(t), \alpha)$ mixed over $N(t) \sim \mathrm{Poisson}(\lambda t)$, which is $\mathrm{Poisson}(\alpha\lambda t)$; independence of the marked and unmarked substreams follows from the independence of the marks. Hence one physical source supplies arbitrarily many mutually independent inputs of any rates $x_i \lambda$, $x_i \in [0,1]$, with no pseudorandom generator.

### 5.2 Coincidence: exact survival form

Fix a stream 1 event at time $t$. Stream 2, independent Poisson of rate $r_2$, deposits no event in the window $[t - \tau_w, t + \tau_w]$ with probability $e^{-2\tau_w r_2}$. The rate of stream 2 events falling within $\tau_w$ of *some* stream 1 event is, by symmetry and stationarity,

$$ r_{\text{AND}} \;=\; r_2\big(1 - e^{-2\tau_w r_1}\big) \;\xrightarrow{\ \tau_w r_1 \ll 1\ }\; 2\tau_w r_1 r_2, $$

the multiplier of the gate set; with $r_i = x_i \lambda$ the output rate is proportional to $x_1 x_2$. The exact form matters at high drive: at $2\tau_w r_1 = 0.2$ the leading order overpredicts by ten percent, an effect reproduced to Monte Carlo precision in `/transport/results.md`.

### 5.3 Transport linearity and signed weights

With cross sections frozen, the Boltzmann transport operator is linear in $\phi$, so the port to port response defines a matrix $\mathcal{G}$ with $\phi_{\text{out}} = \mathcal{G}\,\phi_{\text{in}}$ and superposition holds exactly (verified to Monte Carlo error in `/transport`). Physical rates are nonnegative, so $\mathcal{G}$ has nonnegative entries; signed weights are realized by complementary channel pairs $(w^+, w^-)$ feeding excitatory and inhibitory (veto) inputs, the standard construction shared with optical neural networks.

### 5.4 The Siegert activation

A site receiving Poisson excitation and inhibition with net drift $\mu$ and variance $\sigma^2$ is, in the diffusion limit, an Ornstein Uhlenbeck membrane $\tau_m \dot V = -(V - \mu) + \sigma\sqrt{2\tau_m}\,\xi(t)$; the mean first passage time from reset $V_r$ to threshold $V_{\text{th}}$ gives the firing rate

$$ \nu(\mu,\sigma) \;=\; \Big[\, t_{\text{ref}} + \tau_m \sqrt{\pi} \int_{(V_r-\mu)/\sigma}^{(V_{\text{th}}-\mu)/\sigma} e^{u^2}\big(1 + \mathrm{erf}\,u\big)\, du \,\Big]^{-1}, $$

a smooth sigmoid in $\mu$ (Siegert 1951). Composed with the linear map $\mathcal{G}$ it satisfies the hypotheses of the universal approximation theorems (Cybenko 1989; Hornik 1991).

### 5.5 Detailed balance of the sampler

Sites update at Poisson proposal times; a proposal at site $k$ sets $z_k = 1$ with probability $\sigma(u_k) = (1 + e^{-u_k})^{-1}$, $u_k = \sum_j W_{kj} z_j + b_k$, $W$ symmetric with zero diagonal. This is exactly the conditional law $p(z_k = 1 \mid z_{\setminus k})$ of the Gibbs measure $p(z) \propto \exp(\tfrac12 z^\top W z + b^\top z)$, so each update leaves $p$ invariant (a random scan Gibbs sampler), and irreducibility plus aperiodicity of the chain give convergence to $p$ from any start. The digital twin in `/simulator` verifies this empirically to KL divergence a few times $10^{-4}$ over all $2^8$ states, at a measured cost of about 26 decays per independent sample.

### 5.6 The precision law

An estimate of a rate $r$ from a count $n \sim \mathrm{Poisson}(rT)$ has Fisher information $T/r$, so any unbiased estimator obeys $\mathrm{Var} \geq r/T$ (Cramér Rao), giving relative error $\geq 1/\sqrt{rT}$. Resolving $b$ bits means relative error $\leq 2^{-b}$, hence $N = rT \geq 2^{2b}$, and a network sharing an event budget $\lambda$ sustains at most $f_{\text{gate}} \approx \lambda / 2^{2b}$ evaluations per second at that precision. Corrections from reset and pile up are given in Section 3.

---

## 6. Universality without the keystone: the Bernstein construction

The universality results of the main document (Cybenko for analog, NAND for digital) both consume the threshold gate, and therefore both wait on the keystone. This section proves that a large and useful class of computation waits on nothing.

**The stream algebra.** Encode $x \in [0,1]$ as a thinned Poisson stream of rate $x\lambda$ (Section 5.1), or equivalently as the Bernoulli occupancy of its time slices. The three routine gates then implement, exactly:

- coincidence: $z = x \cdot y$ (independent streams multiply, Section 5.2),
- scattering MUX with select weight $s$: $z = s\,x + (1-s)\,y$ (convex combination),
- absorption: $z = 1 - x$ (complement).

This is precisely the algebra of stochastic computing (Gaines 1967), realized in radiation rather than in shift registers.

**Theorem (feed forward universality).** For any continuous $f : [0,1] \to [0,1]$ and any $\varepsilon > 0$ there is a *feed forward* circuit of the three routine gates whose output stream has rate $B_n[f](x)\,\lambda$ with $\sup_x |B_n[f](x) - f(x)| < \varepsilon$, where

$$ B_n[f](x) \;=\; \sum_{k=0}^{n} \binom{n}{k} x^k (1-x)^{n-k}\, f\!\left(\tfrac{k}{n}\right) $$

is the degree $n$ Bernstein polynomial of $f$.

*Proof.* The Bernstein coefficients $\beta_k = f(k/n)$ lie in $[0,1]$ because $f$ does. Draw $n$ independent time slices of the input stream (independence by Section 5.1); the number $k$ of occupied slices is $\mathrm{Binomial}(n, x)$. Use $k$ to select, by a MUX tree, a reference stream of rate $\beta_k \lambda$ (a thinned aperture constant). The output occupancy is $\mathbb{E}[\beta_K] = B_n[f](x)$ by construction, and $B_n[f] \to f$ uniformly (Bernstein 1912), with error $O(\|f''\|_\infty / n)$ for smooth $f$. Every element used is a routine gate. $\square$

The synthesis of arbitrary polynomials in this form is the stochastic logic architecture of Qian and Riedel (DAC 2008; IEEE Trans. Computers 60, 93 (2011)), imported here wholesale: their shift register Bernoulli sources are replaced by thinned decay streams that no circuit had to generate.

**What the keystone actually buys.** The construction is feed forward and memoryless: it approximates functions, it does not iterate them. Three things remain locked behind the threshold gate with gain: *recurrence* (closing loops without signal death requires $\Gamma_{\text{eff}} \geq 1$), *restoration* (composing unbounded depth requires levels that do not degrade), and *memory coupled dynamics* (Turing completeness requires state that the computation itself rewrites). The honest hierarchy is therefore: **function approximation and Monte Carlo estimation are keystone free; open loop inference is keystone free; anything with a feedback loop crossing a gain deficit is not.** This sharpens both kill criteria: even a total failure of Phase B leaves a machine that evaluates arbitrary continuous functions and integrals by physics alone. The construction is verified numerically, gate by gate, in [/transport](../transport/results.md).

**Cost accounting.** Precision still obeys Section 5.6 at every stage: a depth $d$ Bernstein circuit read to $b$ bits consumes $O(d\, 2^{2b})$ source events per evaluation, and the degree $n$ needed scales as $O(\|f''\|/\varepsilon)$. Nothing here is fast. It is merely universal, free of the keystone, and running on decays.

---

## 7. Aging invariance: correctness does not decay

A sealed source decays; the machine built on it slows. This section proves that a properly designed machine slows *without becoming wrong*, which is the mathematical heart of self sustainment.

**Setup.** Let every stream in the machine derive from one source of activity $\lambda(t) = \lambda_0\, 2^{-t/T}$, so all rates scale together by $s = \lambda(t)/\lambda_0$. Define the **coincidence degree** $\deg(r)$ of a signal: a thinned stream has degree 1; a coincidence output has $\deg = \deg_1 + \deg_2$ (its rate is $2\tau_w r_1 r_2$); MUX and absorption preserve degree (convex combinations and survival fractions of like degree streams).

**Theorem (degree homogeneity).** Under global scaling $\lambda \to s\lambda$, every signal of degree $k$ transforms as $r \to s^k r$. Consequently any quantity formed as a *ratio of like degree signals* is invariant, and any decision made by comparing like degree signals is invariant, for all $s > 0$.

*Proof.* Induction over the circuit. Thinning multiplies a degree $k$ signal by a constant; coincidence maps $(s^{k_1} r_1,\, s^{k_2} r_2) \mapsto 2\tau_w s^{k_1 + k_2} r_1 r_2$; MUX and absorption are linear with constant coefficients. Ratios of equal powers of $s$ cancel. $\square$

**Design rule (boxed in one line).** *Compare like degree only with like degree.* A circuit that thresholds a degree 2 coincidence signal against a degree 1 reference is correct on the day it ships and drifts as $2^{-t/T}$ thereafter; the same circuit thresholded against a degree 2 reference is correct until the source is gone. Homogenization costs one gate per reference path and buys immunity to the only aging mechanism the substrate has.

**Corollary 1 (the sampler does not age).** The Gibbs acceptance $\sigma(u_k)$ of the sampling tier depends only on occupancies $z_j \in \{0,1\}$ and dimensionless weights, never on absolute rates; the stationary law $p(z) \propto \exp(\tfrac12 z^\top W z + b^\top z)$ is therefore exactly activity invariant. Aging rescales only the event clock: mixing time in wall clock seconds grows as $2^{+t/T}$.

**Corollary 2 (the aging law of a sealed machine).** A degree homogeneous machine of half life $T$ delivers throughput $C(t) = C_0\, 2^{-t/T}$ at unchanged accuracy, with no recalibration, no trimming, and no reference standard other than itself. Its performance at end of mission is known on the day of manufacture to Poisson precision. No battery powered computer can state its own end of life curve in closed form; this one can.

---

## 8. The boundary: translating compute in and out

The charter forbids conventional electronics *inside* the loop; it says nothing about the skin. This section is the theory of the skin: how radiation native results become currents, counts, and spectra, and how external problems become apertures, velocities, and fields, with the price of every conversion stated.

### 8.1 Outputs

1. **Counts (digital).** A boundary detector converts a rate $r$ to counted quanta; the precision law prices it: $b$ bits per read costs $2^{2b}$ counts, so a boundary budget $\lambda_B$ (detected events per second) supports an output bandwidth $f_{\text{out}} = \lambda_B / 2^{2b}$. At $\lambda_B = 10^7$ s⁻¹ detected: about 150 reads per second at 8 bits, 40,000 at 4 bits. Precision is purchasable per port, per read.
2. **Current (analog).** A photovoltaic or betavoltaic junction at the boundary converts a quantum rate to $I = e\, G\, r$ ($G$ the carrier yield per quantum). The shot noise of $I$ *is* the same Poisson limit in a different unit; nothing is gained or lost in the conversion, which is the correct sanity check.
3. **Spectrum (energy division multiplexing).** Distinct isotope lines are orthogonal channels through one physical window: a boundary spectrometer with resolving power to separate $N_E$ lines reads $N_E$ parallel ports simultaneously. Position adds $N_x$ pixel ports; arrival time adds $N_\tau$ resolvable bins per mean interval.
4. **The per quantum ceiling.** One detected quantum distinguishable among $N_E N_x N_\tau$ classes carries at most $\log_2(N_E N_x N_\tau)$ bits. A pixelated CZT boundary ($N_E \approx 10^2$ lines, $N_x = 256$ pixels, $N_\tau \approx 10^3$ timing bins) ceilings near **24 bits per detected quantum**; realized mutual information sits below this, but the ceiling sets the design target: *spend the decay budget on distinguishable quanta, not on more quanta.*

### 8.2 Inputs

1. **Apertures** (mechanical or magnetic shutters): set thinning fractions $x$; slow (ms and up), absolute, zero power at rest. The program counter of the stochastic tier.
2. **Doppler drives.** A resonant channel detunes by one natural linewidth at $v = c\,\Gamma/E$: for ⁵⁷Fe, $0.097$ mm/s. Piezoelectric velocity transducers (the ordinary Mössbauer drive, seventy years of practice) modulate resonant transmission fully at kHz to MHz rates: **the fast input port**, writing waveforms directly into cross sections.
3. **Zeeman programming.** An external field shifts hyperfine components by of order $0.1\,\mu_N B$: for ⁵⁷Fe about **0.7 natural linewidths per tesla**, enough to move a resonant channel on or off a line with ordinary coils, *through a sealed wall, with no penetration*. Weights become field maps: the machine is reprogrammed the way an MRI shims, from outside.
4. **Beam injection** through thin windows (X ray, VUV, or neutron): the high bandwidth port when a penetration is acceptable.

### 8.3 The no penetration principle

Together 8.1 and 8.2 permit a machine whose enclosure is never breached: problems enter as *fields and motions* (Zeeman maps, Doppler waveforms, aperture settings through magnetic couplings), answers leave as *glow* (the boundary emission spectrum, read by any external spectrometer or diode). Input by field, output by light, power by decay: the complete unit is specified in [transistor/SEALED.md](../transistor/SEALED.md).

---

## 9. The nuclear lamp: closing the bandwidth gap from inside

The sealed unit's failure to write its own memory ([transistor/SEALED.md](../transistor/SEALED.md), Section 3) has a specific anatomy: an *atomic* light source (an excimer continuum, $10^{14}$ Hz wide) was aimed at a *nuclear* line ($10^{-4}$ Hz wide), and the overlap integral ate eighteen orders of magnitude. The fix is not a brighter lamp. It is to notice that the mismatch is a property of atomic light, and that a sealed decay inventory contains emitters that are not atomic.

### 9.1 The bandwidth matching principle

The pumping rate of an absorber by a source is $R = \int \sigma(\nu)\,\phi_\nu\, d\nu$, and for a source of bandwidth $\Delta\nu_s$ delivering flux $\phi$ onto a line of width $\Gamma$, $R \sim \phi\,\sigma_0\,(\Gamma/\Delta\nu_s)$ when $\Delta\nu_s \gg \Gamma$. The figure of merit is the bandwidth ratio, and it is binary in practice:

- **atomic sources** (thermal, excimer, scintillation, even most lasers) have $\Delta\nu_s/\Gamma \gtrsim 10^{12}$ against nuclear lines: dead, per the arithmetic already published;
- **nuclear sources emit nuclear lines.** A radioactive parent that decays *into* the working transition emits quanta at exactly the resonant energy with exactly the natural width (recoil free fraction permitting): $\Delta\nu_s/\Gamma = 1$ by construction. This is not a proposal; it is the operating principle of every Mössbauer source since 1958. ⁵⁷Co embedded in a rhodium foil *is* a 14.4 keV lamp with a $10^{-8}$ eV linewidth: the narrowline internal source, sitting in catalogs for seventy years.

The design consequence for the ampoule is one sentence: **the trim layer's resonant channels must be driven by embedded parent isotopes of their own working transitions, never by the broadband core.** The core remains power, clock, and entropy; the parents are the machine's monochromatic light plant, one line per channel. Standard matched pairs, all demonstrated: ⁵⁷Co → ⁵⁷Fe (14.4 keV), ¹¹⁹ᵐSn → ¹¹⁹Sn (23.9 keV), ¹⁵¹Sm → ¹⁵¹Eu (21.5 keV), ¹⁸¹W → ¹⁸¹Ta (6.2 keV).

### 9.2 Radiogenic feeding: writing without photons

The second nuclear channel skips light entirely: some parents decay *directly into the metastable state*. The canonical case is the machine's own memory isotope: about 2 percent of ²³³U alpha decays populate ²²⁹ᵐTh, which is how the isomer's radiation was first detected. A crystal doped with ²³³U therefore maintains a **standing isomer population** with no laser and no lamp, at equilibrium $n_m = 0.02\,\lambda_{233}\,N_{233}\,\tau_m$: computable, self replenishing, and proven physics. Numbers in [`sealed_results.md`](../transistor/sealed_results.md): at $10^{17}$ ²³³U per cm³ the standing population is of order $2\times10^5$ isomers per cm³. What radiogenic feeding does *not* provide is addressing: it writes everywhere at once, a bias, not a bit. It supplies the resonant reference ensemble (a carrier the trim layer can modulate), and it is the existence proof that the sealed unit can hold excited nuclear state without any penetration; the addressed write is what remains.

### 9.3 Resonance addressing: the MRI move

Addressing is the third piece, and magnetic resonance imaging already solved it in a different spectral register: flood the volume with a narrowline drive, and let a **field gradient** decide which voxel is on resonance. The trim layer's Zeeman tuning becomes spatial selection: with line sensitivity $dE/dB$ and gradient $G = dB/dx$, the addressable resolution is

$$ \delta x \;=\; \frac{\Gamma}{(dE/dB)\,G}. $$

The sensitivity is set by the linewidth, which makes the ultranarrow lines the easy ones. For ⁵⁷Fe ($\Gamma = 4.7\times10^{-9}$ eV, about 0.7 linewidths per tesla) gradients of tesla per centimeter are needed: hard. For **¹⁸¹Ta** (6.2 keV, $t_{1/2} = 6.05$ µs, $\Gamma = 7.5\times10^{-11}$ eV) the same nuclear moment buys about **40 linewidths per tesla**, so a *millitesla* scale field moves a channel by a full linewidth, and modest gradients address millimeter voxels; its Doppler sensitivity, one linewidth per 3.6 µm/s, makes a whisper of a piezo a full modulation (and makes vibration isolation a real engineering line item, stated honestly). ¹⁸¹Ta is fed by ¹⁸¹W (121 d), a standard source; its 6 µs lifetime makes it not storage but a **latch**: a microsecond scale, field addressed, parent driven holding register, which is precisely the missing timing element between the 98 ns ⁵⁷Fe relay and the 630 s ²²⁹Th register. Known cost, stated plainly: the 6.2 keV transition is heavily conversion dominated and its recoil free fraction is small, so photon budgets are thin; the latch is real physics with an efficiency tax, not free.

### 9.4 What remains open

Sections 9.1 to 9.3 upgrade the sealed machine from "no nuclear state at all" to: proven relays (ns), proven latch physics (µs, addressable), and a proven standing register population (minutes, unaddressed). The single remaining gap, now stated much more narrowly than "the bandwidth problem," is the **addressed long retention write**: either a parent fed, gradient addressed line with lifetime above seconds (a search the isomer catalog in [/gates](../gates/) can run: long lived isomers with Mössbauer class feeding parents), or a bright sub kHz source at 148.38 nm (the nuclear clock community's laser roadmap, arriving on its own schedule). That is Open Problem 6, sharpened.

---

## 10. The rate coded canon: everything that keeps stream computation honest

Four results complete the defensibility of the rate coded machine, each short, each load bearing.

### 10.1 The isolation lemma and the variance calculus

Stream circuits fail in exactly one way: **reuse.** If a stream feeds two paths that later recombine, products are biased: $\mathbb{E}[z\,z] = x \neq x^2$, and generally $\mathbb{E}[z_1 z_2] = x_1 x_2 + \rho\,\sigma_1\sigma_2$ for correlation $\rho$. The cure is structural: by the independent increments property, disjoint time slices and independent thinnings of one source are exactly independent (Section 5.1), so the rule is: **every fan out is a fresh thinning, never a copy.** With the rule obeyed, the calculus is benign: each gate's output is itself a Bernoulli/Poisson stream whose *mean is exactly* the target function of the input means, so depth does not compound systematic error at all; an estimate from $N$ slices has $\mathrm{Var} = p(1-p)/N \leq 1/4N$ *at any depth*. Depth costs only budget: a depth $d$ circuit read to $b$ bits consumes $O(d\,2^{2b})$ events per evaluation. Error does not accumulate; only the bill does.

### 10.2 The annealing schedule, as one moving part

The sampler's temperature is a global scale on $u_k$, and $u_k$ is built from weight carrying fluxes: one master aperture on the weight paths scales all of them, so **the machine's temperature is a single mechanical dial**. The Geman and Geman theorem (IEEE PAMI 6, 721 (1984)) then applies verbatim: a logarithmic cooling schedule $T(k) \geq c/\log(1+k)$ converges in probability to the ground state, and any faster practical schedule inherits the usual guarantees on approximate optima. The ampoule anneals by turning one absorber, on a printed schedule, powered by a clockwork spring if need be. Asynchronous updates are not an approximation here: the Poisson event clock *is* Glauber dynamics, which is the setting the theorem wants.

### 10.3 Graceful degradation and self calibration

There is no bit to flip: a lost quantum perturbs a rate by one count in $N$, so single event upsets, the plague of conventional radiation adjacent electronics, do not exist as a failure class. Uniform losses (aging, uniform dose, detector fatigue) are global thinnings, absorbed exactly by degree homogeneity (Section 7). The residual hazard is *nonuniform* drift, one path fading faster than another, which breaks the like for like rule slowly; the counter is already onboard: a fixed nuclear line (the ²⁴¹Am 60 keV, or any parent line from 9.1) is a drift free standard against which every path's ratio can be re trimmed through the wall, MRI shim style. The machine carries its own meter stick, of nuclear invariance, at zero marginal cost.

### 10.4 Modules

Ampoules compose: each unit's boundary glow, filtered to a distinct emission line, is another unit's beam injection input (Section 8.2, item 4), so a rack of ampoules is a network with energy division multiplexed links, one line per edge, no shared electronics, and the aging theorem applying per module. Nothing about the theory is single vessel.

---

*Sections 1 through 3 are the referee armor: every known way a working gate quietly dies, written down with its inequality. Section 4 is the existence proof that the model survives them all at one scale. Sections 6 through 10 are the machine that needs no keystone, no calibration, and no wires: what can be built while the search runs. The rest is the search itself.*
