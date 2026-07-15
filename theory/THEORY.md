# Theory supplement: derivations and the engineering form of the keystone

This document carries the full derivations behind the foundational README and extends the keystone criterion from its per nucleus form to the form an engineer or a referee would actually test: areal densities, collection losses, cascadability, reset accounting, and the one sector of nuclear physics where every keystone quantity is already a library constant. Notation follows Appendix A of the README throughout.

---

## 1. The keystone criterion in engineering form

The README states the criterion per nucleus: η = σ_trigφ_ctrl / (σ_trigφ_ctrl + λ_m) > ½ and Γ = βη/C_in > 1. Real gates are slabs, not single nuclei, and the per nucleus form hides the two loss channels that dominate any laboratory attempt. Both are made explicit here.

### 1.1 Slab gain and the areal density requirement

Let a gate be a slab of isomer bearing material with areal number density N_A (excited nuclei per cm²) facing a control beam. A single control quantum crossing the slab triggers a release with probability

> `P_1 = 1 - e^(-N_A σ_trig) ≈ N_A σ_trig (optically thin),`

so the photon number gain per control quantum, before any losses, is

> `Γ_slab = β (1 - e^(-N_A σ_trig)) ≈ β N_A σ_trig.`

The amplification condition Γ_slab > 1 therefore sets a required areal density

> `N_A > 1/(β σ_trig)`

in the thin limit. The scale of the problem follows immediately. For ¹⁷⁸ᵐ²Hf with its measured β = 12.39 (see `/gates`), a cross section of one barn would demand N_A > 8.1×10²² excited nuclei per cm², about two centimeters of *pure, fully inverted* solid hafnium isomer; no macroscopic quantity of ¹⁷⁸ᵐ²Hf has ever existed. A millibarn cross section demands a thousand times more. Only two escapes exist: a resonantly enormous σ_trig (the ²²⁹Th optical transition reaches effective resonant cross sections many orders above geometric, which is why lasers can drive single nuclei), or a channel whose cross section is already hundreds of barns (Section 4).

### 1.2 Self absorption

The released quanta must leave the slab. If the output line has attenuation coefficient μ_out in the host, a release at depth x escapes toward the collector with probability e^(-μ_out x), and the slab average multiplies the gain by

> `f_esc = (1 - e^(-μ_out L))/(μ_out L),`

which punishes exactly the thick slabs that Section 1.1 demands. Gain per unit thickness rises while escape falls; the product has an interior optimum, and honest candidate evaluation must quote Γ at that optimum, not at either limit.

### 1.3 Collection: the fan out tax

Spontaneous and cascade emission is isotropic; the next gate subtends a solid angle Ω. The gain that survives routing is

> `Γ_eff = Γ_slab f_esc Ω/(4π) η_tr`

with η_tr the transport efficiency of the interconnect. A measured β of 12 with one percent collection is a net loss of 0.12: isotropy, not multiplicity, is the first thing that kills naive cascade designs. Three known answers, in increasing power:

1. Geometry: near 4π enclosure of the emitter by the successor gate (concentric shells), buying Ω/4π → 1 at the price of addressing.
2. Coherent forward emission: in nuclear forward scattering of Mössbauer transitions the excited ensemble radiates as a collective exciton, *directionally*, into the incident beam mode; this is routine at synchrotron nuclear resonance beamlines and is the physical solution to interconnect directionality at 14.4 keV (⁵⁷Fe) and its relatives. The stochastic tier does not need it; the cascaded amplifier tier almost certainly does.
3. A self restoring medium in which the "next gate" is the same medium everywhere, so there is no routing loss at all. That is Section 4.

### 1.4 The rate condition: the third inequality

For long lived isomers the leak condition flatters the candidate: with t½ = 31 y, any perceptible drive beats λ_m. What a computer needs is not merely to beat the leak but to fire on the machine's clock:

> `R_trig = σ_trig φ_ctrl ≳ f_gate`

At a synchrotron nuclear resonance beamline (φ ∼ 10¹⁶ cm⁻² s⁻¹, see `/gates/experiment_menu.md`), a one barn cross section fires a given nucleus once per 10⁸ seconds. The keystone criterion is therefore three inequalities, of which the published two (leak, amplification) are the *existence* conditions and this one is the *usefulness* condition. It is the binding constraint for every long lived candidate in the table.

---

## 2. Level restoration: what makes a gate cascadable

Electronics quietly relies on a property so basic it is rarely named: a transistor's output levels are set by the supply rails, not by its input levels, so stages can be chained indefinitely and noise does not accumulate. The nuclear analog deserves a name and a place in the theory.

**Definition.** A triggered release gate is *level restoring* if its output quanta are of the kind and energy that trigger further gates of the same design, with the released stored energy, not the input, setting the output scale.

Three classes exhaust the candidates:

