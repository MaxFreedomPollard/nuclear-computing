# The nuclear transistor: one unit of this computer, held in your hand

Every computing technology earns belief at the moment it can point to its unit: the one physical object that switches, stores, and can be tiled into a machine. For electronics that object is the transistor. This document is the answer to "what is yours?", and it gives the answer three times, because the same schematic exists today at three scales: a benchtop cell you could assemble this month from catalog parts, a crystal cell that is the program's target, and a reactor scale cell that already exists and proves the schematic closes. One drawing, three sizes ([figure 10](../figures/fig10_nuclear_transistor.svg)).

The unit is deliberately named a transistor and not a gate: a transistor is a *terminal device*. What makes a MOSFET buildable is not its physics but its pinout, the discipline of gate, source, drain, channel, and body. The claim of this document is that the nuclear cell has the same pinout.

## The pinout

| terminal | MOSFET | benchtop cell (today) | crystal cell (target) | neutron gate (proven) |
|---|---|---|---|---|
| **GATE** (control) | gate voltage | aperture position $\alpha$ | 148.38 nm trigger beam | control absorber position |
| **SOURCE** (supply) | supply rail | ¹³⁷Cs disk, 1 µCi | pump laser + source bath | driver source and neighbor leakage |
| **DRAIN** (output) | drain current | coincidence rate out | 8.4 eV fluorescence burst | leakage flux to next region |
| **CHANNEL** (state) | inversion charge | encoded rate $x\lambda$ | isomer fraction $n_m$ | neutron population |
| **BODY** (substrate) | silicon | scintillator volume | CaF₂ lattice | moderator block |
| **gain** | transconductance | none ($\beta \approx 1$) | **the empty socket: the keystone** | $1/(1-k)$, proven |

Read the last row left to right and you have the entire research program in one line: the benchtop cell works without gain, the crystal cell is complete except for the one socket this repository exists to fill, and the neutron gate has had gain since 1942.

---

## Scale 1. The benchtop cell: a probabilistic bit you can order this month

This is the p bit of the stochastic tier, and nothing in it awaits a discovery.

**The object.** An aluminum box the size of a deck of cards. Inside, in a line: a license exempt 1 µCi ¹³⁷Cs disk source (within the 10 CFR 30.71 Schedule B exempt quantity; about $120 from any isotope supplier), a tungsten shutter on a hobby servo (the thinning aperture, the GATE), a short lead collimator (the fixed weights), and two 10 mm cubes of EJ-200 plastic scintillator, each read by a silicon photomultiplier (the BODY and the readout). Per cell, about $300 to $400 in parts; the only shared infrastructure is a discriminator and counter, which in the first version is ordinary boundary electronics.

**The operation.** The disk emits its 662 keV line (via ¹³⁷ᵐBa) as a Poisson stream at $3.7\times10^4$ decays per second. The shutter thins it to $x\lambda$: the CHANNEL state is a rate, set mechanically, exactly the thinning theorem of Appendix B.1. Two cells aimed at a shared scintillator volume with a 100 ns coincidence window form the multiplier of the gate set; the survival form of that gate is verified to 0.4 percent in [/transport](../transport/results.md). Feed the discriminated output back to the next cell's servo and the network is the sampler of [/simulator](../simulator/results.md).

**The numbers.** At a thinned proposal rate of $10^4$ per second and the measured 26 decays per independent sample, one cell contributes about **385 independent samples per second**. An eight cell machine reproducing the digital twin instance fits in a briefcase and costs about $3000. It is slow, honest, and real: every random number in it was manufactured by a nucleus.

**What is electronics and what is not.** In this version the weighted sum is geometry, the randomness is nuclear, the state is a rate, and the threshold is a discriminator at the boundary. The purity claim of the charter is staged, not violated: each successive version pushes the boundary outward, and the document says so plainly.

## Scale 2. The crystal cell: the target device

This is the cell the whole program is trying to reach, and every part of it except one has been demonstrated somewhere.

