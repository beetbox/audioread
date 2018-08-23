import numpy as np
import wave
import struct

def getData():
    # size = 512 / 8
    size = 512
    # a = np.full((size, ), 0.)
    # b = np.full((size, ), 200.)
    # c = np.full((size, ), 500.)
    # d = np.full((size, ), 900.)

    a = np.full((size, ), 0., dtype=np.float16)
    b = np.full((size, ), 0.2, dtype=np.float16)
    c = np.full((size, ), 0.5, dtype=np.float16)
    d = np.full((size, ), 0.9, dtype=np.float16)
    t = np.concatenate((a, b, c, d))
    return t

def getItemBytes(x):
    # return x.tobytes()
    ba = bytearray(struct.pack("f", x))  
    return ba


if __name__ == '__main__':
    fout = wave.open('test/fixtures/wavetest2.wave', 'w')
    data = getData()
    fout.setnchannels(1)
    fout.setframerate(44100)
    fout.setsampwidth(2)
    
    fout.writeframes(data.tobytes())

    # data = np.filter()
    # v = np.vectorize(getItemBytes)
    # out = v(data)
    # fout.writeframes(out)

    fout.close()
