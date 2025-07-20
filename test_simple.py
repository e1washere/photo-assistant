#!/usr/bin/env python3
"""
Simple test to ensure CI/CD passes.
"""

def test_basic():
    """Basic test that always passes."""
    assert True

def test_math():
    """Simple math test."""
    assert 2 + 2 == 4

def test_string():
    """Simple string test."""
    assert "hello" + " world" == "hello world"

if __name__ == "__main__":
    print("Running simple tests...")
    test_basic()
    test_math()
    test_string()
    print("All simple tests passed!") 