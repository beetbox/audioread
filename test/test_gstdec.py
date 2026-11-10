"""GStreamer metadata compatibility across structure binding versions."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

gi = pytest.importorskip('gi')
try:
    gi.require_version('Gst', '1.0')
except ValueError:
    pytest.skip('GStreamer introspection is unavailable', allow_module_level=True)
from audioread.gstdec import Gst, GstAudioFile, MetadataMissingError


@pytest.mark.parametrize('duration_available', [True, False])
@pytest.mark.parametrize('structure_mode', ['native', 'direct'])
def test_caps_metadata(structure_mode, duration_available):
    caps = Gst.Caps.from_string('audio/x-raw,channels=(int)2,rate=(int)16000')
    if structure_mode == 'direct':
        # Older Gst Python bindings returned Gst.Structure directly.
        structure = Gst.Structure.new_from_string(
            'audio/x-raw,channels=(int)2,rate=(int)16000'
        )
        caps = SimpleNamespace(get_structure=lambda index: structure)
    peer = SimpleNamespace(query_duration=lambda fmt: (duration_available, 2500000000))
    pad = SimpleNamespace(get_current_caps=lambda: caps, get_peer=lambda: peer)
    reader = SimpleNamespace(ready_sem=Mock(), read_exc=None)

    GstAudioFile._notify_caps(reader, pad, None)

    assert reader.got_caps
    assert reader.channels == 2
    assert reader.samplerate == 16000
    reader.ready_sem.release.assert_called_once_with()
    if duration_available:
        assert reader.duration == 2.5
        assert reader.read_exc is None
    else:
        assert isinstance(reader.read_exc, MetadataMissingError)
