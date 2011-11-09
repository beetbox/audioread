"""Decode audio files."""

def _gst_available():
    """Determines whether pygstreamer is installed."""
    try:
        import gst
    except ImportError:
        return False
    else:
        return True

def _ca_available():
    """Determines whether CoreAudio is available (i.e., we're running on
    Mac OS X).
    """
    import ctypes.util
    lib = ctypes.util.find_library('AudioToolbox')
    return lib is not None

def _mad_available():
    """Determines whether the pymad bindings are available."""
    try:
        import mad
    except ImportError:
        return False
    else:
        return True

def audio_open(path):
    """Open an audio file using a library that is available on this
    system.
    """
    if _ca_available():
        from . import macca
        return macca.ExtAudioFile(path)
    elif _gst_available():
        from . import gstdec
        return gstdec.GstAudioFile(path)
    elif _mad_available():
        from . import maddec
        return maddec.MadAudioFile(path)
    else:
        import ffdec
        return ffdec.FFmpegAudioFile(path)
