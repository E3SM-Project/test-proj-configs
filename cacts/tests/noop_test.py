# define a simple test so that pytest can run

import pytest


def test_noop():
    print("noop!")
    assert True
