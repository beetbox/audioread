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

"""Command-line tool to decode audio files to WAV files."""
from __future__ import print_function
import audioread
import sys
import os
import wave
import contextlib


def decode(filename=None):
    """Decode audio from a file on disk or, if no file is specified,
    from the standard input.
    """
    if filename:
        filename = os.path.abspath(os.path.expanduser(filename))
        if not os.path.exists(filename):
            print("File not found.", file=sys.stderr)
            sys.exit(1)

    try:
        if filename:
            f = audioread.audio_open(filename)
        else:
            f = audioread.decode(sys.stdin)

        with f:
            print('Input file: %i channels at %i Hz; %.1f seconds.' %
                  (f.channels, f.samplerate, f.duration),
                  file=sys.stderr)
            print('Backend:', str(type(f).__module__).split('.')[1],
                  file=sys.stderr)

            outname = filename or 'out'
            with contextlib.closing(wave.open(outname + '.wav', 'w')) as of:
                of.setnchannels(f.channels)
                of.setframerate(f.samplerate)
                of.setsampwidth(2)

                for buf in f:
                    of.writeframes(buf)

    except audioread.DecodeError:
        print("File could not be decoded.", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    if sys.argv[1:]:
        decode(sys.argv[1])
    else:
        decode()
