import struct

def encode_msp_rc(channels):
    """
    channels : list[int] 1000-2000 μs  (8 values)
    returns  bytes ready to send
    """
    if len(channels) != 8:
        raise ValueError("Need 8 channels")
    payload = struct.pack("<8H", *[max(1000, min(2000, c)) for c in channels])
    length = len(payload)
    msp_id = 200            # MSP_SET_RAW_RC
    checksum = 0
    for b in bytes([length, msp_id]) + payload:
        checksum ^= b
    return b'$M<' + bytes([length, msp_id]) + payload + bytes([checksum])