- **Self restoring.** Fission: output neutrons are born fast (about 2 MeV, set by the fission barrier physics) *regardless of the energy of the triggering neutron*, and after moderation they are again ideal triggers. The output token is the input token. The loop closes with no conversion stage, which is precisely why a chain reaction exists at all.
- **Convertible.** Isomer cascades emit fixed lines differing from their trigger line. A homogeneous chain is impossible, but a *heterogeneous* pair (gate A's strongest cascade line chosen to be resonant with gate B's gateway, and vice versa) restores levels by design, the way CMOS pairs complementary devices. This is an open design problem stated precisely: find isomer pairs (A, B) in ENSDF with mutually resonant cascade and gateway lines. The `/gates` catalog is the search space.
- **Terminal.** ¹⁸⁰ᵐTa releases 77 keV against a trigger costing at least 1.01 MeV. No arrangement of terminal gates can cascade; they are readouts, not logic. Photon number gain without level restoration is bookkeeping, not amplification: the energy ledger must also close, β Ē_out > C_in E_trig, with Ē_out usable at the next stage.

**Consequence.** The keystone search is not for any (η > ½, Γ > 1) pair; it is for such a pair *within one of the first two classes*. This tightens kill criterion B honestly: a gain gate that cannot drive its successor kills the amplifier tier just as dead.

---

## 3. Corrections to the throughput ledger

### 3.1 Reset accounting

A fired gate is an emptied register: the isomer must be re pumped before the gate can fire again. If the pump transition has cross section σ_p under pump flux φ_p, the rewrite takes t_reset ∼ (σ_p φ_p)⁻¹ and consumes C_reset pump quanta per stored excitation (inclusive of pump inefficiency). The full cost of one gate evaluation at b bit output precision is then

> `C_eval = C_in + C_reset + 2²ᵇ (readout counts),`

and the sustained rate of a pipelined gate is bounded by both the trigger and the pump:

> `f_gate ≤ min(R_trig, σ_p φ_p).`

Ops per decay, the document's figure of merit, must be quoted against C_eval, not against C_in alone. For the stochastic tier the correction is benign (the sampler's proposals do not empty registers); for the amplifier tier it typically doubles the cost.

### 3.2 The pile up ceiling

Any physical interaction site or detector has a resolving time τ_d; above rate ∼ 1/τ_d per site, events merge and information is destroyed rather than gained. A machine of activity λ must therefore spread its traffic over at least

> `n_sites ≳ λ τ_d`

independent interaction sites. This converts the throughput law from a promise into a floor plan: activity buys throughput only when matched by parallelism, which the in memory character of the substrate (every nucleus is a site) is naturally suited to supply.

---

## 4. The proven keystone at reactor scale

Apply the three inequalities of Sections 1 and 2, with no new physics, to the fissile nucleus.

- **Storage.** ²³⁵U stores about 202 MeV per nucleus behind a fission barrier; t½ = 7.04×10⁸ y, so λ_m = 3.1×10⁻¹⁷ s⁻¹ and the leak condition is satisfied by any perceptible drive.
- **Trigger.** Thermal neutron capture, σ_f = 585 b, tabulated to four significant figures in ENDF/B. At an ordinary thermal flux of 10¹⁴ n cm⁻² s⁻¹, R_trig = 5.85×10⁻⁸ s⁻¹ per nucleus, and η ≈ 1 identically; the *rate* condition is met not per nucleus but per gate, because a gate contains of order 10²² nuclei.
- **Multiplicity and gain.** ν̄ = 2.43 neutrons plus about 7 prompt photons per fission; per neutron *absorbed*, ν̄ σ_f/(σ_f + σ_γ) ≈ 2.1 > 1.
- **Level restoration.** Self restoring, Section 2: fission neutrons are born at the same spectrum whatever triggered the fission.

Every keystone inequality is satisfied simultaneously, by library data, with margins measured in orders of magnitude (`/gates/experiment_menu.md`). The same holds for ²⁴²ᵐAm, which is literally an *isomer* whose trigger channel (thermal fission, σ_f ≈ 6.4 kb) is proven, closing the loop with the candidate table: the one isomer row where trigger, flux, and multiplicity are all measured is the one whose release channel is fission. And ⁹Be(n,2n) supplies a proven β = 2 gate with no fissile material, though it is only convertible, not self restoring (its outputs degrade in energy toward threshold). The neutron sector therefore admits two drivers, and the machine is named for whichever it uses: a fission computer (fission compute) when the multiplying region is fissile, and a fusion computer (fusion compute) when the neutrons are supplied by a fusion source instead, whose 14.1 MeV deuterium tritium output clears the 1.85 MeV ⁹Be(n,2n) threshold with room to spare and drives higher multiplicity multipliers. The gate algebra below is identical for both; only the neutron supply differs.

**The gate network already has its mathematics.** A subcritical multiplying region with multiplication factor k < 1 amplifies an injected neutron population by M = 1/(1-k): a threshold amplifier whose gain is set by composition and geometry. Coupled region kinetics, in which region i feeds region j with coupling coefficients k_ij, was worked out by Avery in 1958 for coupled reactor cores; it is formally the Green's function synapse of this theory with gain on the diagonal. Local absorbers (control elements) program thresholds and vetoes; a two region arrangement in which region B fires only on the coincidence of region A's leakage with an external drive is an AND with gain; adding a veto absorber yields NAND. Prompt neutron generation times set the clock: about 10⁻⁴ s in thermal systems and about 10⁻⁸ s in fast ones. All of this remains strictly subcritical (k < 1 everywhere, always, with gain 1/(1-k) bounded and externally driven); it is standard reactor kinetics rearranged into computational language.

