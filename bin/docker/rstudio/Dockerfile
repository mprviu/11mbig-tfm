FROM rocker/tidyverse:latest

MAINTAINER Mario del Pozo

# Install utilities and dependencies.
RUN set -eux; \
  apt-get update && apt-get install --assume-yes --no-install-recommends \
    tk \
    libgdal26 \
    libproj15 \
    libudunits2-0 \
  ; \
	rm -rf /var/lib/apt/lists/* 

# Install additional R packages.
# https://www.rocker-project.org/use/extending/
RUN set -eux; \
  install2.r kohonen plot3D plot3Drgl rnaturalearth rnaturalearthdata sf cowplot rgeos
