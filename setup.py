# This file is part of audioread.
# Copyright 2011, Adrian Sampson.
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

def _read(fn):
    path = os.path.join(os.path.dirname(__file__), fn)
    return open(path).read()

setup(name='audioread',
      version='0.7',
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
      ],
)