**What this does and does not claim.** It does not claim a practical computer: a neutron gate is centimeters to meters of moderated or fast assembly, wrapped in licensing, shielding, and fissile material control that place it outside individual reach, and its energy per operation is grotesque by Section 5 of the README. It claims something more important for the theory: existence. The model of computation defined by the two governing equations is physically complete at one scale, with 1940s physics; nature has run self restoring triggered release networks (natural reactors at Oklo, two billion years ago) without human help. The keystone program is therefore a *miniaturization* program, from meter scale neutron gates toward crystal scale photon gates, and not a search for whether the model can exist at all. A theory whose central risk is "can this be shrunk" is in a categorically stronger position than one whose central risk is "can this exist."

The simulation counterpart is specified in the README roadmap (Phase B2): reproduce the two region NAND in OpenMC with ENDF data, all inputs public, all outputs subcritical. It requires no laboratory and settles the architecture questions (coupling matrices, absorber programming, clock rates) that the isomer sector will inherit when its own gate arrives.

---

## 5. Derivations

### 5.1 Independent streams from one source (thinning)

For a Poisson process N(t) of rate λ, increments over disjoint intervals are independent by definition, so time slicing yields independent streams. Marking each event independently with probability α (an aperture of transmission α) yields a process whose count in [0,t] is Binomial(N(t), α) mixed over N(t) ∼ Poisson(λ t), which is Poisson(αλ t); independence of the marked and unmarked substreams follows from the independence of the marks. Hence one physical source supplies arbitrarily many mutually independent inputs of any rates x_i λ, x_i ∈ [0,1], with no pseudorandom generator.

### 5.2 Coincidence: exact survival form

Fix a stream 1 event at time t. Stream 2, independent Poisson of rate r_2, deposits no event in the window [t - τ_w, t + τ_w] with probability e^(-2τ_w r_2). The rate of stream 2 events falling within τ_w of *some* stream 1 event is, by symmetry and stationarity,

> `r_AND = r_2(1 - e^(-2τ_w r_1)) → 2τ_w r_1 r_2,`

the multiplier of the gate set; with r_i = x_i λ the output rate is proportional to x_1 x_2. The exact form matters at high drive: at 2τ_w r_1 = 0.2 the leading order overpredicts by ten percent, an effect reproduced to Monte Carlo precision in `/transport/results.md`.

### 5.3 Transport linearity and signed weights

With cross sections frozen, the Boltzmann transport operator is linear in φ, so the port to port response defines a matrix 𝒢 with φ_out = 𝒢 φ_in and superposition holds exactly (verified to Monte Carlo error in `/transport`). Physical rates are nonnegative, so 𝒢 has nonnegative entries; signed weights are realized by complementary channel pairs (w^+, w^-) feeding excitatory and inhibitory (veto) inputs, the standard construction shared with optical neural networks.

### 5.4 The Siegert activation

A site receiving Poisson excitation and inhibition with net drift μ and variance σ² is, in the diffusion limit, an Ornstein Uhlenbeck membrane τ_m V̇ = -(V - μ) + σ√(2τ_m) ξ(t); the mean first passage time from reset V_r to threshold V_th gives the firing rate

> `ν(μ,σ) = [ t_ref + τ_m √π ∫_(V_r-μ)/σ^((V_th-μ)/σ) e^(u²)(1 + erf u) du ]⁻¹,`

a smooth sigmoid in μ (Siegert 1951). Composed with the linear map 𝒢 it satisfies the hypotheses of the universal approximation theorems (Cybenko 1989; Hornik 1991).

### 5.5 Detailed balance of the sampler

Sites update at Poisson proposal times; a proposal at site k sets z_k = 1 with probability σ(u_k) = (1 + e^(-u_k))⁻¹, u_k = Σ_j W_kj z_j + b_k, W symmetric with zero diagonal. This is exactly the conditional law p(z_k = 1 | z_∖ k) of the Gibbs measure p(z) ∝ exp(½ zᵀ W z + bᵀ z), so each update leaves p invariant (a random scan Gibbs sampler), and irreducibility plus aperiodicity of the chain give convergence to p from any start. The digital twin in `/simulator` verifies this empirically to KL divergence a few times 10⁻⁴ over all 2⁸ states, at a measured cost of about 26 decays per independent sample.

### 5.6 The precision law

An estimate of a rate r from a count n ∼ Poisson(rT) has Fisher information T/r, so any unbiased estimator obeys Var ≥ r/T (Cramér Rao), giving relative error ≥ 1/√(rT). Resolving b bits means relative error ≤ 2⁻ᵇ, hence N = rT ≥ 2²ᵇ, and a network sharing an event budget λ sustains at most f_gate ≈ λ / 2²ᵇ evaluations per second at that precision. Corrections from reset and pile up are given in Section 3.

---

## 6. Universality without the keystone: the Bernstein construction

