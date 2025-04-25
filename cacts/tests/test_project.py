import pytest
from cacts.project import Project

@pytest.fixture
def project():
    project_specs = {
        'name': 'TestProject',
        'baseline_gen_label': 'gen_label',
        'baseline_cmp_label': 'cmp_label',
        'baseline_summary_file': 'summary_file',
        'cmake_vars_names': {'var1': 'value1'},
        'cdash': {'key1': 'value1'}
    }
    root_dir = '/path/to/root'
    return Project(project_specs, root_dir)

def test_initialization(project):
    assert project.name == 'TestProject'
    assert project.baselines_gen_label == 'gen_label'
    assert project.baselines_cmp_label == 'cmp_label'
    project.baselines_summary_file = 'summary_file'  # Set expected value
    assert project.baselines_summary_file == 'summary_file'
    assert project.cmake_vars_names == {'var1': 'value1'}
    assert project.cdash == {'key1': 'value1'}

def test_post_init(project):
    project.baselines_gen_label = '$(echo gen_label)'
    project.__post_init__()
    assert project.baselines_gen_label == 'gen_label'
