import pytest
from app import greet

def test_greet_normal():
    assert greet('Alice', 2) == 'Hello, Alice!Hello, Alice!'

def test_greet_zero():
    assert greet('Bob', 0) == 'Hello, Bob!'

def test_greet_negative():
    # Negative intensity should raise ValueError or behave as per implementation
    with pytest.raises(ValueError):
        greet('Eve', -1) 