The universality results of the main document (Cybenko for analog, NAND for digital) both consume the threshold gate, and therefore both wait on the keystone. This section proves that a large and useful class of computation waits on nothing.

**The stream algebra.** Encode x ∈ [0,1] as a thinned Poisson stream of rate xλ (Section 5.1), or equivalently as the Bernoulli occupancy of its time slices. The three routine gates then implement, exactly:

- coincidence: z = x · y (independent streams multiply, Section 5.2),
- scattering MUX with select weight s: z = s x + (1-s) y (convex combination),
- absorption: z = 1 - x (complement).

This is precisely the algebra of stochastic computing (Gaines 1967), realized in radiation rather than in shift registers.

**Theorem (feed forward universality).** For any continuous f : [0,1] → [0,1] and any ε > 0 there is a *feed forward* circuit of the three routine gates whose output stream has rate B_n[f](x) λ with sup_x |B_n[f](x) - f(x)| < ε, where

> `B_n[f](x) = Σ_k=0ⁿ C(n,k) xᵏ (1-x)ⁿ⁻ᵏ f(k/n)`

is the degree n Bernstein polynomial of f.

*Proof.* The Bernstein coefficients β_k = f(k/n) lie in [0,1] because f does. Draw n independent time slices of the input stream (independence by Section 5.1); the number k of occupied slices is Binomial(n, x). Use k to select, by a MUX tree, a reference stream of rate β_k λ (a thinned aperture constant). The output occupancy is 𝔼[β_K] = B_n[f](x) by construction, and B_n[f] → f uniformly (Bernstein 1912), with error O(‖f''‖_∞ / n) for smooth f. Every element used is a routine gate. ∎

The synthesis of arbitrary polynomials in this form is the stochastic logic architecture of Qian and Riedel (DAC 2008; IEEE Trans. Computers 60, 93 (2011)), imported here wholesale: their shift register Bernoulli sources are replaced by thinned decay streams that no circuit had to generate.

**What the keystone actually buys.** The construction is feed forward and memoryless: it approximates functions, it does not iterate them. Three things remain locked behind the threshold gate with gain: *recurrence* (closing loops without signal death requires Γ_eff ≥ 1), *restoration* (composing unbounded depth requires levels that do not degrade), and *memory coupled dynamics* (Turing completeness requires state that the computation itself rewrites). The honest hierarchy is therefore: function approximation and Monte Carlo estimation are keystone free; open loop inference is keystone free; anything with a feedback loop crossing a gain deficit is not. This sharpens both kill criteria: even a total failure of Phase B leaves a machine that evaluates arbitrary continuous functions and integrals by physics alone. The construction is verified numerically, gate by gate, in [/transport](../transport/results.md).

**Cost accounting.** Precision still obeys Section 5.6 at every stage: a depth d Bernstein circuit read to b bits consumes O(d 2²ᵇ) source events per evaluation, and the degree n needed scales as O(‖f''‖/ε). Nothing here is fast. It is merely universal, free of the keystone, and running on decays.

---

## 7. Aging invariance: correctness does not decay

A sealed source decays; the machine built on it slows. This section proves that a properly designed machine slows *without becoming wrong*, which is the mathematical heart of self sustainment.

**Setup.** Let every stream in the machine derive from one source of activity λ(t) = λ_0 2^(-t/T), so all rates scale together by s = λ(t)/λ_0. Define the coincidence degree deg(r) of a signal: a thinned stream has degree 1; a coincidence output has deg = deg_1 + deg_2 (its rate is 2τ_w r_1 r_2); MUX and absorption preserve degree (convex combinations and survival fractions of like degree streams).

**Theorem (degree homogeneity).** Under global scaling λ → sλ, every signal of degree k transforms as r → sᵏ r. Consequently any quantity formed as a *ratio of like degree signals* is invariant, and any decision made by comparing like degree signals is invariant, for all s > 0.

*Proof.* Induction over the circuit. Thinning multiplies a degree k signal by a constant; coincidence maps (s^(k_1) r_1, s^(k_2) r_2) ↦ 2τ_w s^(k_1 + k_2) r_1 r_2; MUX and absorption are linear with constant coefficients. Ratios of equal powers of s cancel. ∎

**Design rule (boxed in one line).** *Compare like degree only with like degree.* A circuit that thresholds a degree 2 coincidence signal against a degree 1 reference is correct on the day it ships and drifts as 2^(-t/T) thereafter; the same circuit thresholded against a degree 2 reference is correct until the source is gone. Homogenization costs one gate per reference path and buys immunity to the only aging mechanism the substrate has.

**Corollary 1 (the sampler does not age).** The Gibbs acceptance σ(u_k) of the sampling tier depends only on occupancies z_j ∈ \0,1\ and dimensionless weights, never on absolute rates; the stationary law p(z) ∝ exp(½ zᵀ W z + bᵀ z) is therefore exactly activity invariant. Aging rescales only the event clock: mixing time in wall clock seconds grows as 2^(+t/T).

