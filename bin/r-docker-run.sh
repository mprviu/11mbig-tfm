#!/bin/bash

if [ "$UID" != "0" -a "$EUID" != "0" ]
then
  echo "This script must be run as root."
  exit 1
fi

# https://www.rocker-project.org/
# https://hub.docker.com/r/rocker/tidyverse

# Navigate to http://localhost:8787 and you should be logged into RStudio as the rstudio user without
# needing a password.

CONTAINER_NAME=rstudio-$(basename "$PWD")
if [ "$(sudo docker ps -q -f name=$CONTAINER_NAME)" ]; then
  CONTAINER_NAME=rstudio-$(basename "$PWD")-$(date +%y%m%d%H%M%S)
fi

docker run \
  --rm \
  --name $CONTAINER_NAME \
  -p 127.0.1.1:8787:8787 \
  -e DISABLE_AUTH=true \
  -v "$PWD":/home/rstudio/work \
  mariodpros/rstudio:latest

