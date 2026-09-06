# Data: where every input comes from

Every number in this repository descends from public nuclear data through the scripts in the tree. The inputs the scripts read are either committed here, so that everything reproduces offline, or fetched from an official archive by a script that verifies what it fetched. This page names each one. The committed inputs are listed with their SHA-256 digests in [data-manifest.sha256](data-manifest.sha256), and a test fails if any of them changes without the manifest.

## Committed inputs

| file | what it is | source | read by |
|---|---|---|---|
| `gates/data/nubase_4.mas20.txt` | NUBASE2020, the evaluation of nuclear and decay properties of every known nuclide and isomer | Kondev, Wang, Huang, Naimi, Audi, Chin. Phys. C 45, 030001 (2021); IAEA AMDC | `gates/isomer_screen.py`, `photon/ensdf.py` |
| `gates/data/decay_g_*.csv` | decay radiation (gamma) tables for the curated candidate isomers, from ENSDF | IAEA Live Chart of Nuclides, `fields=decay_rads` | `gates/isomer_screen.py` |
| `photon/levels.json.gz` | the adopted levels and gammas of the 544 nuclides carrying an isomer that holds a bit for at least a second, packed | IAEA Live Chart of Nuclides (ENSDF), fetched and packed by `photon/ensdf.py` | `photon/census.py` |
| `neutron/tallies.json`, `neutron/benchmarks.json` | the raw tallies of the two region gate protocol and the three handbook benchmarks, with Monte Carlo uncertainties | OpenMC 0.16.0 with ENDF/B-VIII.0, run by `neutron/gate.py` and `neutron/benchmarks.py` | `neutron/report.py` |
| `ampoule/tallies.json`, `ampoule/calibration.json` | the raw tallies of the vessel in photon transport, and the instrument's calibration against XCOM, the exponential and the thick target rule | OpenMC 0.16.0 with ENDF/B-VIII.0 photoatomic data, run by `ampoule/model.py` and `ampoule/calibrate.py` | `ampoule/report.py`, `ampoule/compile.py` |

## Fetched inputs

| what | source | fetched by | verified how |
|---|---|---|---|
| the ENDF/B-VIII.0 library in OpenMC's HDF5 form (the files the two transport directories use, about 2 GB of a 3.4 GB archive) | openmc.org, the official distribution | `neutron/data.py`, streamed once into `neutron/data/` (ignored by git) or `NC_DATA_DIR` | `python neutron/data.py --verify`, and the three ICSBEP handbook criticals in `neutron/benchmarks.py` |
| the raw level and gamma CSVs behind `photon/levels.json.gz` | IAEA Live Chart of Nuclides | `photon/ensdf.py`, cached in `photon/cache/` (ignored by git) | the packed file is committed; the census reproduces from it offline |

## Reference values quoted from the literature

Handbook eigenvalues and the JEFF-3.1 results on the same cases are from OECD/NEA JEFF Report 21, Appendix 2, with geometries as transcribed in the MIT CRPG benchmark collection. NIST XCOM attenuation coefficients, the ICRP 107 beta mean energies and the ICRP 116 dose coefficients are carried inside the scripts and tally files that use them, with their citations. The ²²⁹Th transition frequency, the NEEC and IGE literature, and the probabilistic hardware benchmark are cited in the [README](README.md) references.

## Reproducing everything

```
pip install -r requirements.txt
python reproduce.py --check
```

runs every step in the order the CI does and reports whether every number, table and vector figure came back byte for byte. The OpenMC runs that regenerate the two tally sets are in `.github/workflows/openmc.yml` and, for a local machine, the [Dockerfile](Dockerfile).
