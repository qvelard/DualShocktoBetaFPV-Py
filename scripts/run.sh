#!/usr/bin/env bash
JS=${1:-/dev/input/js0}
TTY=${2:-/dev/ttyUSB0}
exec sudo python3 ds4_to_betafpv.py --js "$JS" --serial "$TTY"