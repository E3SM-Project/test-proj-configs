import pytest
from cacts.utils import expect, run_cmd, run_cmd_no_fail, expand_variables, evaluate_commands, str_to_bool, is_git_repo

def test_expect():
    with pytest.raises(RuntimeError):
        expect(False, "This is an error message")

def test_run_cmd():
    stat, output, errput = run_cmd("echo Hello, World!")
    assert stat == 0
    assert output == "Hello, World!"

def test_run_cmd_no_fail():
    output = run_cmd_no_fail("echo Hello, World!")
    assert output == "Hello, World!"

def test_expand_variables():
    class MockObject:
        def __init__(self):
            self.name = "MockObject"
            self.value = "${project.name}_value"

    mock_obj = MockObject()
    expand_variables(mock_obj, {'project': mock_obj})
    assert mock_obj.value == "MockObject_value"

def test_evaluate_commands():
    class MockObject:
        def __init__(self):
            self.command = "$(echo 'Hello, World!')"

    mock_obj = MockObject()
    evaluate_commands(mock_obj)
    assert mock_obj.command == "Hello, World!"

def test_str_to_bool():
    assert str_to_bool("True", "test_var") is True
    assert str_to_bool("False", "test_var") is False
    with pytest.raises(ValueError):
        str_to_bool("Invalid", "test_var")

def test_is_git_repo():
    assert is_git_repo() is True
