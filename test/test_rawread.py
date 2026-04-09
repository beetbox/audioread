import os

from audioread.rawread import byteswap


def test_byteswap_known_values():
    # 16-bit words: 0x0102, 0xA0B0 -> swapped by bytes within each word.
    assert byteswap(b"\x01\x02\xa0\xb0") == b"\x02\x01\xb0\xa0"


def test_byteswap_roundtrip():
    data = os.urandom(4096)
    if len(data) % 2:
        data = data[:-1]
    assert byteswap(byteswap(data)) == data
