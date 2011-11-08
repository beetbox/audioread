audioread
=========

Decode audio files using whichever library is available. The library currently
supports:

* [Gstreamer][] via [gst-python][].
* [Core Audio][] on Mac OS X via [ctypes][]. (PyObjC not required.)

[Gstreamer]: http://gstreamer.freedesktop.org/
[gst-python]: http://gstreamer.freedesktop.org/modules/gst-python.html
[Core Audio]: http://developer.apple.com/technologies/mac/audio-and-video.html
[ctypes]: http://docs.python.org/library/ctypes.html

Use the library like so:

    with audioread.audio_open(filename) as f:
        print f.channels, f.samplerate, f.duration
        for buf in f:
            do_something(buf)

Buffers in the file can be accessed by iterating over the object returned from
`audio_open`. Each buffer is a `buffer` or `str` object containing raw 16-bit
integer PCM data.

Additional values are available as fields on the audio file object:

* `channels` is the number of audio channels (an integer).
* `samplerate` is given in Hz (an integer).
* `duration` is the length of the audio in seconds (a float).
