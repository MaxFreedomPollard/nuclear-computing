# Changelog

Every release of this repository is archived on Zenodo under the concept DOI [10.5281/zenodo.21330486](https://doi.org/10.5281/zenodo.21330486); the version DOI of each release is on its Zenodo record.

## 1.1.0: the second edition

The founding edition stated the theory, evaluated its criterion against the nuclear data record, and specified the device. This edition computes the machine: the keystone in the neutron sector in real neutron transport, the photon sector keystone searched for in ENSDF, the sealed vessel in real photon transport, and the compiler run on what that transport measured. It also makes the repository's oldest promise, that every number regenerates from public data, into a checked one.

### New results

- **The neutron gate, computed** ([neutron/](neutron/)). The two region subcritical gate of theory Section 4 built in OpenMC with the official ENDF/B-VIII.0 library, calibrated first against three ICSBEP handbook criticals: the fission matrix and its eigenvalue check, a drain of 1.49 fission neutrons per driver neutron with the gate open, the transfer curves of two absorbers, superposition to 0.6 percent, level restoration to a total variation of 0.002 across a thermal to 14 MeV input range, the clock (Λ = 106 µs, 1/Λ = 9.4 kHz), and the temperature coefficient that prices the sector's only veto. The convergence trap of weakly coupled regions is on the record with its remedy.
- **The photon keystone, searched** ([photon/](photon/)). Every gateway of the 415 isomers that hold a bit for a second, in observed and allowed classes, with its release cascade; the level restoring pairs of theory Section 2 counted (12470 candidates, none the data can resolve, all behind the areal density wall); the veto gateway that gives isomers the inhibition the neutron sector lacks (214 isomers); the NEEC class as the Phase B1 target list.
- **The ampoule, transported** ([ampoule/](ampoule/)). The sealed vessel of the machine and build notes in OpenMC photon transport, driven by its own ⁹⁰Sr and ⁹⁰Y beta spectra: the photon budget, the site rates in plastic and CsI, the collar's transfer curve, the 64 × 64 Green's function and the septum's effect on it, the boundary count, the energy budget and the dose outside. The notes are amended where the numbers say so.
- **The vessel, compiled** ([ampoule/compile.py](ampoule/compile.py), [figure 18](figures/fig18_compiled.svg)). The compiler of theory Section 11 run on the measured Green's function: the fabric read as solid angle times an interaction probability; Way B placing the twin's instance on the vessel's lattice and the fabric's unaperturable couplings burying it, with the collar pass as the last compilation step; the 64 site law checked against an exact transfer matrix at 3.3 sweeps per independent sample; and the timing closure, every weight a photon current, which prices the vessel as built at 0.34 independent samples per second against the 38,462 the machine note priced on proposals alone, with the ladder of measured and catalogue levers between the two. Theory Section 11.5 and the reset ledger of Section 3.1 gain the synapse term; the machine note, the build note and the ENIAC ledger are amended.

### The repository as an instrument

- `reproduce.py` runs every step in the CI's order and, with `--check`, fails unless every number, table and vector figure came back byte for byte. The CI now runs the same check on every push.
- `tests/`: the documents' headline numbers read back from the files that compute them (the class of drift the 1.0.1 erratum corrected), every internal link resolved, the house style enforced (no dashes in prose, isotopes as superscripts, no edition notes inside the documents), the instruments checked against things that are not themselves (the beta spectra against ICRP 107, the transfer matrix against enumeration, the sampler against its exact law, the adjoint against finite differences, the committed fission matrix against the committed eigenvalue), and the committed inputs against a manifest.
- `requirements.txt` is pinned. Under the pin the numbers reproduce byte for byte on macOS and Linux; the vector figures do too, now that the two that did not (a cancellation in the Siegert integrand, an embedded raster in the ampoule figure) are drawn in a platform independent form. Raster PNGs are regenerated but not compared.
- `Dockerfile`: the OpenMC 0.16.0 environment of the two transport directories, the image the neutron README referred to, for the x86-64 platform conda-forge builds it on.
- `data-manifest.sha256` and [DATA.md](DATA.md): every committed input with its digest and its source; the two compressed tables are written without a timestamp so they reproduce.
- [GLOSSARY.md](GLOSSARY.md): the terms the work coins, each with the place it is defined.
- The finite difference check of the adjoint compiler uses a step where truncation and not rounding sets the residual, so it reads the same on every BLAS (1×10⁻⁸ where it read 9×10⁻⁷).
- `CITATION.cff` carries the version.

### Corrections

- Hyphenated isotope designations in the transport documents are written as superscripts (²⁵²Cf), as the rest of the work does.

## 1.0.1: error corrections (2026-08-01)

- The ¹⁸⁰ᵐTa excitation energy corrected to the NUBASE2020 evaluated value, 75.3 keV, and the leverage figure derived from it, 0.075. The curated candidate table carried the superseded 77.1 keV value while the generated catalogue already read 75.3.

## 1.0.0: the founding release (2026-07-13)

The theory: the model, the gate set, the physical limits, the complexity ceiling, and the whole feasibility question concentrated into one falsifiable component, the keystone gate, judged by three inequalities. The criterion run against every isomer in NUBASE2020 and evaluated against ENSDF. The routine gates verified to Monte Carlo precision, the digital twin run decay by decay against exact enumeration, the compiler three ways, the degree checker. The reference transistor at three scales with its datasheet, the sealed ampoule with its build note, the valve, the component inventory, the metabolism and the ENIAC ledger. Seven executable instruments, a CI that recomputes every number, and a Zenodo archive.
