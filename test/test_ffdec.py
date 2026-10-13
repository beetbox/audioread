"""FFmpeg startup must release resources even before both readers start."""

import pytest

import audioread
from audioread import ffdec


@pytest.fixture
def recording_backend():
    if not ffdec.available():
        pytest.skip('FFmpeg is not installed')
    instances = []

    class RecordingFFmpegAudioFile(ffdec.FFmpegAudioFile):
        def __new__(cls, *args, **kwargs):
            instance = super().__new__(cls)
            instances.append(instance)
            return instance

    yield RecordingFFmpegAudioFile, instances

    # Also clean up when testing against a version that leaks on startup.
    for instance in instances:
        proc = getattr(instance, 'proc', None)
        if proc is None:
            continue
        if proc.poll() is None:
            proc.kill()
        proc.wait(timeout=5)
        for name in ('stdout_reader', 'stderr_reader'):
            thread = getattr(instance, name, None)
            if thread is not None and thread.ident is not None:
                thread.join(timeout=5)
                assert not thread.is_alive()
        proc.stdout.close()
        proc.stderr.close()
        del instance.proc


def assert_closed(instance):
    assert instance.proc.poll() is not None
    assert instance.proc.stdout.closed
    assert instance.proc.stderr.closed
    for name in ('stdout_reader', 'stderr_reader'):
        thread = getattr(instance, name, None)
        if thread is not None:
            assert not thread.is_alive()
    # Explicit close, context exit and finalization can all reach close again.
    instance.close()
    instance.close()


@pytest.mark.parametrize('failure_at', [1, 2])
@pytest.mark.parametrize('error_type', [RuntimeError, KeyboardInterrupt])
def test_reader_start_failure_closes_resources(
        audiofile, recording_backend, monkeypatch, failure_at, error_type):
    backend, instances = recording_backend
    original_start = ffdec.QueueReaderThread.start
    error = error_type("can't start new thread")
    calls = 0

    def start(thread):
        nonlocal calls
        calls += 1
        if calls == failure_at:
            raise error
        return original_start(thread)

    monkeypatch.setattr(ffdec.QueueReaderThread, 'start', start)
    with pytest.raises(error_type) as raised:
        audioread.audio_open(audiofile.path, backends=[backend])
    assert raised.value is error
    assert_closed(instances[0])


@pytest.mark.parametrize('missing', [False, True])
def test_failed_probe_closes_resources(recording_backend, tmp_path, missing):
    backend, instances = recording_backend
    path = tmp_path / 'not-audio'
    if not missing:
        path.write_bytes(b'This is not an audio file.\n')
    expected = OSError if missing else audioread.NoBackendError
    with pytest.raises(expected):
        audioread.audio_open(str(path), backends=[backend])
    assert_closed(instances[0])


def test_full_decode_and_repeated_close(audiofile, recording_backend):
    backend, instances = recording_backend
    with audioread.audio_open(audiofile.path, backends=[backend]) as audio:
        assert audio.channels == audiofile.channels
        assert audio.samplerate == audiofile.samplerate
        assert sum(map(len, audio)) > 0
    assert_closed(instances[0])
