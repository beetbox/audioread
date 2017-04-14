# This file is part of audioread.
# Copyright 2013, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

import os
from distutils.core import setup
import imp

version = imp.load_source('audioread.version', 'audioread/version.py')


def _read(fn):
    path = os.path.join(os.path.dirname(__file__), fn)
    return open(path).read()


setup(name='audioread',
      version=version.version,
      description='multi-library, cross-platform audio decoding',
      author='Adrian Sampson',
      author_email='adrian@radbox.org',
      url='https://github.com/sampsyo/audioread',
      license='MIT',
      platforms='ALL',
      long_description=_read('README.rst'),

      packages=['audioread'],

      classifiers=[
          'Topic :: Multimedia :: Sound/Audio :: Conversion',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
)
