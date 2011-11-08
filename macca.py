"""Read audio files using CoreAudio on Mac OS X."""
import os
import sys
import ctypes
import ctypes.util
import copy


# CoreFoundation and CoreAudio libraries along with their function
# prototypes.

def _load_framework(name):
    return ctypes.cdll.LoadLibrary(ctypes.util.find_library(name))
_coreaudio = _load_framework('AudioToolbox')
_corefoundation = _load_framework('CoreFoundation')

# Convert CFStrings to C strings. 
_corefoundation.CFStringGetCStringPtr.restype = ctypes.c_char_p
_corefoundation.CFStringGetCStringPtr.argtypes = [ctypes.c_void_p, ctypes.c_int]

# Free memory.
_corefoundation.CFRelease.argtypes = [ctypes.c_void_p]

# Create a file:// URL.
_corefoundation.CFURLCreateFromFileSystemRepresentation.restype = \
    ctypes.c_void_p
_corefoundation.CFURLCreateFromFileSystemRepresentation.argtypes = \
    [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_bool]

# Get a string representation of a URL.
_corefoundation.CFURLGetString.restype = ctypes.c_void_p
_corefoundation.CFURLGetString.argtypes = [ctypes.c_void_p]

# Open an audio file for reading.
_coreaudio.ExtAudioFileOpenURL.restype = ctypes.c_int
_coreaudio.ExtAudioFileOpenURL.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

# Set audio file property.
_coreaudio.ExtAudioFileSetProperty.restype = ctypes.c_int
_coreaudio.ExtAudioFileSetProperty.argtypes = \
    [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p]

# Get audio file property.
_coreaudio.ExtAudioFileGetProperty.restype = ctypes.c_int
_coreaudio.ExtAudioFileGetProperty.argtypes = \
    [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p]

# Read from an audio file.
_coreaudio.ExtAudioFileRead.restype = ctypes.c_int
_coreaudio.ExtAudioFileRead.argtypes = \
    [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]

# Close/free an audio file.
_coreaudio.ExtAudioFileDispose.restype = ctypes.c_int
_coreaudio.ExtAudioFileDispose.argtypes = [ctypes.c_void_p]


# Check for errors in functions that return error codes.

class MacError(Exception):
    pass

def check(err):
    """If err is nonzero, raise a MacError exception."""
    if err != 0:
        raise MacError(err)


# CoreFoundation objects.

class CFObject(object):
    def __init__(self, obj):
        if obj == 0:
            raise ValueError('object is zero')
        self._obj = obj

    def __del__(self):
        if _corefoundation:
            _corefoundation.CFRelease(self._obj)

class CFURL(CFObject):
    def __init__(self, filename):
        filename = os.path.abspath(os.path.expanduser(filename))
        url = _corefoundation.CFURLCreateFromFileSystemRepresentation(
            0, filename, len(filename), False
        )
        super(CFURL, self).__init__(url)
    
    def __str__(self):
        cfstr = _corefoundation.CFURLGetString(self._obj)
        out = _corefoundation.CFStringGetCStringPtr(cfstr, 0)
        # Resulting CFString does not need to be released according to docs.
        return out


# Constants used in CoreAudio.

def multi_char_literal(chars):
    """Emulates character integer literals in C. Given a string "abc",
    returns the value of the C single-quoted literal 'abc'.
    """
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


# Structs used in CoreAudio.

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


# Main functionality.

class AudioFile(object):
    def __init__(self, filename):
        url = CFURL(filename)
        self._obj = self._open_url(url)
        del url

        self.closed = False
        self._file_fmt = None
        self._client_fmt = None

        self.setup()

    @classmethod
    def _open_url(cls, url):
        """Given a CFURL Python object, return an opened ExtAudioFileRef.
        """
        file_obj = ctypes.c_void_p()
        check(_coreaudio.ExtAudioFileOpenURL(
            url._obj, ctypes.byref(file_obj)
        ))
        return file_obj

    def set_client_format(self, desc):
        """Get the client format description. This describes the
        encoding of the data that the program will read from this
        object.
        """
        assert desc.mFormatID == AUDIO_ID_PCM
        check(_coreaudio.ExtAudioFileSetProperty(
            self._obj, CLIENT_DATA_FORMAT, ctypes.sizeof(desc),
            ctypes.byref(desc)
        ))
        self._client_fmt = desc

    def get_file_format(self):
        """Get the file format description. This describes the type of
        data stored on disk.
        """
        # Have cached file format?
        if self._file_fmt is not None:
            return self._file_fmt

        # Make the call to retrieve it.
        desc = AudioStreamBasicDescription()
        size = ctypes.c_int(ctypes.sizeof(desc))
        check(_coreaudio.ExtAudioFileGetProperty(
            self._obj, FILE_DATA_FORMAT, ctypes.byref(size), ctypes.byref(desc)
        ))

        # Cache result.
        self._file_fmt = desc
        return desc

    def setup(self, bitdepth=16):
        """Set the client format parameters, specifying the desired PCM
        audio data format to be read from the file. Must be called
        before reading from the file.
        """
        fmt = self.get_file_format()
        newfmt = copy.copy(fmt)

        newfmt.mFormatID = AUDIO_ID_PCM
        newfmt.mFormatFlags = \
            PCM_IS_BIG_ENDIAN | PCM_IS_SIGNED_INT | PCM_IS_PACKED
        newfmt.mBitsPerChannel = bitdepth
        newfmt.mBytesPerPacket = \
            (fmt.mChannelsPerFrame * newfmt.mBitsPerChannel // 8)
        newfmt.mFramesPerPacket = 1
        newfmt.mBytesPerFrame = newfmt.mBytesPerPacket
        self.set_client_format(newfmt)

    def read_data(self, blocksize=4096):
        """Generates byte strings reflecting the audio data in the file.
        """
        frames = ctypes.c_uint(blocksize // self._client_fmt.mBytesPerFrame)
        buf = ctypes.create_string_buffer(blocksize)

        buflist = AudioBufferList()
        buflist.mNumberBuffers = 1
        buflist.mBuffers[0].mNumberChannels = self._client_fmt.mChannelsPerFrame
        buflist.mBuffers[0].mDataByteSize = blocksize
        buflist.mBuffers[0].mData = ctypes.cast(buf, ctypes.c_void_p)

        while True:
            check(_coreaudio.ExtAudioFileRead(
                self._obj, ctypes.byref(frames), ctypes.byref(buflist)
            ))
            
            assert buflist.mNumberBuffers == 1
            size = buflist.mBuffers[0].mDataByteSize
            if not size:
                break

            data = ctypes.cast(buflist.mBuffers[0].mData,
                            ctypes.POINTER(ctypes.c_char))
            blob = data[:size]
            yield blob

    def close(self):
        """Close the audio file and free associated memory."""
        if not self.closed:
            check(_coreaudio.ExtAudioFileDispose(self._obj))
            self.closed = True

    def __del__(self):
        if _coreaudio:
            self.close()


# Smoke test.

if __name__ == '__main__':
    af = AudioFile(sys.argv[1])
    for blob in af.read_data():
        print len(blob),
    af.close()
