# The ampoule: a sealed, self sustaining nuclear computer

*A note accompanying [the reference transistor](README.md): the sealed machine built from these units.*

The foundational document's machine still leans on the outside world in three places: lasers write its memory, electronics read its answers, and a wall socket powers both. This document designs those dependencies away and prices what remains. The result is the ampoule: a sealed vessel with no penetrations, powered, clocked, and randomized by its own decay inventory, programmed through its wall by fields, and read by its glow. Every claim is either derived in [theory/THEORY.md](../theory/THEORY.md) Sections 6 to 8, computed in [`sealed_unit.py`](sealed_unit.py) (which regenerates [`sealed_results.md`](sealed_results.md) and figure 11), or honestly marked dead.

## 1. What self sustaining means, exactly

A unit is self sustaining over a mission time τ_m if every subsystem's demand is met by the decay inventory alone at all times:

> `a_i λ_0 2^(-t/T) ≥ D_i for all i and all t ≤ τ_m,`

where a_i is the activity share allotted to subsystem i (entropy, weights, threshold traffic, boundary power) and D_i its demand at the specified performance. Because every term is Poisson statistics on a known decay curve, the ampoule's end of mission performance is computable on the day it is sealed (the aging law, THEORY.md Section 7): correctness is activity invariant by the degree homogeneity theorem, and only throughput decays, as 2^(-t/T).

## 2. Architecture: five shells, no penetrations

From the center outward (figure 11, panel A):

1. **Core: the source and its lamp.** An alpha emitter (²⁴¹Am for century missions, ²³⁸Pu for decades, ⁹⁰Sr/⁹⁰Y for power density) dispersed in a high pressure krypton cell. Alpha energy ionizes and excites the gas; Kr₂* excimers radiate the second continuum centered near 148 nm, a nuclear pumped VUV lamp with no filament and no supply. The same core furnishes the machine's clock and entropy (the Poisson stream) and its heat.
2. **Compute shell.** The gate medium: scattering and absorbing microstructure whose geometry *is* the weight matrix 𝒢, with coincidence volumes and saturable channels arranged per the transport theory. The problem is ground into the shell at manufacture, the way an ASIC's function is etched: a problem in a can.
3. **Trim layer.** Resonant channels (Mössbauer foils) whose detunings are set through the sealed wall: Zeeman coils outside the vessel shift lines (about 0.7 natural linewidths per tesla on ⁵⁷Fe, about 42 per tesla on ¹⁸¹Ta), and piezoelectric Doppler rings modulate them at kHz to MHz (THEORY.md 8.2). Each channel is driven at exactly its own linewidth by an embedded parent isotope (⁵⁷Co for ⁵⁷Fe, ¹⁸¹W for ¹⁸¹Ta: the nuclear lamp principle of THEORY.md Section 9), never by the broadband core; the ¹⁸¹Ta channels double as microsecond, millitesla addressed latches. The ampoule is fixed function in topology, field programmable in weights.
4. **Boundary: the mouth.** A scintillator and diode ring converts escaping quanta to counts and currents, and a betavoltaic layer harvests the decay budget to power that conversion. The boundary electronics are *outside the loop* per the charter, and inside the seal: the machine pays for its own mouth from the same inventory (about 180 µW deposited per GBq of ⁹⁰Sr/⁹⁰Y; a fraction of that, converted at betavoltaic efficiencies, runs microwatt class counting silicon, which exists).
5. **Shield and shell.** Passive. The only things that cross it are fields inbound and photons outbound.

## 3. The lamp that cannot write, and why that is worth publishing

The core's 148 nm continuum lands, remarkably, on the ²²⁹Th transition at 148.38 nm. It is tempting to conclude the ampoule writes its own isomer memory. The arithmetic says no, and the size of the no is the finding:

- A 1 GBq alpha core depositing 5.5 MeV per decay into krypton at 30 percent VUV conversion emits about 2×10¹⁴ photons per second near 148 nm: a bright lamp by any ordinary standard.
- Spread over the excimer bandwidth (about 10 nm, i.e. 1.4×10¹⁴ Hz), that is a spectral flux near 1 photon cm⁻² s⁻¹ Hz⁻¹.
- The nuclear line's integrated cross section is (λ²/2π) Γ_rad ≈ 2×10⁻¹⁵ cm² Hz. The excitation rate per nucleus is their product: about 3×10⁻¹⁵ s⁻¹, one write quantum per voxel of 10⁸ nuclei every five weeks.

The mismatch is the ratio of the lamp's bandwidth to the nuclear linewidth, about eighteen orders of magnitude, and no achievable activity closes it. The conclusion is structural, not incremental: broadband self pumping of neV lines is dead, and publishing this closes the most obvious "why not just..." a referee could raise.

The failure also points directly at its own repair, worked out in THEORY.md Section 9: the mismatch is a property of *atomic* light, and the inventory contains emitters that are not atomic. Parent isotopes emit their daughters' lines at natural width (the Mössbauer source principle, seventy years old): bandwidth ratio one, by construction. ²³³U decays feed ²²⁹ᵐTh directly (2 percent branch, no photons involved), maintaining a computed standing population of about 2×10⁵ isomers per cm³ in a doped crystal ([`sealed_results.md`](sealed_results.md)). And field gradients turn the trim layer into an addressing system on the MRI principle, with ¹⁸¹Ta the standout at 42 linewidths per tesla. What stays open, sharply now: the *addressed, long retention* write. Meanwhile the sealed unit computes in rates.

