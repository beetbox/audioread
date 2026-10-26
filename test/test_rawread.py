import aifc
import os
import struct
import sunau
import sys
import wave

import pytest

from audioread.rawread import RawAudioFile, byteswap


def test_byteswap_known_values():
    # 16-bit words: 0x0102, 0xA0B0 -> swapped by bytes within each word.
    assert byteswap(b"\x01\x02\xa0\xb0") == b"\x02\x01\xb0\xa0"


def test_byteswap_roundtrip():
    data = os.urandom(4096)
    if len(data) % 2:
        data = data[:-1]
    assert byteswap(byteswap(data)) == data


@pytest.mark.parametrize("file_format", ["aiff", "au", "wav"])
@pytest.mark.parametrize("width", [1, 2, 3, 4])
@pytest.mark.parametrize("channels", [1, 2])
@pytest.mark.parametrize("block_samples", [1, 4])
def test_linear_pcm_width_conversion(tmp_path, file_format, width, channels,
                                     block_samples):
    if file_format == "wav" and width > 1 and sys.byteorder != "little":
        pytest.skip("Existing native-endian WAV output is outside this fix")
    values = [0, 1, -1, (1 << (width * 8 - 1)) - 1,
              -(1 << (width * 8 - 1)), 0]
    # Duplicate each sample per channel, with distinct signed extremes.
    samples = [value for value in values for _ in range(channels)]
    byteorder = sys.byteorder if file_format == "wav" else "big"
    if file_format == "wav" and width == 1:
        data = bytes(value + 128 for value in samples)
    else:
        data = b"".join(value.to_bytes(width, byteorder, signed=True)
                        for value in samples)
    path = str(tmp_path / ("samples." + file_format))
    writer = {"aiff": aifc, "au": sunau, "wav": wave}[file_format]
    with writer.open(path, "wb") as output:
        if file_format == "aiff":
            output.aiff()
        elif file_format == "au":
            output.setcomptype("NONE", "not compressed")
        output.setnchannels(channels)
        output.setsampwidth(width)
        output.setframerate(8000)
        output.writeframes(data)

    expected = [value << 8 if width == 1 else value >> (8 * (width - 2))
                for value in samples]
    with RawAudioFile(path) as decoded:
        assert decoded.channels == channels
        assert decoded.samplerate == 8000
        pcm = b"".join(decoded.read_data(block_samples=block_samples))
    assert pcm == struct.pack("<" + "h" * len(expected), *expected)
