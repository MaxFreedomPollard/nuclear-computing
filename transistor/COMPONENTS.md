# The inventory note: every component of a working computer, accounted for

*A note accompanying [the reference transistor](README.md): the complete parts list of a computer, each part mapped to its nuclear implementation, its status stated in one of three honest words, and the missing ones simulated in [`simulator/components.py`](../simulator/components.py) (results in [`components_results.md`](../simulator/components_results.md), figure 13).*

## The inventory

| component | in silicon | nuclear implementation | status |
|---|---|---|---|
| transistor | MOSFET | the reference transistor, three scales, one pinout | specified ([README.md](README.md)) |
| logic gates | CMOS | coincidence AND, absorption NOT, scattering MUX, valve routing | demonstrated ([/transport](../transport/results.md), [VALVE.md](VALVE.md)) |
| adder | ripple carry | scattering MUX at select 1/2: $z = (x+y)/2$, exact | demonstrated (fig. 13; worst error 0.0014) |
| multiplier | array multiplier | the coincidence gate | demonstrated (0.4 percent against the exact form) |
| comparator | sense amp | like degree count comparison | demonstrated ([degree checker](../transport/degree_check.py)) |
| ALU | adder + logic | the four above, composed feed forward (Bernstein universality for everything continuous) | demonstrated in parts |
| clock | crystal oscillator | divide by N on the Poisson stream: jitter exactly $1/\sqrt{N}$ | demonstrated (fig. 13A; 0.1 percent clock = $10^6$ decays per tick) |
| random source | PRNG (fake) | the substrate itself | native, born at the ceiling |
| register / latch | flip flop | ¹⁸¹Ta parent fed, field addressed latch (6 µs) | catalog physics ([theory 9.3](../theory/THEORY.md)) |
| nonvolatile memory | flash | isomer populations, ²²⁹Th to the catalog ladder | demonstrated physics (write/hold/read, fig. 12B) |
| rewritable working memory | DRAM + sense amps | a self exciting loop through a saturable stage: latches iff loop gain $\Gamma > 1$ | keystone gated (fig. 13B: the fork at $\Gamma = 1$, measured) |
| address decoder | row/column decoders | resonance addressing by field maps (MRI move) | catalog physics (theory 9.3a) |
| bus / interconnect | copper traces | energy division multiplexing, one line per channel | computed plan ([gates/edm_channels.md](../gates/edm_channels.md): 8 of 8 clean on CZT) |
| control unit | instruction sequencer | aperture schedule tables; the one dial annealer (Geman and Geman) | specified (theory 10.2; [EMBODIMENT.md](EMBODIMENT.md) operating procedure) |
| input | keyboard, network | fields through the wall: Zeeman maps, Doppler waveforms, apertures | catalog physics (theory 8.2) |
| output | display, network | the modulated glow: a valve keys an emission line | demonstrated (fig. 13C; below) |
| power supply | the wall socket | the decay inventory itself, five conversion chains | specified ([POWER.md](POWER.md)) |

## What the inventory says, read honestly

Every row is filled. Three rows carry the word that matters most: the rewritable working memory row (and with it, unbounded digital recurrence) is *keystone gated*, and figure 13B now shows exactly why, as a measurement: a written bit circulating a lossy loop dies geometrically below $\Gamma = 1$ and latches above it. This is the amplification condition of the keystone criterion reappearing as the memory regeneration requirement, the same physics that makes DRAM need sense amplifiers. The machine has *storage* today (isomers are nonvolatile without gain); what waits on the keystone is memory the computation itself can rewrite through a loop, which is the difference between an appliance and a stored program computer, stated as one inequality.

Everything else, the ALU, the clock, the decoder, the bus, the control, the I/O, and the power, is demonstrated, computed, or sitting in catalogs. The inventory is the miniaturized restatement of the whole repository: one socket, everything else on the shelf.

## The output row, expanded: the modulated glow

The best way to move results out of a sealed, self contained computer is the one that uses what the machine already is. An internal valve ([VALVE.md](VALVE.md)) keys one of the machine's own emission lines; any external spectrometer or counting detector, behind the wall, behind steel, behind soil, reads the keying. Figure 13C measures the link over the Poisson counting channel: at a modest $10^4$ detected counts per second and 40 percent valve contrast, a $10^{-4}$ error rate at 33 bits per second, and a $10^{-9}$ grade link at about ten bits per second; rate scales linearly with detected budget, so $10^6$ counts per second is a kilobit link. The properties no conventional interface has: no antenna, no cable, no penetration, no emission in any radio band, and a carrier that traverses conductors and shielding that stop every electromagnetic alternative. Telemetry from inside reactor vessels, from sealed waste containers, from deep boreholes, from anywhere a wire cannot go and a radio cannot reach, is the natural first customer, and the transmitter is nothing but the machine deciding what its own glow says. Inbound, the same wall is crossed by fields (theory 8.2); the pair together is a full duplex interface with zero penetrations.
