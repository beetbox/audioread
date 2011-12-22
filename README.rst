audioread
=========

Decode audio files using whichever backend is available. The library
currently supports:

- `Gstreamer`_ via `gst-python`_.
- `Core Audio`_ on Mac OS X via `ctypes`_. (PyObjC not required.)
- `MAD`_ via the `pymad`_ bindings.
- `FFmpeg`_ via its command-line interface.
- The standard library `wave`_ and `aifc`_ modules (for WAV and AIFF files).

.. _Gstreamer: http://gstreamer.freedesktop.org/
.. _gst-python: http://gstreamer.freedesktop.org/modules/gst-python.html
.. _Core Audio: http://developer.apple.com/technologies/mac/audio-and-video.html
.. _ctypes: http://docs.python.org/library/ctypes.html
.. _MAD: http://www.underbit.com/products/mad/
.. _pymad: http://spacepants.org/src/pymad/
.. _FFmpeg: http://ffmpeg.org/
.. _wave: http://docs.python.org/library/wave.html
.. _aifc: http://docs.python.org/library/aifc.html

Use the library like so::

    with audioread.audio_open(filename) as f:
        print f.channels, f.samplerate, f.duration
        for buf in f:
            do_something(buf)

Buffers in the file can be accessed by iterating over the object returned from
``audio_open``. Each buffer is a ``buffer`` or ``str`` object containing raw
**16-bit little-endian signed integer PCM data**. (Currently, these PCM format
parameters are not configurable, but this could be added to most of the
backends.)

Additional values are available as fields on the audio file object:

- ``channels`` is the number of audio channels (an integer).
- ``samplerate`` is given in Hz (an integer).
- ``duration`` is the length of the audio in seconds (a float).

The ``audio_open`` function transparently selects a backend that can read the
file. (Each backend is implemented in a module inside the ``audioread``
package.) If no backends succeed in opening the file, a ``DecodeError``
exception is raised. This exception is only used when the file type is
unsupported by the backends; if the file doesn't exist, a standard ``IOError``
will be raised.

Future Work
-----------

Possible additional backends:

-  PyOgg?
-  Other command-line tools?

Example
-------

The included ``decode.py`` script demonstrates using this package to
convert compressed audio files to WAV files.

Version History
---------------

0.3
  Fix a problem with the Gstreamer backend where audio files could be left open
  even after the ``GstAudioFile`` was "closed".

0.2
  Fix a hang in the GStreamer backend that occurs occasionally on some
  platforms.

0.1
  Initial release.

Et Cetera
---------

``audioread`` is by Adrian Sampson. It is made available under `the MIT
license`_. An alternative to this module is `decoder.py`_.

.. _the MIT license: http://www.opensource.org/licenses/mit-license.php
.. _decoder.py: http://www.brailleweb.com/cgi-bin/python.py
