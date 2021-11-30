# This file is part of audioread.
# Copyright 2018, Sam Thursfield
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


import json
import os

import pytest


@pytest.fixture()
def audiofile(request):
    """Fixture that provides an AudiofileSpec instance."""
    spec_path = os.path.join(DATADIR, request.param + '.json')
    with open(spec_path) as f:
        spec = json.load(f)
    result = AudiofileSpec(**spec)
    return result


# The audiofiles used for testing live in the data/ directory. They are defined
# by .json files and each one must be listed here by name.
TEST_AUDIOFILES = ['test-1', 'test-2']

DATADIR = os.path.join(os.path.dirname(__file__), 'data')


class AudiofileSpec():
    """Defines the expected attributes for a test audiofile."""
    def __init__(self, filename, duration, channels, samplerate):
        self.path = os.path.join(DATADIR, filename)
        self.duration = duration
        self.channels = channels
        self.samplerate = samplerate


def pytest_generate_tests(metafunc):
    """Parametrize the audiofile() fixture using TEST_AUDIOFILES."""
    if 'audiofile' in metafunc.fixturenames:
        metafunc.parametrize("audiofile", TEST_AUDIOFILES, indirect=True)
