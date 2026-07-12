# The logic note: the valve, fully specified

*A note accompanying [the reference transistor](README.md): the complete specification of the field effect γ ray valve introduced there, as a device, as an algebra, and as an instrument that has been sitting on Mössbauer benches for sixty years without ever being asked to compute.*

## 1. The device

A valve is four parts on one sight line:

1. **Source**: ⁵⁷Co diffused into rhodium foil, 1 to 25 mCi (a standard commercial Mössbauer source). Emits the 14.4 keV line at natural width with recoil free fraction $f_s \approx 0.75$ at room temperature.
2. **Channel medium**: the absorber foil, 95 percent enriched ⁵⁷Fe, 1 to 2 µm, epoxy free mounted on 25 µm beryllium. Effective resonant thickness $t_a = f_a n \sigma_0 d$ of order 5 to 15 for this geometry (with the strength split across the six magnetic hyperfine components in α iron): deep dips are routine.
3. **The GATE, in either of two forms**:
   - *kinematic*: a piezoelectric velocity transducer carrying source or absorber; one natural linewidth per **0.097 mm/s**, full authority within ±10 mm/s, bandwidth from DC to tens of kHz (the ordinary Mössbauer drive);
   - *magnetic*: a coil at the foil; roughly **0.7 linewidths per tesla** on ⁵⁷Fe (the trim ring's ¹⁸¹Ta channels reach 42 per tesla and switch with millitesla; see the [build note](EMBODIMENT.md)).
4. **DRAIN**: whatever the sight line feeds: a coincidence cavity, another valve, or a boundary counter.

**Measured behavior to expect** (standard Mössbauer practice, quoted as ranges because they are geometry dependent): resonant transmission dips of 30 to 70 percent of the recoil free component; insertion loss from electronic absorption in the foil of a few percent (mass attenuation at 14.4 keV across 1 to 2 µm of iron); OFF to ON contrast on the *resonant component* of 3:1 to 10:1 per stage, compounding across stages in series.

**Switching time**: the channel cannot respond faster than the excited state lifetime (141 ns for ⁵⁷Fe), and in practice the gate is limited by the drive: kHz to tens of kHz kinematic, up to MHz for small magnetic swings. The valve is a **microsecond class router**, not a nanosecond one, until faster lines (⁶⁷Zn, ⁷³Ge class) or switched hyperfine media are engineered.

## 2. The algebra

Let a valve's state be OPEN (detuned, transmitting) or CLOSED (on resonance, absorbing). For the *resonant* component of the stream:

- **series composition is AND of openness**: a stream survives a chain of valves only if every one is open; transmission is the product of stage transmissions, exactly the thinning algebra of the gate set;
- **parallel composition is OR**: split paths recombined pass flux if any path is open;
- **NOT is built in**: a closed valve is a complement on the resonant component (and its *re emission* is isotropic, so a closed valve is also a tap: the absorbed traffic reappears as $4\pi$ fluorescence, usable as a monitor port);
- **velocity multiplexing**: a single physical sight line carries several logical channels at once, one per Doppler offset; a valve tuned to offset $v_i$ gates channel $i$ and ignores the others. This is frequency division multiplexing inside one γ line, orthogonal to the energy division multiplexing between lines ([gates/edm_channels.md](../gates/edm_channels.md)); a Mössbauer drive is a **channel selector** the way a superheterodyne dial is.

What the algebra is for, honestly: valves **route, modulate, select, and complement**. They do not amplify ($\beta = 1$ and lossy), so valve networks obey the same law as the rest of the routine gate set: any feed forward function (Bernstein, theory Section 6), no unbounded recurrence. A valve network is the machine's *switchboard*; the gain socket is still the keystone's.

## 3. The modulator

Driven with a waveform instead of a setpoint, the valve writes time structure onto the resonant component: sideband generation, pulse shaping, and phase control of single γ quanta by exactly this mechanism are demonstrated physics (the coherent γ optics literature: waveform control of recoilless photons through vibrating resonant absorbers). For the machine this is the **fast input port made rigorous**: an external problem enters as a drive waveform, and the valve imprints it onto nuclear traffic with no penetration of the vessel (magnetic flux coupling, per the build note).

## 4. The two disciplines

1. **Temperature.** The second order Doppler shift moves the line by about one linewidth per 10 K near room temperature; a valve bank must be either thermally uniform to a few kelvin or per channel trimmed (the trim coils exist anyway). Stated as a specification, not discovered as a mystery drift.
2. **Background.** The valve gates the *recoil free resonant* component only; Compton scattered and non resonant photons pass regardless, a DC pedestal under the logic. Discrimination is by energy window (the 14.4 keV photopeak) and, where needed, by coincidence with the 122 keV feeding photon of the ⁵⁷Co cascade, which tags true source quanta. The pedestal costs contrast, is fully characterized by a one hour bench scan, and enters the error budget as a known constant, never as noise.

## 5. Why this note exists

Every element above is decades old. The Mössbauer drive was built to *measure* hyperfine spectra, and the entire apparatus has spent its life as an instrument pointed at samples. Pointed instead at another valve, it is a logic element; arranged in series and parallel under the stream algebra, it is a switchboard; driven by waveforms, it is a modem between the electronic world and the nuclear one. The reference transistor's GATE terminal is not a proposal; it ships from catalogs with a calibration sheet. What has never shipped is the intent.
