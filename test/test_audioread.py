import os
import unittest
import audioread
from audioread import rawread, macca

testMaccaFilename = os.path.abspath(os.path.join('test', 'fixtures', 'test.wav'))

rowLookup = [
    b'\x00\x00',
    b'\x9a\x19',
    b'\x00@',
    b'3s',
]
numSamples = 512

class TestAudioread(unittest.TestCase):

    def test_audio_open_as_generator(self):
        result = []
        with audioread.audio_open(testMaccaFilename, block_samples=numSamples) as f:
            gen = f.read_data()
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


    def test_audio_open_as_forloop(self):
        result = []
        with audioread.audio_open(testMaccaFilename, block_samples=numSamples) as f:
            self.assertEqual(f.nframes, 2048)
            for buf in f:
                result.append(buf)

        self.assertEqual(len(bytes(result[0])), numSamples*2)
        self.assertEqual(len(rowLookup), len(result))
        for i, row in enumerate(result):
            self.assertEqual(bytes(row[0:2]), rowLookup[i])


class TestMacca(unittest.TestCase):

    def test_macca_as_generator(self):
        result = []
        with macca.ExtAudioFile(testMaccaFilename, block_samples=numSamples) as f:
            gen = f.read_data()
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


    def test_macca_as_forloop(self):
        result = []
        with macca.ExtAudioFile(testMaccaFilename, block_samples=numSamples) as f:
            self.assertEqual(f.nframes, 2048)
            for buf in f:
                result.append(buf)

        self.assertEqual(len(bytes(result[0])), numSamples*2)
        self.assertEqual(len(rowLookup), len(result))
        for i, row in enumerate(result):
            self.assertEqual(bytes(row[0:2]), rowLookup[i])

    def test_seek(self):
        result = []
        with macca.ExtAudioFile(testMaccaFilename, block_samples=numSamples) as input_file:
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


testWaveFilename = os.path.abspath(os.path.join('test', 'fixtures', 'wavetest2.wave'))
waveRowLookup = [
    b'\x00\x00',
    b'f2',
    b'\x008',
    b'3;',
]

class TestRawRead(unittest.TestCase):

    def test_open_as_generator(self):
        result = []
        with rawread.RawAudioFile(testWaveFilename, block_samples=numSamples) as input_file:
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
            self.assertEqual(bytes(row[0:2]), waveRowLookup[i])


    def test_open_as_forloop(self):
        result = []
        with audioread.rawread.RawAudioFile(testWaveFilename, block_samples=numSamples) as input_file:
            print(input_file.channels, input_file.samplerate, input_file.duration)
            for buf in input_file:
                result.append(buf)

        for i, row in enumerate(result):
            self.assertEqual(bytes(row[0:2]), waveRowLookup[i])

    def test_seek(self):
        result = []
        with rawread.RawAudioFile(testWaveFilename, block_samples=numSamples) as input_file:
            gen = input_file.read_data()

            # move forward
            row = next(gen)
            row = next(gen)
            row = next(gen)

            # go back
            input_file.seek(512)
            row = next(gen)
            self.assertEqual(bytes(row[0:2]), waveRowLookup[1])
            row = next(gen)
            self.assertEqual(bytes(row[0:2]), waveRowLookup[2])


if __name__ == '__main__':
    unittest.main()
