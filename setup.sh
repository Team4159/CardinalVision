#!/usr/bin/env bash

python3 setup.py develop
sudo cp CardinalVision.service /etc/systemd/system/
sudo systemctl enable CardinalVision.service