**The object.** A millimeter scale crystal of CaF₂, transparent to its own working wavelength, doped with ²²⁹Th at $10^{17}$ to $10^{18}$ nuclei per cm³ (the doping already achieved in the crystals used for the 2024 nuclear clock measurements). There are no wires in it, no junctions, no lithography. The device structure is *optical*: focused beams define where the cells are.

**The register.** One cell is a voxel of the crystal about $(10\ \mu\text{m})^3$, containing $10^8$ to $10^9$ ²²⁹Th nuclei. The CHANNEL variable is the isomer fraction $n_m$ of that ensemble: an analog value, held without refresh for the isomer lifetime (about 630 s fluorescence lifetime in crystal; 1740 s half life in vacuum). By the precision law, a full destructive read of $10^8$ nuclei supports at most $\tfrac12\log_2 10^8 \approx 13$ bits of analog depth per voxel; that is an upper bound at perfect collection, and it is the honest unit of capacity for this machine.

**The terminals.** The GATE is a focused 148.38 nm VUV beam: pump fluence writes $n_m$ (demonstrated, 2024), a trigger or dump pulse releases it, and the resulting 8.4 eV fluorescence burst, proportional to $n_m$, is the DRAIN, guided by the crystal itself toward the next voxel or the boundary. Addressing is by position (beam waist, micrometers) and by energy (different dopant isotopes resonate at cleanly separated lines in the same voxel: spectral addressing, with no electronic analog).

**The two honest gaps.** First, writing speed: today's microwatt class VUV sources excite only trace populations, which suffices for rate encoded signaling but not for filling the 13 bit analog depth in useful time; milliwatt class 148 nm generation is an engineering gap, not a physics gap. Second, the gain socket: this cell is a nonvolatile memory and a soft threshold neuron with $\beta \approx 1$. It cannot drive successors. The socket where transconductance belongs is exactly the keystone of the main document, and the cell is drawn with that socket visibly empty because drawing it filled would be a lie.

## Scale 3. The neutron gate: the cell that already exists

**The object.** A moderated region containing fissile material (²³⁵U, or ²⁴²ᵐAm, the one entry that is simultaneously an isomer and a proven gain medium), kept strictly subcritical at, say, $k = 0.9$. It is the size of a washing machine and wants a license, shielding, and an institution.

**The terminals.** The control absorber is the GATE, programmable by position. Neutrons arriving from the driver source and from neighboring regions are the SOURCE. The multiplied leakage flux to the next region is the DRAIN. The circulating neutron population is the CHANNEL, and the moderator is the BODY. The gain is $M = 1/(1-k) = 10$ at $k = 0.9$: real transconductance, tabulated in ENDF to four digits, with level restoration built in because fission neutrons are born fast regardless of what triggered them. Clocking is set by the prompt generation time: about $10^{-4}$ s in thermal assemblies, about $10^{-8}$ s in fast ones.

**Why it is in this document.** Not as a proposal; nobody wants this computer. It is here because a skeptical reader's strongest objection to the crystal cell ("no such device has ever existed") is answered by pointing at this one: the same pinout, with the gain socket filled, has operated on Earth since 1942, and operated *unattended* at Oklo two billion years before that. The crystal cell is that device shrunk by seven orders of magnitude, minus, so far, its gain.

---

## What you would actually see

A visitor looking at the finished crystal machine would see a lead lined box holding a fingernail sized crystal, two or three laser feeds entering through windows, and a detector ring at the boundary. Nothing moves. There is no hum. The entire computation, the weighted sums flowing through the Green's function, the isomer registers filling and dumping, the coincidence multiplications, is photon traffic inside the crystal, invisible and silent, paid for by a decay budget. The benchtop version is the same idea a visitor can watch: servos clicking apertures, scintillators flashing faintly in the dark, a counter ticking off samples that no pseudorandom generator anywhere had to fake.

*The pinout is the argument. If a device has a gate, a source, a drain, a state, and a substrate, it can be tiled; if one of the three embodiments above already runs with gain, the question is not whether this machine can exist, but at what scale it must.*
