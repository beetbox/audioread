import aifc
import sunau
import wave

import pytest

import audioread
from audioread import rawread
from audioread.exceptions import NoBackendError


@pytest.fixture(
    params=[
        b"",
        b"FORM\x00\x00\x00\x5cAIFCFVER\x00\x00\x00\x04",
        b"RIFF\x34\x00\x00\x00WAVEfmt \x10\x00\x00\x00",
        b".snd\x00\x00\x00\x18",
    ],
    ids=["empty", "aiff", "wave", "au"],
)
def truncated_file(request, tmp_path):
    path = tmp_path / "truncated.audio"
    path.write_bytes(request.param)
    return path


def test_truncated_header_is_rejected_and_closed(truncated_file, monkeypatch):
    opened = []

    def tracking_open(*args, **kwargs):
        handle = open(*args, **kwargs)
        opened.append(handle)
        return handle

    monkeypatch.setattr(rawread, "open", tracking_open, raising=False)
    with pytest.raises(rawread.UnsupportedError):
        rawread.RawAudioFile(truncated_file)

    assert len(opened) == 1
    assert opened[0].closed


def test_truncated_header_allows_backend_fallback(truncated_file):
    fallback = object()

    def next_backend(path):
        assert path == truncated_file
        return fallback

    assert (
        audioread.audio_open(
            truncated_file, backends=[rawread.RawAudioFile, next_backend]
        )
        is fallback
    )


def test_truncated_header_without_fallback(truncated_file):
    with pytest.raises(NoBackendError):
        audioread.audio_open(truncated_file, backends=[rawread.RawAudioFile])


@pytest.mark.parametrize(
    "format_module", [aifc, wave, sunau], ids=["aiff", "wave", "au"]
)
def test_valid_raw_audio_still_decodes(format_module, tmp_path):
    path = tmp_path / "valid.audio"
    with format_module.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(8000)
        if format_module is aifc:
            writer.setcomptype(b"NONE", b"uncompressed")
        elif format_module is sunau:
            writer.setcomptype("NONE", "uncompressed")
        writer.writeframes(b"\x00\x00" * 8)

    with rawread.RawAudioFile(path) as reader:
        assert reader.channels == 1
        assert reader.samplerate == 8000
        assert reader.duration == 0.001
        assert b"".join(reader) == b"\x00\x00" * 8
    assert reader._fh.closed


def test_missing_raw_file_preserves_os_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        audioread.audio_open(
            tmp_path / "missing",
            backends=[
                rawread.RawAudioFile,
                lambda path: pytest.fail("Missing input must not fall back"),
            ],
        )