## 4. What the ampoule computes

Since the sealed unit cannot write isomer populations, its state lives where the aging theorem likes it best: in rates. The three routine gates on thinned streams form the stochastic computing algebra, and the Bernstein construction (THEORY.md Section 6) makes that algebra universal for continuous functions, feed forward, with no gain element anywhere. The ampoule is therefore, honestly:

- a Monte Carlo appliance: integrals, expectations, and Bayesian updates evaluated by physics, with accuracy priced by the precision law and immune to aging by degree homogeneity;
- an annealer for the Ising instance ground into its compute shell, field trimmed through the wall, sampling its Boltzmann law at a rate that halves each half life while the law itself never moves;
- not a stored program computer. The empty socket of [the reference transistor](README.md) is empty here too, and the ampoule is what the theory can seal *today*.

## 5. The inventory ledger

Deposited power and roles per GBq, computed in `sealed_unit.py`:

| isotope | half life | emission | deposited power per GBq | role in the ampoule |
|---|---|---|---|---|
| ³H | 12.3 y | β, 5.7 keV avg | 0.9 µW | gentle lamp (via phosphor), proven in sealed lights |
| ⁶³Ni | 100 y | β, 17 keV avg | 2.8 µW | betavoltaic boundary power, century missions |
| ⁹⁰Sr/⁹⁰Y | 28.8 y | β, 1.13 MeV per pair | 181 µW | power density: lamp + boundary harvest |
| ²³⁸Pu | 87.7 y | α, 5.6 MeV | 897 µW | the RTG choice: lamp and heat, decades |
| ²⁴¹Am | 432 y | α, 5.5 MeV + 60 keV γ | 888 µW | century lamp; the 60 keV line doubles as a built in spectral reference |

Entropy and clock cost almost nothing (any share of the stream suffices); the lamp and the mouth dominate the budget. Shares a_i are a design dial, not a constraint, until activities fall to where the boundary electronics starve, and that day is computable in advance.

## 6. Aging and mission

By Corollary 2 of the aging theorem: throughput C(t) = C_0 2^(-t/T) at constant correctness, provided the circuit is degree homogeneous (the design rule: compare like coincidence degree only with like). Mission planning is then one inequality per subsystem (Section 1). Figure 11 panel B draws C(t)/C_0 for the ledger's isotopes across a century: a ⁹⁰Sr ampoule delivers half its birth throughput at year 29 and an eighth at year 86; an ²⁴¹Am ampoule loses fifteen percent in a human lifetime. There is no other computer whose hundred year performance curve is a two parameter formula with laboratory grade constants.

## 7. The mouth, priced

The boundary translates by the theory of THEORY.md Section 8. For a detected boundary budget of 10⁷ events per second (a 1 GBq class core with percent level boundary collection):

- digital ports: f_out = λ_B / 2²ᵇ: about 150 reads per second at 8 bits, 2,400 at 6 bits, 40,000 at 4 bits (figure 11, panel C);
- analog ports: betavoltaic current proportional to rate, shot noise limited, same Poisson bound in different units;
- spectral ports: each distinct emission line in the machine is a separate simultaneous channel through one window (the computed channel plan, eight clean CZT channels from catalog sources, is [gates/edm_channels.md](../gates/edm_channels.md)); the ²⁴¹Am 60 keV line serves as a free onboard energy calibration;
- the ceiling: a pixelated spectroscopic boundary approaches 20 to 25 bits per detected quantum; the design target is always *more distinguishable* quanta, not more quanta.

Inputs cross the wall without holes: aperture settings by magnetic coupling, waveforms by Doppler rings, weight maps by Zeeman coils. The complete I/O surface is fields in, glow out.

## 8. A worked unit

A sealed cylinder, roughly a liter, one GBq of ⁹⁰Sr/⁹⁰Y at the core (181 µW deposited), krypton lamp shell, a 64 site compute shell with its Ising instance etched in, Zeeman trim coils outside the wall, CZT and diode boundary inside it:

- proposal budget: thinned streams totalling 10⁶ proposals per second across sites → order 4×10⁴ independent samples per second at birth (26 decays per sample, measured in [/simulator](../simulator/results.md));
- readout: 8 bit sample statistics at about 150 reads per second through the counting port, continuous analog anneal energy on the current port;
- at year 29: exactly half of all of the above, same answers;
- assembly grade specification: every shell, dimension, material, and procedure is in the [build note](EMBODIMENT.md); license class: GBq sealed sources are institutional (this is the tier between the exempt benchtop cell and the reactor gate of [the reference transistor](README.md)); the ampoule is a laboratory instrument, not a consumer object, and the document says so.

*The ampoule closes the loop the charter opened: a lump of structured matter, bathed in its own radiation, computing. Nothing enters but fields; nothing leaves but light; nothing inside it can be recalled, recharged, or corrected, and by the aging theorem nothing needs to be.*
