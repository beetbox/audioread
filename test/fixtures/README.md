Audio file fixtures for the tests.

#### test.wav
Test.wav was produced by doing:

```py
import numpy as np
from scipy.io import wavfile

if __name__ == '__main__':
    size = 512
    a = np.full((size, ), 0.)
    b = np.full((size, ), 0.2)
    c = np.full((size, ), 0.5)
    d = np.full((size, ), 0.9)
    t = np.concatenate((a, b, c, d))

    wavfile.write('test.wav', 44100, t)
```

#### wavetest.wav

Produced with `make_test_wave.py`
