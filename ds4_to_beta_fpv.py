#!/usr/bin/env python3
"""
Entry point.
"""
import argparse, signal, sys, time, yaml, serial
from ds4 import DS4
from msp import encode_msp_rc

def load_cfg(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--js", default="/dev/input/js0")
    ap.add_argument("--serial", default="/dev/ttyUSB0")
    ap.add_argument("--rate", type=int, default=50)
    ap.add_argument("--cfg", default="config.yaml")
    args = ap.parse_args()

    cfg = load_cfg(args.cfg)
    ds4 = DS4(args.js, cfg)
    ser = serial.Serial(args.serial, 115200, timeout=0.01)

    running = True
    def stop(*_):
        nonlocal running
        running = False
    signal.signal(signal.SIGINT, stop)

    period = 1.0 / args.rate
    next_t = time.perf_counter()
    while running:
        ds4.update()
        channels = ds4.channels()
        ser.write(encode_msp_rc(channels))
        next_t += period
        time.sleep(max(0, next_t - time.perf_counter()))

    ser.close()
    print("\nBye!")

if __name__ == "__main__":
    main()