**Corollary 2 (the aging law of a sealed machine).** A degree homogeneous machine of half life T delivers throughput C(t) = C_0 2^(-t/T) at unchanged accuracy, with no recalibration, no trimming, and no reference standard other than itself. Its performance at end of mission is known on the day of manufacture to Poisson precision. No battery powered computer can state its own end of life curve in closed form; this one can.

### 7.1 The homogenization procedure

The theorem becomes a construction method in three steps, and the method is machine checkable ([`transport/degree_check.py`](../transport/degree_check.py)):

1. **Label.** Propagate degrees through the circuit by the induction rules: thinning and absorption preserve degree, coincidence adds the degrees of its inputs, MUX requires (and preserves) equal degree inputs.
2. **Detect.** Flag every comparator, threshold, or MUX whose inputs carry unequal degrees. Each flag is a latent aging defect: the decision it guards will drift as 2^(-Δ k t/T) for a degree mismatch Δ k.
3. **Repair.** Raise the lower degree side by coinciding it with a reference stream: a full open thinning of the same source (value ≈ 1, degree 1). Semantically this multiplies by unity; dimensionally it raises the signal's degree by one. Repeat Δ k times. Each repair stage costs one coincidence volume and the usual variance bill of Section 10.1, and buys exact invariance under global activity scaling.

The procedure terminates (degrees are finite nonnegative integers), never changes a circuit's meaning at the ship date activity, and converts "correct today" into "correct until the source is gone." Layout tools should run it the way silicon tools run design rule checks; the checker does exactly this on a circuit netlist and demonstrates, by simulation, an inhomogeneous comparator flipping its decision at half activity while the repaired circuit holds.

---

## 8. The boundary: translating compute in and out

The charter forbids conventional electronics *inside* the loop; it says nothing about the skin. This section is the theory of the skin: how radiation native results become currents, counts, and spectra, and how external problems become apertures, velocities, and fields, with the price of every conversion stated.

### 8.1 Outputs

1. **Counts (digital).** A boundary detector converts a rate r to counted quanta; the precision law prices it: b bits per read costs 2²ᵇ counts, so a boundary budget λ_B (detected events per second) supports an output bandwidth f_out = λ_B / 2²ᵇ. At λ_B = 10⁷ s⁻¹ detected: about 150 reads per second at 8 bits, 40,000 at 4 bits. Precision is purchasable per port, per read.
2. **Current (analog).** A photovoltaic or betavoltaic junction at the boundary converts a quantum rate to I = e G r (G the carrier yield per quantum). The shot noise of I *is* the same Poisson limit in a different unit; nothing is gained or lost in the conversion, which is the correct sanity check.
3. **Spectrum (energy division multiplexing).** Distinct isotope lines are orthogonal channels through one physical window: a boundary spectrometer with resolving power to separate N_E lines reads N_E parallel ports simultaneously. Position adds N_x pixel ports; arrival time adds N_τ resolvable bins per mean interval.
4. **The per quantum ceiling.** One detected quantum distinguishable among N_E N_x N_τ classes carries at most log_2(N_E N_x N_τ) bits. A pixelated CZT boundary (N_E ≈ 10² lines, N_x = 256 pixels, N_τ ≈ 10³ timing bins) ceilings near 24 bits per detected quantum; realized mutual information sits below this, but the ceiling sets the design target: *spend the decay budget on distinguishable quanta, not on more quanta.*

### 8.2 Inputs

1. Apertures (mechanical or magnetic shutters): set thinning fractions x; slow (ms and up), absolute, zero power at rest. The program counter of the stochastic tier.
2. **Doppler drives.** A resonant channel detunes by one natural linewidth at v = c Γ/E: for ⁵⁷Fe, 0.097 mm/s. Piezoelectric velocity transducers (the ordinary Mössbauer drive, seventy years of practice) modulate resonant transmission fully at kHz to MHz rates: the fast input port, writing waveforms directly into cross sections.
3. **Zeeman programming.** An external field shifts hyperfine components by of order 0.1 μ_N B: for ⁵⁷Fe about 0.7 natural linewidths per tesla, enough to move a resonant channel on or off a line with ordinary coils, *through a sealed wall, with no penetration*. Weights become field maps: the machine is reprogrammed the way an MRI shims, from outside.
4. Beam injection through thin windows (X ray, VUV, or neutron): the high bandwidth port when a penetration is acceptable.

### 8.3 The no penetration principle

Together 8.1 and 8.2 permit a machine whose enclosure is never breached: problems enter as *fields and motions* (Zeeman maps, Doppler waveforms, aperture settings through magnetic couplings), answers leave as *glow* (the boundary emission spectrum, read by any external spectrometer or diode). Input by field, output by light, power by decay: the complete unit is specified in [transistor/SEALED.md](../transistor/SEALED.md).

---

## 9. The nuclear lamp: closing the bandwidth gap from inside

The sealed unit's failure to write its own memory ([transistor/SEALED.md](../transistor/SEALED.md), Section 3) has a specific anatomy: an *atomic* light source (an excimer continuum, 10¹⁴ Hz wide) was aimed at a *nuclear* line (10⁻⁴ Hz wide), and the overlap integral ate eighteen orders of magnitude. The fix is not a brighter lamp. It is to notice that the mismatch is a property of atomic light, and that a sealed decay inventory contains emitters that are not atomic.

