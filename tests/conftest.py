# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
"""Shared helpers: the repository root, the tracked files, and a loader for
the scripts, which are written to be run and not imported."""
import importlib.util
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tracked(suffix=""):
    """Every file git tracks, optionally filtered by suffix."""
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p.endswith(suffix)]


def read(path):
    return open(os.path.join(ROOT, path), encoding="utf-8").read()


def load_script(path, name=None):
    """Import a script by path without running its main(); the neutron and
    ampoule directories are put on sys.path the way the scripts expect."""
    full = os.path.join(ROOT, path)
    name = name or os.path.basename(path)[:-3] + "_under_test"
    for d in ("neutron", "ampoule", "gates"):
        p = os.path.join(ROOT, d)
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location(name, full)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def root():
    return ROOT
