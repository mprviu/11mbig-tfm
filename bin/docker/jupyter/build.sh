#!/bin/bash

VERSION=latest
IMAGE=mariodpros/jupyter-scipy

# Build image.
docker build -t ${IMAGE}:${VERSION} .
