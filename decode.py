"""Command-line tool to decode audio files to WAV files."""
import audioread
import sys
import os
import wave
import contextlib

def decode(filename):
    filename = os.path.abspath(os.path.expanduser(filename))
    with audioread.audio_open(filename) as f:
        print 'Input file: %i channels at %i Hz; %.1f seconds.' % \
              (f.channels, f.samplerate, f.duration)

        with contextlib.closing(wave.open(filename + '.wav', 'w')) as of:
            of.setnchannels(f.channels)
            of.setframerate(f.samplerate)
            of.setsampwidth(2)

            for buf in f:
                of.writeframes(buf)

if __name__ == '__main__':
    decode(sys.argv[1])
