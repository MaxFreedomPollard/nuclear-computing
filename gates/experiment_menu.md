# The experiment menu: what it costs to satisfy the keystone criterion

This document turns the keystone criterion into shopping lists. For each candidate state it answers one question: what trigger cross section, at what control flux, would satisfy the leak condition $\eta > \tfrac12$, and what would then remain for the amplification condition $\Gamma > 1$? Every number below is either computed from NUBASE2020 and ENSDF (see `isomer_screen.py` and `candidates.csv`) or is an order of magnitude facility figure with its assumption stated inline. Nothing is fitted, nothing is hoped.

## The three conditions, stated operationally

1. **Leak condition.** $\sigma_{\text{trig}}\,\phi_{\text{ctrl}} > \lambda_m$. Equivalently, the control flux must exceed $\phi_{\text{req}} = \lambda_m / \sigma_{\text{trig}}$, or the cross section must exceed $\sigma_{\text{req}} = \lambda_m / \phi$ at a given facility.
2. **Amplification condition.** $\Gamma = \beta\,\eta / C_{\text{in}} > 1$: more usable quanta out than control quanta spent.
3. Rate condition (new; long lived isomers make it the binding one). For an isomer with tiny $\lambda_m$ the leak condition is nearly free, but a *computer* also needs the gate to fire at the machine's clock rate: $R_{\text{trig}} = \sigma_{\text{trig}}\,\phi_{\text{ctrl}} \gtrsim f_{\text{gate}}$. Beating the leak is necessary; beating the clock is what costs flux.

## Facility flux scales (assumptions inline)

| control field | flux $\phi$ (cm⁻² s⁻¹) | assumption |
|---|---|---|
| CW VUV laser, 1 W focused to (10 µm)² | $7\times10^{23}$ | 8.4 eV photons, $7.5\times10^{17}$ ph/s |
| synchrotron nuclear resonance beamline | $10^{16}$ | $10^{10}$ ph/s in a meV bandwidth on (10 µm)² |
| XFEL, time averaged | $10^{24}$ | $10^{12}$ ph/pulse, $10^4$ pulses/s, (1 µm)² focus |
| XFEL, peak during pulse | $4\times10^{33}$ | same pulse compressed to 25 fs |
| research reactor, thermal column | $10^{13}$ to $10^{15}$ | ordinary thermal neutron flux |

## Required trigger cross section $\sigma_{\text{req}} = \lambda_m/\phi$ for $\eta = \tfrac12$

| state | $\lambda_m$ (s⁻¹) | at synchrotron | at XFEL (avg) | at XFEL (peak) | at reactor ($10^{14}$ n) |
|---|---|---|---|---|---|
| ²²⁹ᵐTh | $4.0\times10^{-4}$ | $4.0\times10^{-20}$ cm² | $4.0\times10^{-28}$ | $1.0\times10^{-37}$ | (laser proven; moot) |
| ²³⁵ᵐU | $4.4\times10^{-4}$ | $4.4\times10^{-20}$ | $4.4\times10^{-28}$ | $1.1\times10^{-37}$ | |
| ⁹³ᵐMo | $2.8\times10^{-5}$ | $2.8\times10^{-21}$ | $2.8\times10^{-29}$ | $7.0\times10^{-39}$ | |
| ¹⁷⁷ᵐLu | $5.0\times10^{-8}$ | $5.0\times10^{-24}$ | $5.0\times10^{-32}$ | $1.3\times10^{-41}$ | |
| ¹⁷⁸ᵐ²Hf | $7.1\times10^{-10}$ | $7.1\times10^{-26}$ | $7.1\times10^{-34}$ | $1.8\times10^{-43}$ | |
| ²⁴²ᵐAm | $1.6\times10^{-10}$ | | | | $1.6\times10^{-24}$ cm², i.e. 1.6 b needed, 6400 b available |
| ²³⁵U | $3.1\times10^{-17}$ | | | | $3.1\times10^{-31}$ cm² needed, 585 b available |

