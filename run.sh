#!/bin/bash
self=$(readlink -f "$0")
START=$(dirname "${self}")

export LD_LIBRARY_PATH=${START}
./mpxgui.py
