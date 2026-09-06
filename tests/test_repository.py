# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""The repository's own promises, as tests: the reproduce script and the CI
run the same steps, every generating script is run by one of them, the
environment is pinned, the committed inputs are the ones the manifest
names, and the figures and compressed tables are written in the form that
reproduces byte for byte on every platform."""
import gzip
import hashlib
import os
import re

from conftest import ROOT, load_script, read, tracked

# scripts that need OpenMC, the nuclear data library, or the network, and so run in openmc.yml or by hand
NEEDS_OPENMC_OR_NETWORK = {"neutron/gate.py", "neutron/benchmarks.py", "neutron/data.py",
                           "ampoule/model.py", "ampoule/calibrate.py", "ampoule/beta.py", "photon/ensdf.py"}


def ci_steps():
    return re.findall(r"run:\s*python\s+(\S+\.py)", read(".github/workflows/build.yml"))


def test_reproduce_and_ci_run_the_same_steps_in_the_same_order():
    rep = load_script("reproduce.py")
    assert [s for s, _ in rep.STEPS] == ci_steps()


def test_every_generating_script_is_run_by_reproduce_or_needs_openmc():
    rep = load_script("reproduce.py")
    run = {s for s, _ in rep.STEPS}
    scripts = {p for p in tracked(".py") if not p.startswith("tests/") and p != "reproduce.py"}
    unrun = sorted(scripts - run - NEEDS_OPENMC_OR_NETWORK)
    assert not unrun, f"scripts nobody runs: {unrun}"
    assert not (NEEDS_OPENMC_OR_NETWORK - scripts), "the OpenMC set names a script that does not exist"


def test_the_openmc_workflow_runs_the_openmc_scripts():
    text = read(".github/workflows/openmc.yml")
    for s in ("neutron/data.py", "neutron/benchmarks.py", "neutron/gate.py", "ampoule/calibrate.py", "ampoule/model.py"):
        assert s in text, s


def test_requirements_are_pinned():
    for line in read("requirements.txt").splitlines():
        if line.strip() and not line.startswith("#"):
            assert re.match(r"^[A-Za-z0-9_.-]+==\d", line), f"unpinned requirement: {line}"


def test_the_ci_installs_the_pinned_requirements_and_checks_the_tree():
    text = read(".github/workflows/build.yml")
    assert "pip install -r requirements.txt" in text
    assert "git status --porcelain" in text, "the CI does not verify that the tree reproduced"
    assert "pytest" in text


def test_svg_figures_are_vector_only_and_undated():
    bad = []
    for p in tracked(".svg"):
        text = read(p)
        if "image/png" in text or "<dc:date>" in text:
            bad.append(p)
    assert not bad, f"figures with an embedded raster or a date, which differ between platforms: {bad}"


def test_compressed_tables_carry_no_timestamp():
    for p in tracked(".gz"):
        with open(os.path.join(ROOT, p), "rb") as f:
            header = f.read(10)
        assert header[:2] == b"\x1f\x8b", p
        assert header[4:8] == b"\x00\x00\x00\x00", f"{p} carries a gzip mtime and will differ run to run"
        with gzip.open(os.path.join(ROOT, p), "rb") as f:
            f.read(64)


def test_committed_inputs_match_the_manifest():
    entries = [l.split() for l in read("data-manifest.sha256").splitlines() if l.strip()]
    assert entries, "the manifest is empty"
    wrong = []
    for digest, path in entries:
        h = hashlib.sha256(open(os.path.join(ROOT, path), "rb").read()).hexdigest()
        if h != digest:
            wrong.append(path)
    assert not wrong, f"inputs that differ from the manifest: {wrong}"


def test_the_manifest_names_every_committed_input():
    named = {l.split()[1] for l in read("data-manifest.sha256").splitlines() if l.strip()}
    expected = {p for p in tracked() if p.startswith("gates/data/")} | {
        "photon/levels.json.gz", "neutron/tallies.json", "neutron/benchmarks.json",
        "ampoule/tallies.json", "ampoule/calibration.json"}
    assert named == expected, f"missing: {sorted(expected - named)}, extra: {sorted(named - expected)}"


def test_the_dockerfile_matches_the_ci_openmc_version():
    dockerfile = read("Dockerfile")
    ci = read(".github/workflows/openmc.yml")
    m = re.search(r"openmc=([\d.]+)=\*nompi\*", ci)
    assert m and f"openmc={m.group(1)}=*nompi*" in dockerfile
