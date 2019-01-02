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

from .version import version as __version__  # noqa


class DecodeError(Exception):
    """The base exception class for all decoding errors raised by this
    package.
    """


class NoBackendError(DecodeError):
    """The file could not be decoded by any backend. Either no backends
    are available or each available backend failed to decode the file.
    """


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


def _ffmpeg_available():
    """Determines whether the ffmpeg program is available."""
    from . import ffdec
    return ffdec.available()


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
    if _ffmpeg_available():
        from . import ffdec
        result.append(ffdec.FFmpegAudioFile)

    return result


def audio_open(path, backends=None):
    """Open an audio file using a library that is available on this
    system.

    If the 'backends' parameter is set, the function tries all backends in that
    list in order until one succeeds in reading the file. If all backends fail
    to read the file, a NoBackendError exception is raised.

    If the 'backends' parameter is not set, the function finds all available
    backends and tries them in turn.

    The process of finding available backends can be slow. If your program
    calls audio_open() many times, you should call the available_backends()
    yourself and pass the result to audio_open() each time you call it.

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
