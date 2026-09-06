# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""The house rules of the prose, as tests: no dashes in prose, isotopes as
superscripts, and no edition or version notes inside the documents, which
must read as finished products."""
import re

from conftest import read, tracked

DOCUMENTS = [p for p in tracked(".md") if not p.startswith(".github/")]
ISOTOPE_HYPHEN = re.compile(r"\b(Cf|Cs|Mo|Th|U|Am|Hf|Ta|Sr|Fe|Co|Ba|Ni|Pu|Kr|Ho|Lu|Ag|Tc|Na|Mn|Zn|Rb|Sn|Xe|Ir|Pt|Os|Au|Re|W|Y)-\d{2,3}m?\d?\b")


def prose_lines(text):
    """The lines of a markdown file that are prose: outside fenced code, not
    a table rule, and with inline code and URLs removed."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or re.match(r"^\s*\|?\s*-{3,}", line):
            continue
        line = re.sub(r"`[^`]*`", "", line)
        line = re.sub(r"https?://\S+", "", line)
        out.append(line)
    return out


def test_no_em_or_en_dashes_anywhere_in_the_prose():
    offenders = [(p, i + 1) for p in DOCUMENTS
                 for i, line in enumerate(read(p).splitlines()) if "—" in line or "–" in line]
    assert not offenders, f"em or en dashes in prose: {offenders[:10]}"


def test_isotopes_are_written_as_superscripts_not_hyphenated():
    offenders = [(p, m.group(0)) for p in DOCUMENTS
                 for line in prose_lines(read(p)) for m in ISOTOPE_HYPHEN.finditer(line)]
    assert not offenders, f"hyphenated isotope designations: {offenders[:10]}"


def test_documents_carry_no_version_or_edition_notes():
    pattern = re.compile(r"\bv\d+\.\d+(\.\d+)?\b|\b(this|second|new) edition\b|\bchangelog\b", re.I)
    documents = [p for p in DOCUMENTS if p not in ("CHANGELOG.md",)]
    offenders = [(p, m.group(0)) for p in documents for m in pattern.finditer(read(p))]
    assert not offenders, f"version or edition notes inside a document: {offenders[:10]}"


def test_every_script_carries_the_copyright_and_licence_header():
    missing = []
    for p in tracked(".py"):
        head = read(p).split("\n", 4)[:4]
        if not any("Copyright 2026 Max Freedom Pollard" in l for l in head) or not any("SPDX-License-Identifier: Apache-2.0" in l for l in head):
            missing.append(p)
    assert not missing, f"scripts without the header: {missing}"
