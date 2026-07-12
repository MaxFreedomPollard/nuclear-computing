# The build note: one ampoule, fully specified

*A note accompanying [the reference transistor](README.md): the assembly grade specification of the worked unit of [SEALED.md](SEALED.md), written so that a competent instrumentation group could quote it. Where a number is a design choice rather than a computed quantity, it says so; every computed quantity traces to [`sealed_unit.py`](sealed_unit.py) or [/theory](../theory/THEORY.md).*

## 0. The unit specified

A sealed cylindrical vessel, outer envelope **90 mm diameter × 170 mm, about 4 kg**, delivering the performance of SEALED.md Section 8: a 64 site annealer at about 38,000 independent samples per second at sealing, 8 bit reads at 153 per second, halving in speed every 28.8 years at constant correctness. License class: institutional (GBq sealed sources); everything below assumes an institution that routinely handles mCi to Ci sealed sources.

## 1. Shell by shell, from the center out

### 1.1 Core capsule (the source and lamp)

- **Source**: 1 GBq of ⁹⁰Sr/⁹⁰Y as strontium titanate ceramic (SrTiO₃, the standard immobilized form used in sealed sources), sintered pellet 8 mm diameter × 10 mm, in a doubly encapsulated 316L stainless inner capsule per ISO 2919 sealed source practice.
- **Lamp cell**: the capsule sits on axis inside a 30 mm diameter × 40 mm chamber filled with research grade krypton at **5 bar** (design choice: pressure trades excimer conversion efficiency against window load; 2 to 10 bar is the sensible bracket). Chamber walls are VUV reflective (MgF₂ overcoated aluminum) except for the output apertures; MgF₂ windows (transmitting at 148 nm) couple lamp light to the compute shell where broadband illumination is wanted, and block it elsewhere.
- The core supplies, per SEALED.md: 181 µW deposited power, the Poisson clock and entropy, and broadband VUV for the saturable channels. It supplies **no** resonant nuclear drive; that is the trim ring's job (Section 1.3).

### 1.2 Compute shell (the weights)

- A stack of **etched channel plates**: 40 mm outer diameter borosilicate discs, each carrying a photolithographically etched pattern of through channels and blind cavities, with tungsten aperture inserts (fixed thinning fractions) and lead septa (inhibitory blocking). The stacked pattern is the Green's function $\mathcal{G}$ of the programmed instance: **the problem, ground into geometry** at manufacture.
- 64 interaction sites (scintillating cavities, 2 mm cells of plastic scintillator or CsI, one per logical site), coincidence pairs defined by shared sight lines through the plates.
- Design rule enforced at layout time: every compared path has equal coincidence degree (the homogenization procedure, [theory Section 7.1](../theory/THEORY.md), machine checkable with [`transport/degree_check.py`](../transport/degree_check.py)).

### 1.3 Trim ring (the programmable weights and latches)

- **Resonant channels**: 16 channels (design choice; scales trivially). Each channel is a sandwich: parent source, flight gap, absorber foil, sight line into the compute shell.
  - ⁵⁷Fe channels: absorber is 95 percent enriched ⁵⁷Fe foil, 1 to 2 µm, on 25 µm beryllium backing; parent is ⁵⁷Co electrodeposited in rhodium foil, 1 mCi class per channel (commercial catalog items in exactly this form).
  - ¹⁸¹Ta latch channels: 12 µm natural Ta foil (natural abundance is 99.99 percent ¹⁸¹Ta); parent is ¹⁸¹W, 121 day half life, so latch channels are the one **serviceable consumable**: the design lifetime of a trim ring loading is two years (six parent half lives), after which latch contrast has decayed 60 fold and the ring is exchanged at a hot cell, or the unit is operated latch free (the sampler does not need them).
- **Per channel tuning coils**: 200 turn coils on the outside of the pressure wall, one per channel, delivering 0 to 50 mT at the foil (≈ 2 ¹⁸¹Ta linewidths of Zeeman shift: full on/off authority; ⁵⁷Fe channels use the piezo instead). Coil formers are machined into the outer shield so **no conductor penetrates the wall**.
- **Doppler ring**: an annular piezoelectric actuator (PZT stack, ±30 µm/s velocity authority, kHz bandwidth) carrying the ⁵⁷Fe foils; ±30 µm/s is ±0.3 linewidths for ⁵⁷Fe and ±8 linewidths for ¹⁸¹Ta, so the same ring modulates both families. Drive waveforms enter as magnetic flux through the wall (a sealed voice coil coupling), keeping the no penetration rule.
- **Vibration budget**: the ¹⁸¹Ta linewidth is 3.6 µm/s. The trim ring mounts on a machined elastomer stage with a specified transmissibility knee below 10 Hz; ambient floor vibration (typically 0.1 to 1 mm/s in buildings) must be attenuated by 60 dB at the foils. This is the single most demanding mechanical specification in the unit, it is the price of the ¹⁸¹Ta sensitivity, and it is stated here rather than discovered later.

