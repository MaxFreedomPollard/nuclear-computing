# The metabolism note: how the machine powers itself

*A note accompanying [the reference transistor](README.md): the five conversion chains by which a decay inventory feeds every load the machine has, with numbers traceable to the ledger in [`sealed_results.md`](sealed_results.md).*

## 0. The fact that reframes the whole question

The deepest self powering property is that the computation needs almost no *converted* power at all. In a conventional computer, every operation is electrons pushed through resistance by a supply. Here, **the compute core eats decays raw**: every proposal, every coincidence, every thinning is paid for directly by a decay event, at 100 percent "conversion" because there is no conversion. The chains below exist only to feed the *periphery*: the boundary readout, the trim, and the latches. The brain is metabolically free; only the mouth and the hands need a diet.

## 1. The five chains

| chain | physics | scale (per GBq class inventory) | feeds | provenance |
|---|---|---|---|---|
| **direct charge** | beta emitter on an insulated electrode accumulates charge: current $= A e \approx 0.16$ nA per GBq, potentials to kilovolts | nA at kV; charges 10 pF to 1 kV in about a minute | **electrostatic actuation and holding**: aperture states latched by charge, zero current to hold | the oldest nuclear battery there is (Moseley, 1913) |
| **betavoltaic** | beta junction converts particle energy to current at a few percent | order 0.1 µW electrical per GBq of ⁶³Ni | the counting ASIC at the boundary, duty cycled | commercial product class for decades |
| **radioluminescent photovoltaic** | phosphor converts betas to light, photodiode converts light to current | order 0.01 to 0.1 µW per GBq through the double conversion | trickle loads, indicator functions | tritium betalights plus ordinary PV, both catalog items |
| **thermoelectric** | decay heat across a thermoelectric generator at 5 to 7 percent | needs Ci to kCi to matter: milliwatts to watts at rack scale (²³⁸Pu: 0.57 W thermal per gram) | multi ampoule racks, external cooling fans, anything hungry | every deep space probe since the 1970s |
| **self powered detectors** | rhodium or vanadium emitters generate their detection current from the capture reaction itself, no bias supply | signal current is the measurement | **the mouth senses for free**: counting elements that are their own battery | standard in reactor instrumentation (SPND) |

## 2. Load matching

The sealed ampoule's internal electrical loads, matched to chains:

- **Boundary counting ASIC** (microwatt class, duty cycled): betavoltaic. The match that closes the mouth's budget in [SEALED.md](SEALED.md).
- **Electrostatic aperture latches** (zero holding current): direct charge. A program state, once set, is held by trapped charge on an insulated electrode with the leakage time constant of good insulators (days to years), refreshed from the nanoamp trickle. This is the sealed machine's answer to "how do apertures stay put with no motor": they are charged, not driven.
- **Sensing** (the counting elements themselves): self powered detectors where the geometry permits; SiPMs on the betavoltaic budget elsewhere.
- **Trim coils and Doppler rings**: deliberately *not* on the internal budget; they are driven through the wall by external fields (theory 8.2), which is the no penetration principle doing double duty as power architecture. A field deployed unit with permanent magnet shims needs no trim power at all.
- **Rack scale ancillaries** (multi unit installations): thermoelectric, from the same inventory's heat.

## 3. The honest accounting

Every chain is a tax on the one ledger. A GBq class ⁹⁰Sr inventory deposits 181 µW; the chains convert single digit percent of the slice they are fed; the loads above fit inside single digit microwatts with room to spare, and the margin is computable per mission by the inequality of SEALED.md Section 1. Aging applies to everything equally, which is the saving grace: loads that scale with count rates shrink in exact proportion to the chains that feed them (degree homogeneity, applied to the power budget), so **a correctly matched metabolism never starves before the computation slows to meet it**. The one load that must be engineered against the curve rather than with it is the fixed overhead of the ASIC's sleep current, and that is a part selection problem, not a physics problem.

*Power, like randomness, is a place where this machine starts at an advantage so structural it reads like an error: the computation is powered before any engineer arrives, and the engineering consists of feeding the accessories.*
