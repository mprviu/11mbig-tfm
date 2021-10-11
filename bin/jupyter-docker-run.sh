#!/bin/bash

if [ "$UID" != "0" -a "$EUID" != "0" ]
then
  echo "This script must be run as root."
  exit 1
fi

# https://jupyter-docker-stacks.readthedocs.io/en/latest/using/common.html
# https://github.com/jupyter/docker-stacks/blob/master/base-notebook/start.sh

NAME=jupyter-$(basename "$PWD")

docker run \
  --rm \
  --name $NAME \
  -p 8888:8888 \
  --user root \
  -e NB_GID=1000 \
  -e JUPYTER_ENABLE_LAB=yes \
  -v "$PWD":/home/jovyan/work \
  -v "$PWD"/projects/jupyter/config:/home/jovyan/.jupyter \
  mariodpros/jupyter-scipy:latest \
  start-notebook.sh \
  --ServerApp.token=''

