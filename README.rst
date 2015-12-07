audioread
=========

.. image:: https://secure.travis-ci.org/sampsyo/audioread.png
        :target: https://travis-ci.org/sampsyo/audioread/

Decode audio files using whichever backend is available. The library
currently supports:

- `Gstreamer`_ via `PyGObject`_.
- `Core Audio`_ on Mac OS X via `ctypes`_. (PyObjC not required.)
- `MAD`_ via the `pymad`_ bindings.
- `FFmpeg`_ or `Libav`_ via its command-line interface.
- The standard library `wave`_, `aifc`_, and `sunau`_ modules (for
  uncompressed audio formats).

.. _Gstreamer: http://gstreamer.freedesktop.org/
.. _gst-python: http://gstreamer.freedesktop.org/modules/gst-python.html
.. _Core Audio: http://developer.apple.com/technologies/mac/audio-and-video.html
.. _ctypes: http://docs.python.org/library/ctypes.html
.. _MAD: http://www.underbit.com/products/mad/
.. _pymad: http://spacepants.org/src/pymad/
.. _FFmpeg: http://ffmpeg.org/
.. _Libav: https://www.libav.org/
.. _wave: http://docs.python.org/library/wave.html
.. _aifc: http://docs.python.org/library/aifc.html
.. _aifc: http://docs.python.org/library/sunau.html
.. _PyGObject: https://wiki.gnome.org/Projects/PyGObject

Use the library like so::

    with audioread.audio_open(filename) as f:
        print(f.channels, f.samplerate, f.duration)
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

Audioread is "universal" and supports both Python 2 (2.6+) and Python 3
(3.2+).

Example
-------

The included ``decode.py`` script demonstrates using this package to
convert compressed audio files to WAV files.

Version History
---------------

2.1.0
  The FFmpeg backend can now also use Libav's ``avconv`` command.

2.0.0
  The GStreamer backend now uses GStreamer 1.x via the new
  gobject-introspection API (and is compatible with Python 3).

1.2.2
  When running FFmpeg on Windows, disable its crash dialog. Thanks to
  jcsaaddupuy.

1.2.1
  Fix an unhandled exception when opening non-raw audio files (thanks to
  aostanin).
  Fix Python 3 compatibility for the raw-file backend.

1.2.0
  Add support for FFmpeg on Windows (thanks to Jean-Christophe Saad-Dupuy).

1.1.0
  Add support for Sun/NeXT `Au files`_ via the standard-library ``sunau``
  module (thanks to Dan Ellis).

1.0.3
  Use the rawread (standard-library) backend for .wav files.

1.0.2
  Send SIGKILL, not SIGTERM, to ffmpeg processes to avoid occasional hangs.

1.0.1
  When GStreamer fails to report a duration, raise an exception instead of
  silently setting the duration field to None.

1.0.0
  Catch GStreamer's exception when necessary components, such as
  ``uridecodebin``, are missing.
  The GStreamer backend now accepts relative paths.
  Fix a hang in GStreamer when the stream finishes before it begins (when
  reading broken files).
  Initial support for Python 3.

0.8
  All decoding errors are now subclasses of ``DecodeError``.

0.7
  Fix opening WAV and AIFF files via Unicode filenames.

0.6
  Make FFmpeg timeout more robust.
  Dump FFmpeg output on timeout.
  Fix a nondeterministic hang in the Gstreamer backend.
  Fix a file descriptor leak in the MAD backend.

0.5
  Fix crash when FFmpeg fails to report a duration.
  Fix a hang when FFmpeg fills up its stderr output buffer.
  Add a timeout to ``ffmpeg`` tool execution (currently 10 seconds for each
  4096-byte read); a ``ReadTimeoutError`` exception is raised if the tool times
  out.

0.4
  Fix channel count detection for FFmpeg backend.

0.3
  Fix a problem with the Gstreamer backend where audio files could be left open
  even after the ``GstAudioFile`` was "closed".

0.2
  Fix a hang in the GStreamer backend that occurs occasionally on some
  platforms.

0.1
  Initial release.

.. _Au files: http://en.wikipedia.org/wiki/Au_file_format

Et Cetera
---------

``audioread`` is by Adrian Sampson. It is made available under `the MIT
license`_. An alternative to this module is `decoder.py`_.

.. _the MIT license: http://www.opensource.org/licenses/mit-license.php
.. _decoder.py: http://www.brailleweb.com/cgi-bin/python.py
