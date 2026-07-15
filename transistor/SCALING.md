# The ENIAC ledger: what improves, by how much, and what it hits

*A note accompanying [the reference transistor](README.md): how each part of the unit improves, and what it hits.*

Every computing substrate that matters began contemptible. ENIAC (1945) performed five thousand additions per second, drew 150 kilowatts, weighed twenty seven tons, and lost a vacuum tube every day or two: thirty joules per operation, a number so bad that no extrapolation from it predicted the transistor era, because extrapolation was never the point. The point was that the machine's weaknesses lived in *separately improvable components*, each with a physical lever and a distant ceiling. Tubes became transistors became integrated circuits; delay lines became core became DRAM; plugboards became stored programs. Nobody improved "the computer." They improved its parts.

This document is that ledger for the nuclear machine: every component as it exists in this repository today, the lever that improves it, the ceiling physics imposes, and whose industrial curve it rides. The discipline it enforces is the one the user of this argument must accept in both directions: today's numbers are small, and none of them is stuck.

## The comparison that sets the tone

The 1 GBq ampoule of [SEALED.md](SEALED.md) draws about 38,000 independent samples per second from 181 µW of deposited decay power: roughly 5 nanojoules per sample against ENIAC's 30 joules per operation, ahead by nine to ten orders of magnitude on the day it is sealed, unpowered, with no moving electrons it did not inherit from nuclei. The machine does not begin where ENIAC began. It begins past it, and the ledger below says where it goes.

## The ledger

| component | 1945 analog | in this repository today | the lever | the ceiling | headroom |
|---|---|---|---|---|---|
| source activity | more tubes, bigger rooms | 3.7×10⁴ decays/s (exempt benchtop); 10⁹ (ampoule) | licensing tiers: GBq institutional, TBq industrial irradiator class | pile up: activity must be spread over n ≳ λτ_d sites (THEORY.md 3.2); self absorption | ×10³ to 10⁹ |
| coincidence window | tube switching speed | 100 ns (plastic scintillator, conservative) | LaBr₃ at ~1 ns; time of flight PET silicon photomultipliers at ~200 ps; Cherenkov timing near 30 ps in research devices | nuclear level lifetimes (fs) are far below any electronics | ×10³ |
| collection | hand wiring | ~1 percent solid angle (benchtop) | 4π enclosure geometries; photodetector efficiency ~50 percent; total body PET raised system sensitivity ~40× in one product generation | unity | ×10² |
| boundary channels | punch cards | 2 silicon photomultipliers | million channel, hundred picosecond counting ASICs exist off the shelf (high energy physics and PET readout) | per channel dead time | ×10⁴ to 10⁶ |
| memory retention | mercury delay lines → core | none sealed; 98 ns ⁵⁷Fe relay | the isomer ladder: ¹⁸¹Ta latch (6 µs, field addressed, parent fed: THEORY.md 9.3), ²²⁹Th register (630 s) as VUV sources brighten on the nuclear clock community's roadmap | the catalog itself: 1870 isomers to 31 years and beyond ([/gates](../gates/)) | ×10¹³ in retention |
| addressing | plugboards | mechanical apertures, hand placed | the compiler (THEORY.md 11): adjoint synthesis of the plate layout, plus Zeeman gradients (42 linewidths per tesla on ¹⁸¹Ta: millitesla addressing), Doppler waveforms (µm/s), energy division multiplexing (~10² lines per window) | gradient strength over linewidth, δ x = Γ/((dE/dB) G) | ports ×10² per volume |
| interconnect | point to point wire | isotropic emission, 4π loss | coherent nuclear forward scattering (directional by physics, routine at synchrotrons); grazing and Laue optics at keV | speed of light, no dispersion medium needed | recovers the fan out tax (THEORY.md 1.3) |
| randomness | (decades of pseudorandom repair) | Poisson exact | none needed: born at the ceiling | information theoretic perfection | ×1 |
| synthesis theory | ballistics tables by hand | Bernstein circuits, annealing schedules, degree homogeneous design (THEORY.md 6, 7, 10), and the adjoint compiler (THEORY.md 11) that turns a weight matrix into a plate layout | the stochastic computing literature (2008 onward) and sixty years of reactor perturbation theory import wholesale | BPP without the keystone; BQP with Tier 2 | compounding |

Three structural observations the table compresses:

1. **The machine rides other industries' curves.** The coincidence window, collection, and boundary rows are the PET and high energy physics detector industry, which improves them for its own reasons at billions of dollars a year. The memory row is the nuclear clock community's laser program. The source row is the isotope production industry. Like early silicon riding radar and missile money, the nuclear machine's components are being improved by people who have never heard of it.
2. **The low compute methods are the point, not the placeholder.** Counting, thinning, and coincidence look primitive the way tube flip flops looked primitive. But the precision law makes even 4 bit ports genuinely useful (39,000 reads per second on a modest boundary budget), the Bernstein construction makes the primitive gate set universal for continuous functions, and every row above multiplies *those same primitives*. Improving a component never strands the architecture, because the architecture was stated in component independent form: the two governing equations do not know what a scintillator is.
3. **One aggregate, honestly assembled.** Take catalog technology only: a TBq class core (10¹² decays/s, industrial licensing), 1 ns windows (accidental rates scale as τ_wλ², so a 100× shorter window buys 100× more usable activity at fixed accidental fraction), 30 percent collection, and modern counting ASICs. The sampler ceiling moves from the ampoule's 4×10⁴ to order 10¹⁰ independent samples per second per module, with 8 bit boundary reads in the millions per second: five to six orders of magnitude over today's worked unit with zero new physics, before the keystone, before Tier 2, before any discovery. That is the transistor free portion of the curve. The keystone, if Phase B ever fills the socket, is not a rung on this ladder; it is a different ladder.

## What this ledger is for

When a reader objects that 38,000 samples per second is a toy, the ledger is the reply: *every* substrate's first machine was a toy, the toy's components each carry named levers with named ceilings, most of the levers are being pulled by other industries at their own expense, and the theory upstairs was deliberately written so that no lever invalidates it. The correct comparison for a new substrate is never against the incumbent's present; it is against the incumbent's own first machine, adjusted for who pays for the parts. Against ENIAC, this machine is nine orders ahead, sealed, and aging on a schedule it can print on its own label.
