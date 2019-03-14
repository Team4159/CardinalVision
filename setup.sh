#!/usr/bin/env bash

python3 setup.py install
sudo cp CardinalVision.service /etc/systemd/system/
sudo systemctl enable CardinalVision.service
