# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""Every headline number the documents quote is read back from the file that
computes it. The results files are regenerated before the tests run, so a
number that moves in a computation and not in the prose fails here; the
180mTa correction of the first edition's erratum was exactly this class of
drift, between a curated table and a generated one.

Each check names the generated file, a pattern that captures the number
there, and the documents that must quote it in the form given."""
import csv
import re

import pytest

from conftest import ROOT, read


def captured(path, pattern):
    m = re.search(pattern, read(path))
    assert m, f"{path}: nothing matches {pattern!r}"
    return m.group(1)


def candidate(key, column):
    for row in csv.DictReader(open(f"{ROOT}/gates/candidates.csv", encoding="utf-8")):
        if row["key"] == key:
            return row[column]
    raise AssertionError(f"no candidate {key}")


# (generated file, capture pattern, {document: [forms the document must contain, with {v} for the value]})
CHECKS = [
    ("neutron/results.md", r"Drain per source neutron with the gate open: \*\*([\d.]+)\*\*",
     {"README.md": ["{v} fission neutrons", "{v} with the gate open"], "theory/THEORY.md": ["becomes {v} fission neutrons"],
      "transistor/README.md": ["a drain of {v} fission neutrons"], "neutron/README.md": ["**{v} fission neutrons in B"]}),
    ("neutron/results.md", r"gain bandwidth product M/τ = 1/Λ = \*\*([\d.]+) kHz\*\*",
     {"README.md": ["1/Λ = {v} kHz", "**{v} kHz**"], "theory/THEORY.md": ["1/Λ = {v} kHz"], "transistor/README.md": ["{v} kHz"]}),
    ("neutron/results.md", r"temperature coefficient \*\*(-\d+) pcm/K\*\*",
     {"README.md": ["{v} pcm/K"], "theory/THEORY.md": ["{v} pcm/K"]}),
    ("neutron/results.md", r"dominant eigenvalue of K \*\*([\d.]+) ± [\d.]+\*\* against k \*\*([\d.]+)",
     {"README.md": ["eigenvalue {v}"], "theory/THEORY.md": ["dominant eigenvalue {v}"]}),
    ("neutron/results.md", r"generation time of the pair Λ = \*\*(\d+)\.\d µs\*\*",
     {"README.md": ["Λ = {v} µs"], "theory/THEORY.md": ["generation time is {v} µs"]}),
    ("photon/results.md", r"\| coincidences compatible with resonance within one standard deviation of the data \| (\d+) \|",
     {"README.md": ["{v} release lines"], "theory/THEORY.md": ["{v} coincidences"]}),
    ("photon/results.md", r"\| of which heterogeneous \(different nuclides\) \| (\d+) \|",
     {"README.md": ["{v} of them"], "theory/THEORY.md": ["{v} of them heterogeneous"]}),
    ("photon/results.md", r"\| of which closed loops, A triggers B and B triggers A \| (\d+) \|",
     {"README.md": ["{v} closed loops"], "theory/THEORY.md": ["{v} closed loops"]}),
    ("photon/results.md", r"\| isomers with a signal gateway and a veto gateway \| (\d+) \|",
     {"README.md": ["{v} isomers offer a signal gateway"], "theory/THEORY.md": ["counts {v} such isomers"]}),
    ("photon/results.md", r"\| NEEC class gateways \(within 30 keV of the isomer\) \| \d+, of which (\d+) release \|",
     {"README.md": ["{v} releasing gateways"], "theory/THEORY.md": ["NEEC class of {v} gateways"]}),
    ("ampoule/results.md", r"photons leaving the source capsule into the lamp cell: \*\*([\d.]+ M/s)\*\*",
     {"README.md": ["**{v}** leave the core"], "transistor/SEALED.md": ["sends {v} of bremsstrahlung"]}),
    ("ampoule/results.md", r"detected boundary events: \*\*([\d.]+ M/s)\*\*",
     {"README.md": ["counts **{v}**"], "transistor/SEALED.md": ["boundary counts {v}"], "transistor/EMBODIMENT.md": ["sees {v}"]}),
    ("ampoule/results.md", r"\*\*the same shell with CsI cells\*\*.*?\*\*([\d.]+ M/s)\*\* over all 64",
     {"README.md": ["**{v}**, 31× more"], "transistor/SEALED.md": ["CsI, at {v}"], "transistor/EMBODIMENT.md": ["{v} in all"]}),
    ("ampoule/results.md", r"ON/OFF contrast of the collar: \*\*([\d.]+)\*\*",
     {"README.md": ["contrast of {v} with plastic"], "transistor/SEALED.md": ["contrast of {v}"], "transistor/EMBODIMENT.md": ["contrast is {v} with plastic"]}),
    ("ampoule/results.md", r"\| at the titanium wall \| \*\*([\d.]+) µSv/h\*\* \|",
     {"README.md": ["**{v} µSv/h** at the titanium wall"], "transistor/SEALED.md": ["{v} µSv/h at contact"], "transistor/EMBODIMENT.md": ["{v} µSv/h at the titanium wall"]}),
    ("ampoule/results.md", r"\| 1 m from the centre \| \*\*([\d.]+) µSv/h\*\* \|",
     {"README.md": ["**{v} µSv/h** at one metre"], "transistor/SEALED.md": ["{v} µSv/h at a metre"], "transistor/EMBODIMENT.md": ["{v} µSv/h at a metre"]}),
    ("simulator/results.md", r"decays per independent sample: \*\*(\d+)\*\*",
     {"README.md": ["every {v} decays", "{v} decays per independent sample"], "transistor/README.md": ["measured {v} decays"],
      "transistor/SEALED.md": ["{v} decays per sample"], "ampoule/compile_results.md": ["{v} decays per sample"]}),
    ("simulator/results.md", r"\| 229mTh quantum \(8.4 eV\) \| [\de.+-]+ \| [\de.+-]+ \| (\d+)x cheaper \|",
     {"README.md": ["about {v} times less energy"], "simulator/README.md": ["about {v} times cheaper"]}),
    ("simulator/results.md", r"\| 60Co gamma \(1.25 MeV\) \| [\de.+-]+ \| [\de.+-]+ \| (\d+)x costlier \|",
     {"README.md": ["{v} times *costlier*"], "simulator/README.md": ["about {v} times costlier"]}),
    ("transport/compiler_results.md", r"worst error \*\*([\d.]+%)\*\* in 1500 Adam steps",
     {"README.md": ["to {v0} percent from a blank plate"], "theory/THEORY.md": ["worst weight error of {v0} percent"],
      "transport/README.md": ["random target to {v0} percent"]}),
    ("ampoule/compile_results.md", r"draws about \*\*([\d.]+) independent samples per second\*\*",
     {"README.md": ["**{v} independent samples per second**"], "transistor/SEALED.md": ["{v} independent samples per second"]}),
    ("ampoule/compile_results.md", r"integrated autocorrelation time of \*\*\d+ proposals, ([\d.]+) sweeps\*\*",
     {"README.md": ["{v} sweeps"]}),
    ("ampoule/compile_results.md", r"a nearest neighbour bond carries \*\*[\d.]+ photons per second\*\* with plastic cells and \*\*([\d.]+)\*\* with CsI",
     {"README.md": ["{v} photons per second"], "transistor/SEALED.md": ["{v} photons per second"], "theory/THEORY.md": ["{v} photons per second"]}),
]


@pytest.mark.parametrize("source,pattern,quotes", CHECKS, ids=[c[1][:40] for c in CHECKS])
def test_documents_quote_the_computed_number(source, pattern, quotes):
    m = re.search(pattern, read(source), re.S)
    assert m, f"{source}: nothing matches {pattern!r}"
    v = m.group(1)
    v0 = v.rstrip("%").split(" ")[0]
    if "." in v0:
        v0 = v0.rstrip("0").rstrip(".") if float(v0) != int(float(v0)) else str(int(float(v0)))
    missing = []
    for doc, forms in quotes.items():
        text = read(doc)
        for form in forms:
            want = form.format(v=v, v0=v0)
            if want not in text:
                missing.append((doc, want))
    assert not missing, f"{source} computes {v!r} but these quotations are missing: {missing}"


def test_the_candidate_table_agrees_with_the_documents_on_beta():
    for key, want in (("93mMo", "2.87"), ("178m2Hf", "12.39")):
        assert candidate(key, "beta_gamma") == want, key
    text = read("README.md") + read("gates/README.md") + read("theory/THEORY.md")
    assert "β = 2.87" in text and "β = 12.39" in text


def test_the_180mta_correction_holds_everywhere():
    """The first edition's erratum: the curated table said 77.1 keV while the catalogue said 75.3."""
    assert candidate("180mTa", "E_keV").startswith("75.3")
    for doc in ("README.md", "gates/candidates.md", "gates/experiment_menu.md"):
        assert "77.1" not in read(doc), doc
    assert "75.3 keV" in read("README.md")
