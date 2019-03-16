#!/usr/bin/env bash

python3 setup.py develop
cp CardinalVision.service /etc/systemd/system/
systemctl enable CardinalVision.service
