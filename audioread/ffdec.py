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

"""Read audio data using the ffmpeg command line tools via a UNIX
pipe.
"""
import subprocess
import re

class FFmpegCommunicationError(Exception):
    """Raised when the output of FFmpeg is not parseable."""
    pass

class FFmpegAudioFile(object):
    """An audio file decoded by the ffmpeg command-line utility."""
    def __init__(self, filename):
        self.proc = subprocess.Popen(
            ['ffmpeg', '-i', filename, '-f', 's16le', '-'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        self._get_info()

    def read_data(self, block_size=4096):
        """Read blocks of raw PCM data from the file."""
        while True:
            data = self.proc.stdout.read(block_size)
            if not data:
                break
            yield data

    def _get_info(self):
        """Reads the tool's output from its stderr stream, extracts the
        relevant information, and parses it.
        """
        out_parts = []
        while True:
            line = self.proc.stderr.readline()
            line = line.strip().lower()

            if 'no such file' in line:
                raise IOError('file not found')
            elif 'duration:' in line:
                out_parts.append(line)
            elif 'audio:' in line:
                out_parts.append(line)
                self._parse_info(''.join(out_parts))
                break

        else:
            # Data not found.
            raise FFmpegCommunicationError("stream info not found")

    def _parse_info(self, s):
        """Given relevant data from the ffmpeg output, set audio
        parameter fields on this object.
        """
        self.samplerate = int(re.search(r'(\d+) hz', s).group(1))

        mode = re.search(r'hz, ([^,]+),', s).group(1)
        if mode == 'stereo':
            self.channels = 2
        else:
            self.channels = 1

        durparts = re.search(
            r'duration: (\d+):(\d+):(\d+).(\d)', s
        ).groups()
        durparts = map(int, durparts)
        duration = durparts[0] * 60 * 60 + \
                   durparts[1] * 60 + \
                   durparts[2] + \
                   float(durparts[3]) / 10
        self.duration = duration

    def close(self):
        """Close the ffmpeg process used to perform the decoding."""
        if self.proc.returncode is None:
            self.proc.terminate()
            self.proc.communicate()

    def __del__(self):
        self.close()

    # Iteration.
    def __iter__(self):
        return self.read_data()

    # Context manager.
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
