#!/bin/bash

# xhost + 127.0.0.1

# export DISPLAY=127.0.0.1:0

# docker run -u=$(id -u $USER):$(id -g $USER) -e DISPLAY=unix$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v $(pwd)/cma:/cma --rm cma
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v $(pwd)/cma:/cma --rm cma
sudo apt-get install x11-xserver-utils
xhost +
python launcher.py