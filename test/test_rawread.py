import os
import unittest
import audioread
from audioread import rawread


testFilename = os.path.abspath(os.path.join('test', 'fixtures', 'wavetest.wav'))
rowLookup = [
    b'\x00\x00',
    b'f2',
    b'\x008',
    b'3;',
]
numSamples = 512


class TestRawRead(unittest.TestCase):

    def test_open_as_generator(self):
        result = []
        with rawread.RawAudioFile(testFilename, block_samples=numSamples) as input_file:
            gen = input_file.read_data()
            try:
                while True:
                    data = next(gen)
                    result.append(data)
            except StopIteration:
                pass

        self.assertEqual(len(bytes(result[0])), numSamples*2)
        self.assertEqual(len(rowLookup), len(result))
        for i, row in enumerate(result):
            self.assertEqual(bytes(row[0:2]), rowLookup[i])


    def test_open_as_forloop(self):
        result = []
        with rawread.RawAudioFile(testFilename, block_samples=numSamples) as input_file:
            for buf in input_file:
                result.append(buf)

        for i, row in enumerate(result):
            self.assertEqual(bytes(row[0:2]), rowLookup[i])

    def test_seek(self):
        result = []
        with rawread.RawAudioFile(testFilename, block_samples=numSamples) as input_file:
            gen = input_file.read_data()

            # move forward
            row = next(gen)
            row = next(gen)
            row = next(gen)

            # go back
            input_file.seek(512)
            row = next(gen)
            self.assertEqual(bytes(row[0:2]), rowLookup[1])
            row = next(gen)
            self.assertEqual(bytes(row[0:2]), rowLookup[2])
