"""Uses standard-library modules to read AIFF, AIFF-C, and WAV files."""
import wave
import aifc
import audioop
import struct

TARGET_WIDTH = 2

class UnsupportedError(Exception):
    """File is neither an AIFF nor a WAV file."""

def byteswap(s):
    """Swaps the endianness of the bytesting s, which must be an array
    of shorts (16-bit signed integers). This is probably less efficient
    than it should be.
    """
    assert len(s) % 2 == 0
    parts = []
    for i in xrange(0, len(s), 2):
        chunk = s[i:i+2]
        newchunk =struct.pack('<h', *struct.unpack('>h', chunk))
        parts.append(newchunk)
    return ''.join(parts)

class RawAudioFile(object):
    """An AIFF or WAV file that can be read by the Python standard
    library modules ``wave`` and ``aifc``.
    """
    def __init__(self, filename):
        try:
            self._file = aifc.open(filename)
            self._is_aif = True
            return
        except aifc.Error:
            pass

        try:
            self._file = wave.open(filename)
            self._is_aif = False
            return
        except wave.Error:
            pass

        raise UnsupportedError()
    
    def close(self):
        """Close the underlying file."""
        self._file.close()

    @property
    def channels(self):
        """Number of audio channels."""
        return self._file.getnchannels()

    @property
    def samplerate(self):
        """Sample rate in Hz."""
        return self._file.getframerate()

    @property
    def duration(self):
        """Length of the audio in seconds (a float)."""
        return float(self._file.getnframes()) / self.samplerate

    def read_data(self, block_samples=1024):
        """Generates blocks of PCM data found in the file."""
        old_width = self._file.getsampwidth()

        while True:
            data = self._file.readframes(block_samples)
            if not data:
                break

            # Make sure we have the desired bitdepth and endianness.
            data = audioop.lin2lin(data, old_width, TARGET_WIDTH)
            if self._is_aif and self._file.getcomptype() != 'sowt':
                # Big-endian data. Swap endianness.
                data = byteswap(data)
            yield data

    # Context manager.
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    # Iteration.
    def __iter__(self):
        return self.read_data()
