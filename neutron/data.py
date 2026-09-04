#!/usr/bin/env python3
# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""
Nuclear data for the neutron sector: the official OpenMC ENDF/B-VIII.0
library, fetched once and cached.

The library is the one the OpenMC project distributes at openmc.org
(ENDF/B-VIII.0 processed to HDF5 by NJOY, neutron data at 250 to 2500 K,
thermal scattering at 284 to 800 K). The archive is 3.4 GB compressed and
13.7 GB unpacked, and this machine needs 129 files from it, so the archive
is streamed and only those members are written to disk: about 2 GB,
the two large ones being the uranium evaluations and the water thermal
scattering law. Nothing is modified; the files are the library's own.

The cache lives in neutron/data/ (ignored by git) unless NC_DATA_DIR
points elsewhere; if OPENMC_CROSS_SECTIONS is already set it is used as
is and nothing is downloaded. `python3 data.py` fetches and verifies.
"""
import lzma
import os
import sys
import tarfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LIBRARY = "endfb-viii.0-hdf5"
ARCHIVE_URL = ("https://anl.box.com/shared/static/"
               "uhbxlrx7hvxqw27psymfbhi7bx7s6u6a.xz")

# every nuclide the gate, the benchmarks, and the feedback runs touch
NUCLIDES = [
    "H1", "O16", "O17", "N14", "F19",                        # solution, air
    "Al27", "Si28", "Si29", "Si30", "Mn55",                  # type 1100 Al
    "Cu63", "Cu65", "Zn64", "Zn66", "Zn67", "Zn68", "Zn70",
    "Cd106", "Cd108", "Cd110", "Cd111", "Cd112", "Cd113",    # the sheet
    "Cd114", "Cd116",
    "B10", "B11", "C12", "C13",                              # the blade
    "Cr50", "Cr52", "Cr53", "Cr54", "Fe54", "Fe56", "Fe57",  # stainless steel,
    "Fe58", "Ni58", "Ni60", "Ni61", "Ni62", "Ni64", "P31",   # for the SHEBA-II
    "S32", "S33", "S34", "S36", "N15", "U236",               # and STACY benchmarks
    "U234", "U235", "U238",                                  # the fuel
    # the ampoule's materials (/ampoule): OpenMC expands an element into its
    # natural isotopes and needs their neutron files even in a photon run
    "Sr84", "Sr86", "Sr87", "Sr88", "Ti46", "Ti47", "Ti48", "Ti49", "Ti50", "Y89",
    "Kr78", "Kr80", "Kr82", "Kr83", "Kr84", "Kr86",
    "Mo92", "Mo94", "Mo95", "Mo96", "Mo97", "Mo98", "Mo100",
    "Cs133", "I127", "Te120", "Te122", "Te123", "Te124", "Te125", "Te126", "Te128", "Te130",
    "W180", "W182", "W183", "W184", "W186", "Pb204", "Pb206", "Pb207", "Pb208",
    "Mg24", "Mg25", "Mg26", "K39", "K40", "K41", "Na23",
]
THERMAL = ["c_H_in_H2O"]
# photoatomic and electron data for the ampoule's materials (/ampoule): the
# source ceramic and capsule, krypton, the glass and scintillator of the
# compute shell, tungsten and lead, the detectors, and the shield
PHOTON = ["H", "B", "C", "N", "O", "F", "Na", "Mg", "Al", "Si", "K", "Ti", "Cr", "Mn",
          "Fe", "Ni", "Mo", "Kr", "Sr", "Y", "Zn", "Cd", "Te", "Cs", "I", "W", "Pb"]
MEMBERS = ([f"{LIBRARY}/neutron/{n}.h5" for n in NUCLIDES] +
           [f"{LIBRARY}/thermal/{t}.h5" for t in THERMAL] +
           [f"{LIBRARY}/photon/{e}.h5" for e in PHOTON])


def data_dir():
    return os.environ.get("NC_DATA_DIR", os.path.join(HERE, "data"))


def cross_sections_path():
    return os.path.join(data_dir(), LIBRARY, "cross_sections.xml")


def missing(root):
    return [m for m in MEMBERS if not os.path.exists(os.path.join(root, m))]


def stream_extract(root, wanted, log=print):
    """One sequential pass over the compressed archive, writing only the
    wanted members. Stops as soon as the last of them has been written."""
    wanted = set(wanted)
    log(f"streaming {ARCHIVE_URL}")
    log(f"  {len(wanted)} members wanted; this reads the whole 3.4 GB archive "
        "once and keeps about 1.5 GB")
    req = urllib.request.Request(ARCHIVE_URL, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=120)
    with lzma.open(resp) as xz, tarfile.open(fileobj=xz, mode="r|") as tar:
        for member in tar:
            if member.name in wanted:
                dest = os.path.join(root, member.name)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                src = tar.extractfile(member)
                with open(dest, "wb") as out:
                    while True:
                        chunk = src.read(1 << 22)
                        if not chunk:
                            break
                        out.write(chunk)
                wanted.discard(member.name)
                log(f"  wrote {member.name} ({member.size/1e6:.0f} MB), "
                    f"{len(wanted)} to go")
                if not wanted:
                    break
    if wanted:
        raise RuntimeError(f"archive ended before these were found: {sorted(wanted)}")


def write_cross_sections(root):
    lines = ['<?xml version="1.0"?>', "<cross_sections>"]
    for n in NUCLIDES:
        lines.append(f'  <library materials="{n}" path="neutron/{n}.h5" type="neutron" />')
    for t in THERMAL:
        lines.append(f'  <library materials="{t}" path="thermal/{t}.h5" type="thermal" />')
    for e in PHOTON:
        lines.append(f'  <library materials="{e}" path="photon/{e}.h5" type="photon" />')
    lines.append("</cross_sections>")
    path = os.path.join(root, LIBRARY, "cross_sections.xml")
    open(path, "w").write("\n".join(lines) + "\n")
    return path


def ensure_data(log=print):
    """Return the path of a cross_sections.xml covering every nuclide this
    directory uses, fetching the library on first call."""
    if os.environ.get("OPENMC_CROSS_SECTIONS") and not os.environ.get("NC_FORCE_LIBRARY"):
        return os.environ["OPENMC_CROSS_SECTIONS"]
    root = data_dir()
    need = missing(root)
    if need:
        stream_extract(root, need, log)
    path = write_cross_sections(root)
    os.environ["OPENMC_CROSS_SECTIONS"] = path
    return path


def verify(log=print):
    """Open every file with OpenMC's data reader and report its temperatures."""
    import openmc.data
    root = data_dir()
    for n in NUCLIDES:
        d = openmc.data.IncidentNeutron.from_hdf5(os.path.join(root, LIBRARY, "neutron", n + ".h5"))
        log(f"  {n:6s} {', '.join(sorted(d.temperatures, key=lambda s: float(s[:-1])))}")
    for t in THERMAL:
        d = openmc.data.ThermalScattering.from_hdf5(os.path.join(root, LIBRARY, "thermal", t + ".h5"))
        log(f"  {t}: {', '.join(sorted(d.temperatures, key=lambda s: float(s[:-1])))}")
    for e in PHOTON:
        d = openmc.data.IncidentPhoton.from_hdf5(os.path.join(root, LIBRARY, "photon", e + ".h5"))
        log(f"  {e:3s} photoatomic, Z = {d.atomic_number}, {len(d.reactions)} reactions, "
            f"bremsstrahlung {'yes' if d.bremsstrahlung else 'no'}")


if __name__ == "__main__":
    path = ensure_data()
    print("cross sections:", path)
    if "--verify" in sys.argv:
        verify()
