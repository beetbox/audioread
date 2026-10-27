from io import BytesIO
from types import SimpleNamespace
import wave

import pytest

import audioread
from audioread import ffdec
from audioread.rawread import RawAudioFile


LINKER_ERROR = (
    b"ffmpeg: error while loading shared libraries: libAVdevice.so.56: "
    b"cannot open shared object file: No such file or directory\n"
)


def get_info(stderr):
    reader = SimpleNamespace(proc=SimpleNamespace(stderr=BytesIO(stderr)))
    ffdec.FFmpegAudioFile._get_info(reader)


@pytest.mark.parametrize(
    "stderr",
    [
        LINKER_ERROR,
        LINKER_ERROR.replace(b"ffmpeg:", b"/usr/bin/avconv:"),
        LINKER_ERROR.replace(b"No such file or directory", b"Permission denied"),
    ],
)
def test_shared_library_error_is_backend_failure(stderr):
    with pytest.raises(ffdec.NotInstalledError) as exc:
        get_info(stderr)
    assert str(exc.value) == stderr.decode().strip()


def test_missing_audio_file_remains_os_error():
    with pytest.raises(OSError, match="file not found"):
        get_info(b"missing.mp3: No such file or directory\n")


def test_invalid_audio_file_remains_unsupported_error():
    with pytest.raises(ffdec.UnsupportedError):
        get_info(b"bad.dat: Invalid data found when processing input\n")


def broken_ffmpeg_backend(path):
    get_info(LINKER_ERROR)


def test_shared_library_error_allows_backend_fallback(tmp_path):
    path = tmp_path / "valid.wav"
    pcm = b"\x00\x00" * 8
    with wave.open(str(path), "wb") as output:
        output.setparams((1, 2, 8000, 0, "NONE", "not compressed"))
        output.writeframes(pcm)

    with audioread.audio_open(
        path, backends=[broken_ffmpeg_backend, RawAudioFile]
    ) as audio:
        assert audio.channels == 1
        assert audio.samplerate == 8000
        assert b"".join(audio) == pcm


def test_shared_library_error_without_fallback_is_no_backend_error():
    with pytest.raises(audioread.NoBackendError):
        audioread.audio_open("unused.wav", backends=[broken_ffmpeg_backend])
