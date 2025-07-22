def parse_spec(s:str):
    """
    "axis:0"        -> {"type":"axis","index":0,"negate":False}
    "axis:1,negate" -> {"type":"axis","index":1,"negate":True}
    "button:2"      -> {"type":"button","index":2}
    """
    parts = s.split(",")
    typ, idx = parts[0].split(":")
    return {
        "type": typ,
        "index": int(idx),
        "negate": "negate" in parts[1:]
    }