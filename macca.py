"""Read audio files using CoreAudio on Mac OS X."""
import os
import sys
import ctypes
import ctypes.util
import copy

def _load_framework(name):
    return ctypes.cdll.LoadLibrary(ctypes.util.find_library(name))
_coreaudio = _load_framework('AudioToolbox')
_corefoundation = _load_framework('CoreFoundation')

def cfstr_to_string(cfstr):
    getcstring = _corefoundation.CFStringGetCStringPtr
    getcstring.restype = ctypes.c_char_p
    getcstring.argtypes = [ctypes.c_void_p, ctypes.c_int]
    return getcstring(cfstr, 0)

def release(obj):
    release = _corefoundation.CFRelease
    release.argtypes = [ctypes.c_void_p]
    release(obj)

class MacError(Exception):
    pass
def check(err):
    if err != 0:
        raise MacError(err)

class CFObject(object):
    def __init__(self, obj):
        if obj == 0:
            raise ValueError('object is zero')
        self._obj = obj

    def __del__(self):
        if _corefoundation:
            release(self._obj)

class CFURL(CFObject):
    def __init__(self, filename):
        filename = os.path.abspath(os.path.expanduser(filename))
        createurl = _corefoundation.CFURLCreateFromFileSystemRepresentation
        createurl.restype = ctypes.c_void_p
        createurl.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                              ctypes.c_bool]
        url = createurl(
            0, filename, len(filename), False
        )
        super(CFURL, self).__init__(url)
    
    def __str__(self):
        urlstr = _corefoundation.CFURLGetString
        urlstr.argtypes = [ctypes.c_void_p]
        urlstr.restype = ctypes.c_void_p
        cfstr = urlstr(self._obj)
        out = cfstr_to_string(cfstr)
        # Resulting CFString does not need to be released according to docs.
        return out

class AudioStreamBasicDescription(ctypes.Structure):
    _fields_ = [
        ("mSampleRate",       ctypes.c_double),
        ("mFormatID",         ctypes.c_uint),
        ("mFormatFlags",      ctypes.c_uint),
        ("mBytesPerPacket",   ctypes.c_uint),
        ("mFramesPerPacket",  ctypes.c_uint),
        ("mBytesPerFrame",    ctypes.c_uint),
        ("mChannelsPerFrame", ctypes.c_uint),
        ("mBitsPerChannel",   ctypes.c_uint),
        ("mReserved",         ctypes.c_uint),
    ]

class AudioBuffer(ctypes.Structure):
    _fields_ = [
        ("mNumberChannels", ctypes.c_uint),
        ("mDataByteSize",   ctypes.c_uint),
        ("mData",           ctypes.c_void_p),
    ]

class AudioBufferList(ctypes.Structure):
    _fields_ = [
        ("mNumberBuffers",  ctypes.c_uint),
        ("mBuffers", AudioBuffer * 1),
    ]

def multi_char_literal(chars):
    num = 0
    for index, char in enumerate(chars):
        shift = (len(chars) - index - 1) * 8
        num |= ord(char) << shift
    return num

FILE_DATA_FORMAT = multi_char_literal('ffmt')
CLIENT_DATA_FORMAT = multi_char_literal('cfmt')
AUDIO_ID_PCM = multi_char_literal('lpcm')
PCM_IS_FLOAT = 1 << 0
PCM_IS_BIG_ENDIAN = 1 << 1
PCM_IS_SIGNED_INT = 1 << 2
PCM_IS_PACKED = 1 << 3

class AudioFile(object):
    def __init__(self, url):
        file_obj = ctypes.c_void_p()
        openurl = _coreaudio.ExtAudioFileOpenURL
        openurl.restype = ctypes.c_int
        openurl.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        check(openurl(url._obj, ctypes.byref(file_obj)))
        self._obj = file_obj

    def set_client_format(self, desc):
        assert desc.mFormatID == AUDIO_ID_PCM
        setprop = _coreaudio.ExtAudioFileSetProperty
        setprop.restype = ctypes.c_int
        setprop.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint,
                            ctypes.c_void_p]
        check(setprop(self._obj,
                      CLIENT_DATA_FORMAT,
                      ctypes.sizeof(desc),
                      ctypes.byref(desc)))

    def get_file_format(self):
        desc = AudioStreamBasicDescription()

        getprop = _coreaudio.ExtAudioFileGetProperty
        getprop.restype = ctypes.c_int
        getprop.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p,
                            ctypes.c_void_p]
        size = ctypes.c_int(ctypes.sizeof(desc))
        check(getprop(self._obj,
                      FILE_DATA_FORMAT,
                      ctypes.byref(size),
                      ctypes.byref(desc)))

        return desc

    def read_data(self, blocksize=4096):
        frames = ctypes.c_uint(blocksize // 4) # TODO client bytes per frame
        buf = ctypes.create_string_buffer(blocksize)

        buflist = AudioBufferList()
        buflist.mNumberBuffers = 1
        buflist.mBuffers[0].mNumberChannels = 2 # TODO
        buflist.mBuffers[0].mDataByteSize = blocksize
        buflist.mBuffers[0].mData = ctypes.cast(buf, ctypes.c_void_p)

        afread = _coreaudio.ExtAudioFileRead
        afread.restype = ctypes.c_int
        afread.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]

        while True:
            check(afread(self._obj,
                         ctypes.byref(frames),
                         ctypes.byref(buflist)))
            
            assert buflist.mNumberBuffers == 1
            size = buflist.mBuffers[0].mDataByteSize
            if not size:
                break

            data = ctypes.cast(buflist.mBuffers[0].mData,
                            ctypes.POINTER(ctypes.c_char))
            blob = data[:size]
            yield blob

    # TODO __del__

if __name__ == '__main__':
    url = CFURL(sys.argv[1])
    print url._obj
    print str(url)
    af = AudioFile(url)
    fmt = af.get_file_format()
    print fmt.mSampleRate, fmt.mChannelsPerFrame, fmt.mFormatFlags, \
          fmt.mFormatID, fmt.mBytesPerFrame, fmt.mBitsPerChannel

    newfmt = copy.copy(fmt)
    newfmt.mFormatID = AUDIO_ID_PCM
    newfmt.mFormatFlags = PCM_IS_BIG_ENDIAN | PCM_IS_SIGNED_INT | PCM_IS_PACKED
    newfmt.mBitsPerChannel = 16
    newfmt.mBytesPerPacket = (fmt.mChannelsPerFrame * newfmt.mBitsPerChannel // 8)
    newfmt.mFramesPerPacket = 1
    newfmt.mBytesPerFrame = newfmt.mBytesPerPacket
    print newfmt.mBytesPerFrame
    af.set_client_format(newfmt)

    for blob in af.read_data():
        print len(blob)
