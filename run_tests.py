import os

from unittest import TestLoader, TextTestRunner, TestSuite

loader = TestLoader()
this_dir = os.path.dirname(__file__)
tests = loader.discover(start_dir="tests/", pattern="*_test.py")
suite = TestSuite(tests)

runner = TextTestRunner(verbosity=2)
runner.run(suite)
