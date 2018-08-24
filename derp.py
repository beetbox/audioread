import mad
import os
tf = os.path.abspath(os.path.join('test', 'fixtures', 'wavetest.wav'))

fp = open(tf, 'rb')
mf = mad.MadFile(fp)

print('mf.total_time', mf.total_time())
print(mf.read())
