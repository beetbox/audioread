# This file is part of audioread.
# Tests for ffdec.py parsing logic.

import io

import pytest

from audioread.ffdec import FFmpegAudioFile


class _FakeProc:
    """Minimal subprocess stand-in for testing _get_info without ffmpeg."""

    def __init__(self, stderr_lines):
        self.stderr = io.BytesIO(b"".join(
            line if line.endswith(b"\n") else line + b"\n"
            for line in stderr_lines
        ))
        self.stdout = io.BytesIO(b"")
        self.returncode = 0

    def poll(self):
        pass

    def kill(self):
        pass

    def wait(self):
        pass


def _parse_from_lines(stderr_lines):
    """Call FFmpegAudioFile._get_info with fake process stderr lines.

    Returns an object with `channels`, `samplerate`, and `duration`
    attributes as parsed by the real _get_info / _parse_info code, without
    running ffmpeg.
    """
    obj = FFmpegAudioFile.__new__(FFmpegAudioFile)
    obj.proc = _FakeProc(stderr_lines)
    FFmpegAudioFile._get_info(obj)
    return obj


NORMAL_FFMPEG_OUTPUT = [
    b"Input #0, mp3, from 'test.mp3':",
    b"  Duration: 00:00:02.0, start: 0.000000, bitrate: 128 kb/s",
    b"    Stream #0:0: Audio: mp3, 44100 Hz, stereo, fltp, 128 kb/s",
]

# File whose metadata contains the substring "audio:" – triggers the bug.
METADATA_AUDIO_FFMPEG_OUTPUT = [
    b"Input #0, mp3, from 'out.mp3':",
    b"  Metadata:",
    b"    description     : audio: broken",
    b"    encoder         : Lavf58.29.100",
    b"  Duration: 00:00:02.04, start: 0.025057, bitrate: 129 kb/s",
    b"    Stream #0:0: Audio: mp3, 44100 Hz, stereo, fltp, 128 kb/s",
]


def test_normal_parse():
    """Normal ffmpeg output is parsed correctly."""
    af = _parse_from_lines(NORMAL_FFMPEG_OUTPUT)
    assert af.channels == 2
    assert af.samplerate == 44100
    assert af.duration == pytest.approx(2.0, abs=0.2)


def test_metadata_containing_audio_colon():
    """Metadata field 'audio: …' must not be mistaken for the stream line.

    Regression test for https://github.com/beetbox/audioread/issues/119.
    When a file has a metadata tag whose value contains the substring
    'audio:', the previous code matched that metadata line instead of the
    real stream descriptor, resulting in channels=0, samplerate=0,
    and duration=0.
    """
    af = _parse_from_lines(METADATA_AUDIO_FFMPEG_OUTPUT)
    assert af.channels == 2
    assert af.samplerate == 44100
    assert af.duration == pytest.approx(2.04, abs=0.2)
