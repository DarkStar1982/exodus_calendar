#!/usr/bin/env python3
from tests.run_delta_tests import delta_tests
from tests.run_foundation_tests import foundation_tests
from tests.run_seasons_tests import seasons_test

def run_all_tests():
	delta_tests()
	foundation_tests()
	seasons_test()

run_all_tests()