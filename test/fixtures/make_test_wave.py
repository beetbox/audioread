import numpy as np
import wave
import struct

def getData():
    size = 512

    a = np.full((size, ), 0., dtype=np.float16)
    b = np.full((size, ), 0.2, dtype=np.float16)
    c = np.full((size, ), 0.5, dtype=np.float16)
    d = np.full((size, ), 0.9, dtype=np.float16)
    return np.concatenate((a, b, c, d))


if __name__ == '__main__':
    fout = wave.open('test/fixtures/wavetest.wave', 'w')
    data = getData()
    fout.setnchannels(1)
    fout.setframerate(44100)
    fout.setsampwidth(2)
    fout.writeframes(data.tobytes())
    fout.close()
