import pytest
from cacts.machine import Machine

class MockProject:
    def __init__(self):
        self.name = "MockProject"

@pytest.fixture
def machine():
    project = MockProject()
    machines_specs = {
        'default': {
            'num_bld_res': 4,
            'num_run_res': 8,
            'env_setup': ['echo "Setting up environment"']
        },
        'test_machine': {
            'num_bld_res': 2,
            'num_run_res': 4,
            'env_setup': ['echo "Setting up test environment"']
        }
    }
    return Machine('test_machine', project, machines_specs)

def test_initialization(machine):
    assert machine.name == 'test_machine'
    assert machine.num_bld_res == 2
    assert machine.num_run_res == 4
    assert machine.env_setup == ['echo "Setting up test environment"']

def test_uses_gpu(machine):
    assert machine.uses_gpu() is False
    machine.gpu_arch = 'test_gpu_arch'
    assert machine.uses_gpu() is True
