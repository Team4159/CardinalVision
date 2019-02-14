#!/usr/bin/env bash

# This is the startup script for the Jetson
# See: https://devtalk.nvidia.com/default/topic/1029769/jetson-tx2/how-to-auto-run-shell-script-made-by-me-when-tx2-system-is-booted-/post/5238280/

python3 vision_server.py &

python3 stream_server.py &
