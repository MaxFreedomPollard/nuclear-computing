# /gates: the keystone criterion evaluated against nuclear data

This directory is the working end of the foundational document's central claim: that the entire viability of nuclear computing collapses onto one falsifiable component, the triggered release gate with gain, judged by the leak condition $\eta > \tfrac12$ and the amplification condition $\Gamma > 1$.

| file | what it is |
|---|---|
| `isomer_screen.py` | screens every isomer in NUBASE2020 (1870 states) and evaluates a curated candidate set; regenerates the catalog, the candidate table, and figure 8 |
| `isomer_catalog.csv` | every isomer on Earth: excitation energy, half life, $\lambda_m$, spin parity, decay modes |
| `candidates.csv`, `candidates.md` | the curated candidates with measured multiplicities, trigger mechanisms, energy leverage, and citations |
| `experiment_menu.md` | required trigger cross sections and fluxes per candidate per facility; where the keystone lives and dies |
| `edm_plan.py`, `edm_channels.md` | the computed energy division multiplexing channel plan: eight clean CZT interconnect channels from catalog sources, with leakage matrices and longevity |
| `data/` | cached NUBASE2020 and ENSDF decay radiation files (IAEA), so every number is reproducible offline |

Headline numbers, all computed from the data in this directory:

- 1870 isomeric states known; 585 hold a bit for at least one second; 50 are nonvolatile for at least a day; 38 of those store at least 100 keV.
- ⁹³ᵐMo releases β = 2.87 photons per triggered decay (ENSDF intensities), not the vague "few" of the literature.
- ¹⁷⁸ᵐ²Hf releases β = 12.39 photons per release once the 1147 keV chain it feeds is counted, confirming the folklore value of about a dozen from primary data.
- The only rows of `candidates.md` where trigger cross section, flux, and multiplicity are all *measured* quantities satisfying both keystone inequalities are the neutron sector rows (²⁴²ᵐAm, ²³⁵U). See `experiment_menu.md` for what that means.

Run it:

```
python3 isomer_screen.py
```

Requires `matplotlib` for the figure; the CSV outputs need only the standard library. First run downloads and caches the IAEA files.
