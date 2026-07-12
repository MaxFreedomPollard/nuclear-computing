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

*Sections 1 through 3 are the referee armor: every known way a working gate quietly dies, written down with its inequality. Section 4 is the existence proof that the model survives them all at one scale. The rest is the search for that survival at a scale you can hold.*