### 9.1 The bandwidth matching principle

The pumping rate of an absorber by a source is R = ∫ σ(ν) φ_ν dν, and for a source of bandwidth Δν_s delivering flux φ onto a line of width Γ, R ∼ φ σ_0 (Γ/Δν_s) when Δν_s ≫ Γ. The figure of merit is the bandwidth ratio, and it is binary in practice:

- atomic sources (thermal, excimer, scintillation, even most lasers) have Δν_s/Γ ≳ 10¹² against nuclear lines: dead, per the arithmetic already published;
- **nuclear sources emit nuclear lines.** A radioactive parent that decays *into* the working transition emits quanta at exactly the resonant energy with exactly the natural width (recoil free fraction permitting): Δν_s/Γ = 1 by construction. This is not a proposal; it is the operating principle of every Mössbauer source since 1958. ⁵⁷Co embedded in a rhodium foil *is* a 14.4 keV lamp with a 10⁻⁸ eV linewidth: the narrowline internal source, sitting in catalogs for seventy years.

The design consequence for the ampoule is one sentence: the trim layer's resonant channels must be driven by embedded parent isotopes of their own working transitions, never by the broadband core. The core remains power, clock, and entropy; the parents are the machine's monochromatic light plant, one line per channel. Standard matched pairs, all demonstrated: ⁵⁷Co → ⁵⁷Fe (14.4 keV), ¹¹⁹ᵐSn → ¹¹⁹Sn (23.9 keV), ¹⁵¹Sm → ¹⁵¹Eu (21.5 keV), ¹⁸¹W → ¹⁸¹Ta (6.2 keV).

### 9.2 Radiogenic feeding: writing without photons

The second nuclear channel skips light entirely: some parents decay *directly into the metastable state*. The canonical case is the machine's own memory isotope: about 2 percent of ²³³U alpha decays populate ²²⁹ᵐTh, which is how the isomer's radiation was first detected. A crystal doped with ²³³U therefore maintains a standing isomer population with no laser and no lamp, at equilibrium n_m = 0.02 λ_233 N_233 τ_m: computable, self replenishing, and proven physics. Numbers in [`sealed_results.md`](../transistor/sealed_results.md): at 10¹⁷ ²³³U per cm³ the standing population is of order 2×10⁵ isomers per cm³. What radiogenic feeding does *not* provide is addressing: it writes everywhere at once, a bias, not a bit. It supplies the resonant reference ensemble (a carrier the trim layer can modulate), and it is the existence proof that the sealed unit can hold excited nuclear state without any penetration; the addressed write is what remains.

### 9.3 Resonance addressing: the MRI move

Addressing is the third piece, and magnetic resonance imaging already solved it in a different spectral register: flood the volume with a narrowline drive, and let a field gradient decide which voxel is on resonance. The trim layer's Zeeman tuning becomes spatial selection: with line sensitivity dE/dB and gradient G = dB/dx, the addressable resolution is

> `δ x = Γ/((dE/dB) G).`

The sensitivity is set by the linewidth, which makes the ultranarrow lines the easy ones. For ⁵⁷Fe (Γ = 4.7×10⁻⁹ eV, about 0.7 linewidths per tesla at a deliberately conservative placeholder moment of 0.1 μ_N) gradients of tesla per centimeter are needed: hard. For ¹⁸¹Ta (6.2 keV, t½ = 6.05 µs, Γ = 7.5×10⁻¹¹ eV) the same placeholder buys about 40 linewidths per tesla, and the *measured* moments (μ_g = 2.37 μ_N, μ_e ≈ 5.2 μ_N) make the stretched hyperfine components an order of magnitude more sensitive still, so every field figure in this section is a floor, not an estimate, so a *millitesla* scale field moves a channel by a full linewidth, and modest gradients address millimeter voxels; its Doppler sensitivity, one linewidth per 3.6 µm/s, makes a whisper of a piezo a full modulation (and makes vibration isolation a real engineering line item, stated honestly). ¹⁸¹Ta is fed by ¹⁸¹W (121 d), a standard source; its 6 µs lifetime makes it not storage but a latch: a microsecond scale, field addressed, parent driven holding register, which is precisely the missing timing element between the 98 ns ⁵⁷Fe relay and the 630 s ²²⁹Th register. Known cost, stated plainly: the 6.2 keV transition is heavily conversion dominated and its recoil free fraction is small, so photon budgets are thin; the latch is real physics with an efficiency tax, not free.

### 9.3a The addressing procedure, made operational

The MRI move of 9.3 becomes a four step cycle:

