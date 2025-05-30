import pathlib
import yaml

from .project    import Project
from .machine    import Machine
from .build_type import BuildType
from .utils      import expect, check_minimum_python_version

check_minimum_python_version(3, 4)

###############################################################################
def parse_project(config_file,root_dir):
###############################################################################
    content = yaml.load(open(config_file,"r"),Loader=yaml.SafeLoader)

    expect ('project' in content.keys(),
            "Missing 'project' section in configuration file\n"
            f" - config file: {config_file}\n"
            f" - sections found: {','.join(content.keys())}\n")

    # Build Project
    return Project(content['project'],root_dir)

###############################################################################
def parse_machine(config_file,project,machine_name):
###############################################################################
    content = yaml.load(open(config_file,"r"),Loader=yaml.SafeLoader)

    expect ('machines' in content.keys(),
            "Missing 'machines' section in configuration file\n"
            f" - config file: {config_file}\n"
            f" - sections found: {','.join(content.keys())}\n")

    # Special handling of 'local' machine
    machs = content['machines']
    if machine_name=="local":
        local_yaml = pathlib.Path("~/.cime/cacts.yaml").expanduser()
        local_content = yaml.load(open(local_yaml,'r'),Loader=yaml.SafeLoader)
        machs.update(local_content['machines'])
        machine_name = 'local'

    # Build Machine
    return Machine(machine_name,project,machs)

###############################################################################
def parse_builds(config_file,project,machine,generate,build_types=None):
###############################################################################
    content = yaml.load(open(config_file,"r"),Loader=yaml.SafeLoader)

    expect ('configurations' in content.keys(),
            "Missing 'configurations' section in configuration file\n"
            f" - config file: {config_file}\n"
            f" - sections found: {','.join(content.keys())}\n")

    # Get builds
    builds = []
    if build_types:
        for name in build_types:
            build = BuildType(name,project,machine,content['configurations'])
            # Skip non-baselines builds when generating baselines
            if not generate or build.uses_baselines:
                builds.append(build)
    else:
        # Add all build types that are on by default
        for name in configs.keys():
            if name=='default':
                continue
            build = BuildType(name,project,machine,content['configurations'])

            # Skip non-baselines builds when generating baselines
            if (not generate or build.uses_baselines) and build.on_by_default:
                builds.append(build)

    return builds