### 1.4 Boundary (the mouth)

- **Counting ring**: 24 SiPM tiles (6 × 6 mm) on plastic scintillator paddles facing the compute shell, plus 4 CZT spectroscopic pixels (5 × 5 × 5 mm) for the energy division ports (channel plan in [gates/edm_channels.md](../gates/edm_channels.md)).
- **Reference pip**: a 10 µCi ²⁴¹Am seed (exempt quantity) mounted in view of the CZT pixels: the 59.5 keV line is the onboard energy and drift standard (theory Section 10.3).
- **Power**: a ⁶³Ni betavoltaic stack (100 cm² total active area, GBq class loading) supplying of order 1 µW electrical; the counting ASIC (off the shelf ultra low power counter/discriminator silicon) duty cycles within that budget. Readout leaves the unit as modulated glow: an LED free optical port driven passively by the scintillation itself for the counting channels, and the CZT spectral ports read through a thin (2 mm) aluminum spectroscopy window, the one deliberate thin spot in the shield.
- The boundary is *outside the loop* per the charter, and inside the seal: the machine pays for its own mouth from the same decay inventory.

### 1.5 Shield and shell

- Inner beta stop: **12 mm PMMA** (stops the 2.28 MeV ⁹⁰Y endpoint betas in low Z material, minimizing bremsstrahlung: standard ⁹⁰Sr practice).
- Bremsstrahlung attenuation: **4 mm lead** jacket outside the PMMA.
- Pressure and containment wall: 3 mm titanium, electron beam welded; helium leak checked to sealed source standards.
- External surface dose target: standard sealed source instrument levels at contact; the shield stack above is sized for that with margin, and the final numbers are a health physics calculation the builder must certify (stated as an obligation, not assumed away).

## 2. Assembly sequence

1. Fabricate and stack the channel plates; verify the etched $\mathcal{G}$ against the instance specification optically (the plates are transparent to visible light; the check is a photograph).
2. Run the degree checker on the as built layout; homogenize any flagged comparison with reference apertures (spare blind channels are provided in the plate design for exactly this).
3. Load the trim ring foils and parent sources in a hot cell; verify each channel's resonance dip on the bench with its own coil and the piezo (a one hour Mössbauer scan per channel).
4. Mount trim ring on the isolation stage; verify the vibration budget with the ring live.
5. Install the boundary ring, betavoltaic stack, ASIC, and the ²⁴¹Am pip; calibrate CZT channels against the 59.5 keV line.
6. Fill and seal the krypton lamp cell around the previously encapsulated source capsule (the only step requiring the GBq source present; everything before it is cold work).
7. Close the titanium wall; weld; leak check.
8. Commission: (a) verify the Poisson floor (dead time corrected counting statistics at every SiPM), (b) run the annealing schedule on a known instance and compare the sampled distribution to the digital twin prediction ([/simulator](../simulator/)), (c) record the birth certificate: activity, per channel resonance positions, and the full transfer matrix, all of which the aging theorem then propagates for the life of the unit.
9. Ship with the birth certificate; the unit's performance at any future date is that document plus $2^{-t/T}$.

## 3. Operating procedure

- **Program**: energize tuning coils to the instance's weight trim map (a static current vector, held by external supplies or permanent magnet shims for fixed deployments); load the Doppler waveform table.
- **Anneal**: run the one dial schedule (theory Section 10.2) on the master aperture coil; logarithmic profile, duration set by the required approximation guarantee.
- **Read**: counting ports stream rate words at the chosen precision (153 per second at 8 bits on the birth budget); spectral ports stream the energy multiplexed channels; the ²⁴¹Am line rides along as the per read calibration tick.
- **Re trim** (monthly or on drift alarm): compare each channel's ratio to the pip; correct coil currents. Ten minutes, no penetration, no interruption of sampling.

## 4. Failure modes and what they cost

| failure | symptom | consequence | mitigation |
|---|---|---|---|
| parent decay (¹⁸¹W) | latch contrast fades on the 121 day half life | latches only; sampler unaffected | scheduled ring exchange, or latch free operation |
| vibration excursion | ¹⁸¹Ta channels smear | latch addressing errors | accelerometer interlock gates latch operations |
| scintillator darkening | counting efficiency drift, nonuniform | breaks degree homogeneity slowly | ratio re trim against the pip (Section 3) |
| SiPM death | one port lost | port loss, not corruption (theory 10.3) | 24 way redundancy; remap ports |
| krypton leak into vessel | lamp dimming, pressure alarm inferred from saturable channel drift | soft threshold operating points shift | channels are re trimmed; unit derates, does not fail |
| the one unfixable | source decay | throughput halves per 28.8 years | by design: correctness is invariant (theory Section 7); print the curve on the label |

*Nothing in this note is exotic to a nuclear instrumentation shop: ISO sealed sources, Mössbauer foils and drives from catalog, channel plates from any microfluidics fab, SiPMs and CZT from the PET industry. The novelty is entirely in what the assembly is for. That is the point.*
