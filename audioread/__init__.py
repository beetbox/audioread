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

class DecodeError(Exception):
    """The base exception class for all decoding errors raised by this
    package.
    """

class NoBackendError(DecodeError):
    """The file could not be decoded by any backend. Either no backends
    are available or each available backend failed to decode the file.
    """

def _gst_available():
    """Determines whether Gstreamer bindings for GObject are installed."""
    try:
        from gi.repository import Gst
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
    # Standard-library WAV and AIFF readers.
    from . import rawread
    try:
        return rawread.RawAudioFile(path)
    except DecodeError:
        pass

    # Core Audio.
    if _ca_available():
        from . import macca
        try:
            return macca.ExtAudioFile(path)
        except DecodeError:
            pass

    # GStreamer.
    if _gst_available():
        from . import gstdec
        try:
            return gstdec.GstAudioFile(path)
        except DecodeError:
            pass

    # MAD.
    if _mad_available():
        from . import maddec
        try:
            return maddec.MadAudioFile(path)
        except DecodeError:
            pass

    # FFmpeg.
    from . import ffdec
    try:
        return ffdec.FFmpegAudioFile(path)
    except DecodeError:
        pass

    # All backends failed!
    raise NoBackendError()
