#!/usr/bin/env python3
"""
Test runner for the Texas Hold'em game.
Run this script to execute all tests.
"""

import unittest
import sys


def run_tests():
    """Run all tests for the Texas Hold'em game."""
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(".", pattern="test_*.py")

    # Create a test runner
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
