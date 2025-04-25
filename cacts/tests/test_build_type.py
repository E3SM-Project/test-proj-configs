import pytest
from cacts.build_type import BuildType
from cacts.utils import expand_variables, evaluate_commands, str_to_bool

class MockProject:
    def __init__(self):
        self.name = "MockProject"

class MockMachine:
    def __init__(self):
        self.env_setup = ["echo 'Setting up environment'"]

@pytest.fixture
def build_type():
    project = MockProject()
    machine = MockMachine()
    builds_specs = {
        'default': {
            'longname': 'default_longname',
            'description': 'default_description',
            'uses_baselines': 'True',
            'on_by_default': 'True',
            'cmake_args': {'arg1': 'value1'}
        },
        'test_build': {
            'longname': 'test_longname',
            'description': 'test_description',
            'uses_baselines': 'False',
            'on_by_default': 'False',
            'cmake_args': {'arg2': 'value2'}
        }
    }
    return BuildType('test_build', project, machine, builds_specs)

def test_initialization(build_type):
    assert build_type.name == 'test_build'
    assert build_type.longname == 'test_longname'
    assert build_type.description == 'test_description'
    assert build_type.uses_baselines is False
    assert build_type.on_by_default is False
    assert build_type.cmake_args == {'arg1': 'value1', 'arg2': 'value2'}

def test_expand_variables(build_type):
    build_type.longname = "${project.name}_longname"
    expand_variables(build_type, {'project': build_type.project, 'machine': build_type.machine, 'build': build_type})
    assert build_type.longname == "MockProject_longname"

def test_evaluate_commands(build_type):
    build_type.description = "$(echo 'test_description')"
    evaluate_commands(build_type, "echo 'Setting up environment'")
    assert build_type.description == "test_description"

def test_str_to_bool():
    assert str_to_bool("True", "test_var") is True
    assert str_to_bool("False", "test_var") is False
    with pytest.raises(ValueError):
        str_to_bool("Invalid", "test_var")
