"""Stream metadata must describe the PCM FFmpeg actually outputs."""

import io
import shutil
import subprocess
import wave
from types import SimpleNamespace

import pytest

from audioread import ffdec


def parse_output(log):
    reader = SimpleNamespace(proc=SimpleNamespace(stderr=io.BytesIO(log)))
    reader._parse_info = lambda text: ffdec.FFmpegAudioFile._parse_info(reader, text)
    ffdec.FFmpegAudioFile._get_info(reader)
    return reader


@pytest.mark.parametrize("stream_id", ["0:0", "0.0", "0:0(eng)", "0:0[0x1](eng)"])
def test_metadata_comes_from_output_stream(stream_id):
    reader = parse_output((
        "Input #0, matroska, from 'tracks.mka':\n"
        "  Duration: 00:00:03.20, start: 0.0, bitrate: 100 kb/s\n"
        "  Stream #0:0: Audio: pcm_s16le, 22050 Hz, mono, s16\n"
        "  Stream #0:1: Audio: pcm_s16le, 48000 Hz, stereo, s16 (default)\n"
        "Stream mapping:\n"
        "  Stream #0:1 -> #0:0 (pcm_s16le (native) -> pcm_s16le (native))\n"
        "Output #0, s16le, to 'pipe:':\n"
        "  Metadata:\n"
        "    description: audio: 123 Hz, mono, misleading metadata\n"
        "    title: Stream #0:0: Audio: pcm_s16le, 123 Hz, mono, s16\n"
        f"  Stream #{stream_id}: Audio: pcm_s16le, 48000 Hz, stereo, s16\n"
    ).encode())
    assert reader.channels == 2
    assert reader.samplerate == 48000
    assert reader.duration == pytest.approx(3.2)


@pytest.mark.parametrize("mode,channels", [("mono", 1), ("stereo", 2), ("5.1(side)", 6)])
def test_single_stream_and_missing_duration(mode, channels):
    reader = parse_output((
        "Input #0, wav, from 'audio.wav':\n"
        f"  Stream #0:0: Audio: pcm_s16le, 44100 Hz, {mode}, s16\n"
        "Output #0, s16le, to 'pipe:':\n"
        f"  Stream #0:0: Audio: pcm_s16le, 44100 Hz, {mode}, s16\n"
    ).encode())
    assert reader.channels == channels
    assert reader.samplerate == 44100
    assert reader.duration == 0


def test_input_info_without_output_does_not_report_success():
    with pytest.raises(ffdec.CommunicationError, match="stream info not found"):
        parse_output(
            b"Input #0, wav, from 'audio.wav':\n"
            b"  Stream #0:0: Audio: pcm_s16le, 44100 Hz, stereo, s16\n"
        )


@pytest.mark.parametrize("default_stream", [0, 1, None])
def test_selected_stream_metadata_matches_decoded_pcm(tmp_path, default_stream):
    command = shutil.which("ffmpeg")
    if command is None:
        pytest.skip("FFmpeg is not installed")

    inputs = []
    pcm = []
    specs = [(1, 22050), (2, 48000)]
    for index, (channels, rate) in enumerate(specs):
        path = tmp_path / f"track{index}.wav"
        data = (index + 1).to_bytes(2, "little", signed=True) * (rate // 10) * channels
        with wave.open(str(path), "wb") as output:
            output.setparams((channels, 2, rate, 0, "NONE", "not compressed"))
            output.writeframes(data)
        inputs.extend(["-i", str(path)])
        pcm.append(data)

    path = tmp_path / "tracks.mka"
    subprocess.run(
        [command, "-hide_banner", "-loglevel", "error", *inputs,
         "-map", "0:a", "-map", "1:a", "-c:a", "copy",
         "-disposition:a:0", "default" if default_stream == 0 else "0",
         "-disposition:a:1", "default" if default_stream == 1 else "0", str(path)],
        check=True, capture_output=True, timeout=10,
    )
    # Without a default disposition FFmpeg prefers the stereo track. Keep
    # automatic selection rather than forcing a different input stream.
    selected_stream = 1 if default_stream is None else default_stream
    with ffdec.FFmpegAudioFile(str(path)) as audio:
        data = b"".join(audio)
        assert audio.channels == specs[selected_stream][0]
        assert audio.samplerate == specs[selected_stream][1]
        assert data == pcm[selected_stream]


@pytest.mark.parametrize("consume", [False, True])
def test_existing_mp3_with_ffmpeg_backend(audiofile, consume):
    if not ffdec.available():
        pytest.skip("FFmpeg is not installed")
    with ffdec.FFmpegAudioFile(audiofile.path) as audio:
        assert audio.channels == audiofile.channels
        assert audio.samplerate == audiofile.samplerate
        assert int(audio.duration) == int(audiofile.duration)
        if consume:
            assert b"".join(audio)