Readings, one per row:

- **⁹³ᵐMo.** At XFEL average flux the leak condition needs an effective NEEC cross section of only $2.8\times10^{-29}$ cm² (28 µb). The dispute is whether NEEC delivers anything like this: the 2018 beam based claim implies a per ion depletion probability near $10^{-2}$, while ab initio theory (Wu, Keitel, Pálffy, PRL 122, 212501) predicts values eight to nine orders of magnitude smaller. If the claim survives the ongoing Penning trap and EBIT tests (arXiv 2501.05217), an XFEL gate window is plausible and the keystone program proceeds in the photon sector. If theory wins, no facility on this menu reaches $\eta > \tfrac12$ for ⁹³ᵐMo, and the photon sector keystone dies exactly as kill criterion B allows. Both outcomes are progress; only the experiment decides.
- **¹⁷⁸ᵐ²Hf.** At a synchrotron the leak condition needs 71 mb. The 1999 triggering claim implied roughly this scale; the dedicated synchrotron refutations placed upper limits far below it. By the menu's own arithmetic the Hf gate is dead at synchrotrons unless the refutations are themselves overturned, which nothing in the record suggests. Note that the leak condition is nearly free here ($t_{1/2}$ = 31 y); what actually dies is the rate condition, since the same tiny cross section that fails $\eta$ at short windows also caps $R_{\text{trig}}$ far below any useful clock.
- **¹⁸⁰ᵐTa.** The trigger is proven (photoactivation through gateway states at and above 1.01 MeV, Belic et al., PRL 83, 5242) but the ledger is upside down: about 1 MeV in per 77 keV stored. Leverage 0.076. A proven switch, an impossible amplifier. It earns its place as the existence proof that *photon triggered isomer release is real physics*, and as the cautionary unit of energy accounting.
- **²⁴²ᵐAm and ²³⁵U.** The neutron sector rows are not like the others: every quantity is tabulated to engineering precision. For ²⁴²ᵐAm at an ordinary thermal column ($10^{14}$ n cm⁻² s⁻¹), $\eta = 0.9998$, and the release channel (fission, about 202 MeV, roughly 3.3 neutrons and 8 prompt photons) gives $\Gamma \approx 11$ in photon number or about 2 in neutron number per absorption. For ²³⁵U the neutron ledger reads $\nu\,\sigma_f/(\sigma_f + \sigma_\gamma) \approx 2.1$ neutrons out per neutron absorbed. Both keystone inequalities are satisfied, today, with library data. The keystone gate exists; it lives in the neutron sector, at reactor scale, with all the mass, regulation, and shielding that implies. The isomer program is therefore not a search for whether the gate can exist. It is a miniaturization program.

## What this menu buys the roadmap

- **Phase B is now two questions, not one.** B1 (photon sector): does any isomer plus mechanism reach the required cross sections above? The Penning trap NEEC test largely decides B1 for ⁹³ᵐMo. B2 (neutron sector): already answered yes by ENDF; the open work is architecture (coupled subcritical regions as gates), not existence.
- **The rate condition belongs in the criterion.** For every isomer with $t_{1/2} \gg$ seconds the leak condition is trivially satisfied and quoting $\eta$ alone flatters the candidate. The table to beat is $R_{\text{trig}}$ versus clock rate, and it is brutal: at synchrotron flux, even a 1 b cross section fires a given nucleus once per $10^8$ seconds.
- **Duty cycle honesty.** XFEL peak columns look miraculous ($10^{-39}$ cm² suffices during the pulse) but the machine sleeps between pulses; the average column is the one that meets the rate condition. Pulsed triggering buys synchronization, not sustained throughput.

*Every cross section in this file is a requirement derived from measured $\lambda_m$; the two neutron rows are the only ones where the available value is also known. That asymmetry is the entire state of the field, drawn in one table.*
