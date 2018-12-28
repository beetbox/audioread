import os
import unittest
import audioread

numSamples = 512

testFilename = os.path.abspath(os.path.join('test', 'fixtures', 'wavetest.wav'))
rowLookup = [
    b'\x00\x00',
    b'f2',
    b'\x008',
    b'3;',
]

class TestAudioreadWav(unittest.TestCase):

    def test_audio_open_as_generator(self):
        result = []
        with audioread.audio_open(testFilename, block_samples=numSamples) as f:
            print('wav decode class', f.__class__)
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
        with audioread.audio_open(testFilename, block_samples=numSamples) as f:
            self.assertEqual(f.nframes, 2048)
            for buf in f:
                result.append(buf)

        self.assertEqual(len(bytes(result[0])), numSamples*2)
        self.assertEqual(len(rowLookup), len(result))
        for i, row in enumerate(result):
            self.assertEqual(bytes(row[0:2]), rowLookup[i])


mp3TestFilename = os.path.abspath(os.path.join('test', 'fixtures', 'sample.mp3'))
mp3RowLookup = [
    b'\x00\x00',
    b'\x00\x00',
    b'N\xff',
    b'\xe8/',
    b'.5',
    b'\x089',
    b'\x00\x00',
]

class TestAudioreadMp3(unittest.TestCase):

    def test_audio_open_as_generator(self):
        result = []
        with audioread.audio_open(mp3TestFilename, block_samples=numSamples) as f:
            print('Mp3 decode class', f.__class__)
            gen = f.read_data()
            try:
                while True:
                    data = next(gen)
                    result.append(data)
            except StopIteration:
                pass

        self.assertEqual(len(bytes(result[0])), numSamples*2)
        self.assertEqual(len(mp3RowLookup), len(result))
        for i, row in enumerate(result):
            self.assertEqual(bytes(row[0:2]), mp3RowLookup[i])


    def test_audio_open_as_forloop(self):
        result = []
        with audioread.audio_open(mp3TestFilename, block_samples=numSamples) as f:
            # self.assertEqual(f.nframes, 4)
            for buf in f:
                result.append(buf)

        self.assertEqual(len(bytes(result[0])), numSamples*2)
        self.assertEqual(len(mp3RowLookup), len(result))
        for i, row in enumerate(result):
            self.assertEqual(bytes(row[0:2]), mp3RowLookup[i])


if __name__ == '__main__':
    unittest.main()
