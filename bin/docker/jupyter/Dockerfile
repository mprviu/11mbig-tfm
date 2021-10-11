FROM jupyter/scipy-notebook:latest

MAINTAINER Mario del Pozo <mariodpros@gmail.com>

# Install additional libraries.
RUN set -eux; \
  conda install --yes --channel conda-forge \
    pandas-profiling \
    python-graphviz \
  ; \
	rm -rf /var/lib/apt/lists/* 