1. Configure: establish the field map that puts exactly the intended channels on resonance. Two regimes exist and the distinction is the honest heart of the method:
   - **Discrete (per channel coils): the practical regime.** Each resonant foil carries its own small coil; millitesla class currents move a ¹⁸¹Ta channel by full linewidths (24 mT per Γ), so channel count is set by geometry, not field strength. This is the regime the [build note](../transistor/EMBODIMENT.md) specifies, and it is engineering triviality: sixteen channels are sixteen coils.
   - **Continuous (gradient voxel selection): the scaling regime.** Within one extended medium, a gradient G resolves δ x = Γ / ((dE/dB) G). For ¹⁸¹Ta: 24 cm at 0.1 T/m, 2.4 cm at 1 T/m, 2.4 mm at 10 T/m; for ⁵⁷Fe the same table reads meters, which is why the sensitive line owns this method. Ten tesla per meter is beyond whole body MRI hardware but not beyond pulsed millimeter scale printed gradient coils at ampere class currents; it is the identified engineering lever, not an assumption.
2. Illuminate: nothing to switch; the parent flood (9.1) is continuous, and only on resonance channels accept it.
3. Act: perform the routing, latching, or modulation within the state's window (the ¹⁸¹Ta mean life is 8.7 µs; with microsecond coil rise times the address cycle is of order 10 µs, a 100 kHz addressing rate per bank).
4. Deselect: relax the field map; detuned channels return to transparency.

Crosstalk is a chosen number, not a surprise: a neighbor detuned by δ linewidths absorbs the Lorentzian tail 1/(1 + 4δ²), so separations of 3, 5, and 10 linewidths leak 2.7 percent, 1.0 percent, and 0.25 percent respectively. On a shared sight line the distinguishable setpoint count is N = B_max(dE/dB)/(S Γ): about 7 for ¹⁸¹Ta at half a tesla of authority and S = 3, which is why shared line discrimination is the *multiplexing garnish* and per channel coils are the *meal*.

### 9.4 What remains open

