# Copyright 2026 Max Freedom Pollard
# SPDX-License-Identifier: Apache-2.0
#
# The OpenMC environment of neutron/ and ampoule/: the same OpenMC 0.16.0
# from conda-forge that the openmc.yml workflow installs, with the Python
# packages every other script in the repository needs. The nuclear data is
# not in the image; neutron/data.py streams the official ENDF/B-VIII.0
# archive into a directory you mount at /data (about 2 GB, once). conda-forge
# builds OpenMC 0.16.0 for x86-64 only, so the image is pinned to that
# platform; on an Apple silicon Mac Docker runs it under emulation, slowly.
#
#   docker build -t nuclear-compute .
#   docker run --rm -v "$PWD:/repo" -v "$HOME/nc-data:/data" nuclear-compute \
#       bash -c "python neutron/data.py --verify && python neutron/gate.py --quick && python neutron/report.py"
#
# Everything that needs no OpenMC runs in the same image too:
#
#   docker run --rm -v "$PWD:/repo" nuclear-compute python reproduce.py
FROM --platform=linux/amd64 mambaorg/micromamba:1.5.10
ARG MAMBA_DOCKERFILE_ACTIVATE=1
RUN micromamba install -y -n base -c conda-forge \
        python=3.12 "openmc=0.16.0=*nompi*" numpy matplotlib h5py markdown pytest \
    && micromamba clean --all --yes
ENV NC_DATA_DIR=/data
WORKDIR /repo
CMD ["python", "reproduce.py"]
