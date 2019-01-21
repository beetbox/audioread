# This file is part of audioread.
# Copyright 2013, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Decode audio files."""

from . import ffdec
from .exceptions import DecodeError, NoBackendError
from .version import version as __version__  # noqa


def _gst_available():
    """Determine whether Gstreamer and the Python GObject bindings are
    installed.
    """
    try:
        import gi
    except ImportError:
        return False

    try:
        gi.require_version('Gst', '1.0')
    except (ValueError, AttributeError):
        return False

    try:
        from gi.repository import Gst  # noqa
    except ImportError:
        return False

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
        import mad  # noqa
    except ImportError:
        return False
    else:
        return True


def available_backends():
    """Returns a list of backends that are available on this system."""

    # Standard-library WAV and AIFF readers.
    from . import rawread
    result = [rawread.RawAudioFile]

    # Core Audio.
    if _ca_available():
        from . import macca
        result.append(macca.ExtAudioFile)

    # GStreamer.
    if _gst_available():
        from . import gstdec
        result.append(gstdec.GstAudioFile)

    # MAD.
    if _mad_available():
        from . import maddec
        result.append(maddec.MadAudioFile)

    # FFmpeg.
    if ffdec.available():
        result.append(ffdec.FFmpegAudioFile)

    return result


def audio_open(path, backends=None):
    """Open an audio file using a library that is available on this
    system.

    The optional `backends` parameter can be a list of audio file
    classes to try opening the file with. If it is not provided,
    `audio_open` tries all available backends. If you call this function
    many times, you can avoid the cost of checking for available
    backends every time by calling `available_backends` once and passing
    the result to each `audio_open` call.

    If all backends fail to read the file, a NoBackendError exception is
    raised.
    """
    if backends is None:
        backends = available_backends()

    for BackendClass in backends:
        try:
            return BackendClass(path)
        except DecodeError:
            pass

    # All backends failed!
    raise NoBackendError()


def decode(audio):
    """Given a file-like object containing encoded audio data, create an
    audio file object that produces its *raw* data.
    """
    # FFmpeg.
    from . import ffdec
    try:
        return ffdec.FFmpegAudioFile(audio=audio)
    except DecodeError:
        pass

    # All backends failed!
    raise NoBackendError()
