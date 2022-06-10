
from unittest import TestLoader, TextTestRunner, TestSuite
from tests.unit_test import *

test_cases = [TestUser]

loader = TestLoader()

for test_class in test_cases:
    tests = loader.loadTestsFromTestCase(test_class)

suite = TestSuite(tests)

runner = TextTestRunner(verbosity=2)
runner.run(suite)
