import struct, os, math
from .mapping import parse_spec

class DS4:
    """
    Thin wrapper around /dev/input/js* to provide normalized RC channels.
    """
    _FMT = "@IhBB"

    def __init__(self, path, cfg):
        self._fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        self.cfg = cfg
        self.raw = [0]*8   # -32768..32767
        self.buttons = [0]*16
        self._build_maps()

    def _build_maps(self):
        self.axis_map = {}
        self.btn_map = {}
        for k, v in self.cfg.get("channels", {}).items():
            spec = parse_spec(v)
            if spec["type"] == "axis":
                self.axis_map[k] = spec
        for k, v in self.cfg.items():
            if k.startswith("aux"):
                spec = parse_spec(v)
                if spec["type"] == "button":
                    self.btn_map[k] = spec

    def update(self):
        while True:
            try:
                buf = os.read(self._fd, struct.calcsize(self._FMT))
                time, value, typ, number = struct.unpack(self._FMT, buf)
                if typ & 0x02:          # axis
                    if number < len(self.raw):
                        self.raw[number] = value
                elif typ & 0x01:        # button
                    if number < len(self.buttons):
                        self.buttons[number] = value
            except BlockingIOError:
                return

    def channels(self):
        out = [1500]*8
        expo = self.cfg.get("expo", 0.0)
        dead = self.cfg.get("deadband", 0)

        def apply_expo(x):
            return int(1500 + (x/32767.0)**(1+expo) * 500)

        for name, spec in self.axis_map.items():
            idx = spec["index"]
            v = self.raw[idx]
            if spec["negate"]:
                v = -v
            if abs(v) < dead*327:
                v = 0
            v = max(-32767, min(32767, v))
            ch = {"roll":0,"pitch":1,"throttle":2,"yaw":3}[name]
            out[ch] = apply_expo(v)
            if name == "throttle":
                out[ch] = int(1000 + (v+32767)/65534.0*1000)

        for name, spec in self.btn_map.items():
            idx = spec["index"]
            ch = {"aux1":4,"aux2":5,"aux3":6,"aux4":7}[name]
            out[ch] = 2000 if self.buttons[idx] else 1000

        return out