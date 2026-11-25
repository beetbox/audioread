import struct

import pytest

from audioread import audio_open
from audioread.rawread import RawAudioFile


def write_audio(path, container, compression, payload, channels):
    sample_width = 2 if compression == b'NONE' else 1
    frames = len(payload) // (channels * sample_width)
    if container == 'au':
        encoding = 3 if compression == b'NONE' else 1
        header = struct.pack('>4s5I', b'.snd', 24, len(payload),
                             encoding, 8000, channels)
        path.write_bytes(header + payload)
    else:
        # AIFF-C COMM includes an 80-bit 8000 Hz rate and an empty Pascal name.
        comm = struct.pack('>hIh', channels, frames, 16)
        comm += bytes.fromhex('400bfa00000000000000') + compression + b'\0\0'
        chunks = b'FVER' + struct.pack('>II', 4, 0xA2805140)
        chunks += b'COMM' + struct.pack('>I', len(comm)) + comm
        chunks += b'SSND' + struct.pack('>III', len(payload) + 8, 0, 0) + payload
        path.write_bytes(b'FORM' + struct.pack('>I', len(chunks) + 4)
                         + b'AIFC' + chunks)


@pytest.mark.parametrize('container,compression', [
    ('au', b'ULAW'),
    ('aifc', b'ulaw'),
    ('aifc', b'ULAW'),
    ('aifc', b'alaw'),
    ('aifc', b'ALAW'),
])
@pytest.mark.parametrize('channels', [1, 2])
@pytest.mark.parametrize('block_samples', [1, 3])
def test_g711_little_endian_pcm(tmp_path, container, compression, channels,
                              block_samples):
    codes = [0, 16, 85, 127, 128, 144, 213, 255]
    # G.711 decoded values, independently checked against FFmpeg.
    samples = (-32124, -15996, -716, 0, 32124, 15996, 716, 0)
    if compression.lower() == b'alaw':
        samples = (-5504, -2752, -8, -848, 5504, 2752, 8, 848)
    payload = bytes(code for code in codes for _ in range(channels))
    expected = struct.pack('<' + 'h' * len(payload),
                           *(s for s in samples for _ in range(channels)))
    path = tmp_path / ('samples.' + container)
    write_audio(path, container, compression, payload, channels)

    with audio_open(path, backends=[RawAudioFile]) as decoded:
        assert decoded.channels == channels
        assert decoded.samplerate == 8000
        assert decoded.duration == len(codes) / 8000
        assert b''.join(decoded.read_data(block_samples)) == expected


@pytest.mark.parametrize('container', ['au', 'aifc'])
@pytest.mark.parametrize('channels', [1, 2])
@pytest.mark.parametrize('block_samples', [1, 3])
def test_uncompressed_pcm_byte_order(tmp_path, container, channels,
                                     block_samples):
    samples = [-30000, -1000, -1, 0, 1, 1000, 10000, 30000] * channels
    payload = struct.pack('>' + 'h' * len(samples), *samples)
    path = tmp_path / ('samples.' + container)
    write_audio(path, container, b'NONE', payload, channels)
    with RawAudioFile(path) as decoded:
        assert b''.join(decoded.read_data(block_samples)) == struct.pack(
            '<' + 'h' * len(samples), *samples)
