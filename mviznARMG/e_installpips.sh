#!/bin/bash
cd ~/Code
virtualenv --python=/usr/bin/python3 --system-site-packages venv
source venv/bin/activate
pip install SharedArray pylibmc shapely twisted numpy
