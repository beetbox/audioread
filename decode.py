"""Command-line tool to decode audio files to raw PCM."""
import audioread
import sys
import os

def decode(filename):
    filename = os.path.abspath(os.path.expanduser(filename))
    with audioread.audio_open(filename) as f:
        print 'Input file: %i channels at %i Hz; %.1f seconds.' % \
              (f.channels, f.samplerate, f.duration)
        with open(filename + '.pcm', 'wb') as of:
            for buf in f:
                of.write(buf)

if __name__ == '__main__':
    decode(sys.argv[1])
