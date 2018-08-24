import os
import unittest
import audioread
maccaAvailable = audioread._ca_available()
print('maccaAvailable', maccaAvailable)
if maccaAvailable:
    from audioread import macca

PROJECT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
testFilename = os.path.abspath(os.path.join(PROJECT_DIR, 'test', 'fixtures', 'wavetest.wav'))

rowLookup = [
    b'\x00\x00',
    b'f2',
    b'\x008',
    b'3;',
]
numSamples = 512

@unittest.skipIf(not maccaAvailable, 'Not supported')
class TestMacca(unittest.TestCase):

    def test_macca_as_generator(self):
        result = []
        with macca.ExtAudioFile(testFilename, block_samples=numSamples) as f:
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
        with macca.ExtAudioFile(testFilename, block_samples=numSamples) as f:
            self.assertEqual(f.nframes, 2048)
            for buf in f:
                result.append(buf)

        self.assertEqual(len(bytes(result[0])), numSamples*2)
        self.assertEqual(len(rowLookup), len(result))
        for i, row in enumerate(result):
            self.assertEqual(bytes(row[0:2]), rowLookup[i])

    def test_seek(self):
        result = []
        with macca.ExtAudioFile(testFilename, block_samples=numSamples) as input_file:
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
