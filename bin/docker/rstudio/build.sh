#!/bin/bash

VERSION=latest
IMAGE=mariodpros/rstudio

# Build image.
docker build -t ${IMAGE}:${VERSION} .