Sections 9.1 to 9.3 upgrade the sealed machine from "no nuclear state at all" to: proven relays (ns), proven latch physics (µs, addressable), and a proven standing register population (minutes, unaddressed). The single remaining gap, now stated much more narrowly than "the bandwidth problem," is the addressed long retention write: either a parent fed, gradient addressed line with lifetime above seconds (a search the isomer catalog in [/gates](../gates/) can run: long lived isomers with Mössbauer class feeding parents), or a bright sub kHz source at 148.38 nm (the nuclear clock community's laser roadmap, arriving on its own schedule). That is Open Problem 6, sharpened.

---

## 10. The rate coded canon: everything that keeps stream computation honest

Four results complete the defensibility of the rate coded machine, each short, each load bearing.

### 10.1 The isolation lemma and the variance calculus

Stream circuits fail in exactly one way: reuse. If a stream feeds two paths that later recombine, products are biased: 𝔼[z z] = x ≠ x², and generally 𝔼[z_1 z_2] = x_1 x_2 + ρ σ_1σ_2 for correlation ρ. The cure is structural: by the independent increments property, disjoint time slices and independent thinnings of one source are exactly independent (Section 5.1), so the rule is: every fan out is a fresh thinning, never a copy. With the rule obeyed, the calculus is benign: each gate's output is itself a Bernoulli/Poisson stream whose *mean is exactly* the target function of the input means, so depth does not compound systematic error at all; an estimate from N slices has Var = p(1-p)/N ≤ 1/4N *at any depth*. Depth costs only budget: a depth d circuit read to b bits consumes O(d 2²ᵇ) events per evaluation. Error does not accumulate; only the bill does.

### 10.2 The annealing schedule, as one moving part

The sampler's temperature is a global scale on u_k, and u_k is built from weight carrying fluxes: one master aperture on the weight paths scales all of them, so the machine's temperature is a single mechanical dial. The Geman and Geman theorem (IEEE PAMI 6, 721 (1984)) then applies verbatim: a logarithmic cooling schedule T(k) ≥ c/log(1+k) converges in probability to the ground state, and any faster practical schedule inherits the usual guarantees on approximate optima. The ampoule anneals by turning one absorber, on a printed schedule, powered by a clockwork spring if need be. Asynchronous updates are not an approximation here: the Poisson event clock *is* Glauber dynamics, which is the setting the theorem wants.

### 10.3 Graceful degradation and self calibration

There is no bit to flip: a lost quantum perturbs a rate by one count in N, so single event upsets, the plague of conventional radiation adjacent electronics, do not exist as a failure class. Uniform losses (aging, uniform dose, detector fatigue) are global thinnings, absorbed exactly by degree homogeneity (Section 7). The residual hazard is *nonuniform* drift, one path fading faster than another, which breaks the like for like rule slowly; the counter is already onboard: a fixed nuclear line (the ²⁴¹Am 60 keV, or any parent line from 9.1) is a drift free standard against which every path's ratio can be re trimmed through the wall, MRI shim style. The machine carries its own meter stick, of nuclear invariance, at zero marginal cost.

### 10.4 Modules

Ampoules compose: each unit's boundary glow, filtered to a distinct emission line, is another unit's beam injection input (Section 8.2, item 4), so a rack of ampoules is a network with energy division multiplexed links, one line per edge, no shared electronics, and the aging theorem applying per module. Nothing about the theory is single vessel.

---

## 11. The compiler: from a problem to a piece of matter

Every result so far describes the machine's *instruction set*: the gates, the weights 𝒢, the registers. None answers the constructive question a user actually asks: given my problem, a specific weight matrix 𝒢*, what layout of matter realizes it? A computer without an answer to this is a plugboard with no wiring diagram. This section supplies the assembler, and it exists in three forms, verified end to end in [`transport/compiler_demo.py`](../transport/compiler_demo.py) (figure 14).

### 11.1 The forward map is differentiable, and its gradient is free

Freeze the cross sections (Section 5.3): transport is the linear operator 𝒢(s) = B (I - Q(s))⁻¹ C, where s_v is the survival (one minus absorption) at cell v, Q = diag(s) M is the cell to cell movement, B injects at input ports and C exits at output ports. The compiler needs ∂ 𝒢_io/∂ s_v for every port pair and every cell: naively O(V) transport solves, hopeless for a real layout. The adjoint identity collapses it to two:

> `(∂ 𝒢_io)/(∂ s_v) = φ_i(v) ψ_o(v)`

the forward visit density φ_i = B_i (I-Q)⁻¹ (how often a photon entering port i visits cell v) times the importance ψ_o(v) (the probability that a photon leaving v eventually exits at port o), which is the *adjoint* flux ψ = M(I-Q)⁻¹C + C. One forward solve gives all φ_i; one adjoint solve gives all ψ_o; their outer product is the entire Jacobian of the whole weight matrix with respect to the whole layout. This is not a new trick: it is the importance function reactor physicists have computed since the 1950s (Ussachoff 1955), it is what shielding optimizers already use, and it is, exactly, backpropagation. The demo verifies the boxed formula against finite differences to a worst relative error of 9×10⁻⁷, machine precision.

### 11.2 Way A, full custom: grind the problem into the geometry

With the gradient in hand, compilation is optimization: descend ½‖𝒢(s) - 𝒢*‖² over the cell survivals s_v ∈ [s_min, s_max] (a plate that is mostly transparent, selectively absorbing), then quantize s_v to a fabricable absorber thickness map, the etched channel plates of the [build note](../transistor/EMBODIMENT.md). Three properties make this the flagship route:

- **Nonuniqueness is freedom.** 𝒢 has vastly more cells than matrix entries, so the preimage of 𝒢* is a high dimensional manifold; the compiler needs *any* point on it, and the slack is precisely what absorbs fabrication tolerance and hosts secondary constraints. The demo recovers a feasible random 4×4 target to a worst weight error of 0.65 percent.
- **Constraints are first class.** A demanded crosstalk kill (force 𝒢_io→0 for a chosen pair) is one penalty term; signed weights compile to complementary on/off resonance channel pairs (Section 5.3); the degree homogeneity rule (Section 7.1) is a compile pass over the result. The demo shows the honest edge too: killing one channel of a *diffusive* fabric while preserving its neighbors is over constrained because the paths physically overlap, and the compiler returns the optimum of that trade rather than a fiction, quantifying exactly how much collimation the target really needs.
- It is the reactor perturbation formula, so it inherits sixty years of validation and, for a real geometry, runs in MCNP or OpenMC adjoint mode with no new physics.

### 11.3 Way B, the crossbar: rent a universal fabric

Fabricate once as a collimated grid of independent sight lines, each carrying one matrix entry, weights set by aperture transmission T_io. Compilation is then not optimization but arithmetic: T_io = 𝒢*_io/𝒢^(fab)_io, exact to machine precision for any target under the fabric's open ceiling, and reprogrammable in the field by moving apertures, no refabrication. The price is flux: dedicated sight lines do not share paths, so photon budget per channel falls as the channel count grows. This is the FPGA to Way A's ASIC, and the two are endpoints of one axis: Way A spends design effort to buy density, Way B spends density to buy instant reprogrammability.

### 11.4 Way C, self calibration: tune the glow through the wall

Neither route above needs the *inside* of a sealed unit once built, because the boundary already emits 𝒢 (the glow) and the wall already admits field trims (Section 8.2). So a sealed ampoule is compiled onto its instance from outside by simultaneous perturbation stochastic approximation (Spall 1992): perturb *all* trim fields at once by a random sign vector, measure the loss twice (Poisson noisy counts of the boundary spectrum), and step against the two point difference. The cost is two measurements per iteration regardless of how many trims exist, and it needs no model of the device and no gradient. The demo drives all 144 cell trims to convergence under native Poisson noise. This is the routine that turns the aging theorem's promised self calibration (Section 10.3) into an algorithm: the machine is re compiled onto its drifting self, forever, using only its own light.

**The three are one workflow.** Way A designs the plate; Way B is the reprogrammable alternative when flux is cheap and edits are frequent; Way C trims whatever was built and keeps it trimmed. Together they are the missing assembler, and with them the phrase "the problem is ground into the geometry" stops being a slogan and becomes a function you can call.

---

*Sections 1 through 3 are the referee armor: every known way a working gate quietly dies, written down with its inequality. Section 4 is the existence proof that the model survives them all at one scale. Sections 6 through 10 are the machine that needs no keystone, no calibration, and no wires. Section 11 is the compiler that turns a problem into a piece of matter. What remains is the search itself.*
