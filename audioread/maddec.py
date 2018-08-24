# This file is part of audioread.
# Copyright 2011, Adrian Sampson.
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

"""Decode MPEG audio files with MAD (via pymad)."""
import mad
from . import DecodeError


class UnsupportedError(DecodeError):
    """The file is not readable by MAD."""


class MadAudioFile(object):
    """MPEG audio file decoder using the MAD library."""
    def __init__(self, filename, block_samples=4096):
        self.block_samples = block_samples
        self.fp = open(filename, 'rb')
        self.mf = mad.MadFile(self.fp)
        if not self.mf.total_time():  # Indicates a failed open.
            self.fp.close()
            raise UnsupportedError()

    def close(self):
        if hasattr(self, 'fp'):
            self.fp.close()
        if hasattr(self, 'mf'):
            del self.mf

    def read_blocks(self, block_size=None):
        """Generates buffers containing PCM data for the audio file.
        """
        block_samples = block_size or self.block_samples
        while True:
            out = self.mf.read(block_samples)
            if not out:
                break
            yield out

    @property
    def samplerate(self):
        """Sample rate in Hz."""
        return self.mf.samplerate()

    @property
    def duration(self):
        """Length of the audio in seconds (a float)."""
        return float(self.mf.total_time()) / 1000

    @property
    def channels(self):
        """The number of channels."""
        if self.mf.mode() == mad.MODE_SINGLE_CHANNEL:
            return 1
        elif self.mf.mode() in (mad.MODE_DUAL_CHANNEL,
                                mad.MODE_JOINT_STEREO,
                                mad.MODE_STEREO):
            return 2
        else:
            # Other mode?
            return 2

    def __del__(self):
        self.close()

    # Iteration.
    def __iter__(self):
        return self.read_blocks()

    # Context manager.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
