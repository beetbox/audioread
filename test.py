import unittest
import sys

if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests = loader.discover('test')
    testRunner = unittest.runner.TextTestRunner()
    result = testRunner.run(tests)
    if not result.wasSuccessful():
        sys.exit(1)