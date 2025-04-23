import re

from .utils import expect, expand_variables, evaluate_commands, str_to_bool

###############################################################################
class BuildType(object):
###############################################################################
    """
    Class of predefined build types for the project.
    The script 'test-proj-build' will query this object for runtime info on the build
    """

    def __init__(self, name, project, machine, builds_specs):
        # Check inputs
        expect (isinstance(builds_specs,dict),
                f"BuildType constructor expects a dict object for 'builds_specs' (got {type(builds_specs)} instead).\n")
        expect (name in builds_specs.keys(),
                f"BuildType '{name}' not found in the 'build_types' section of the config file.\n"
                f" - available build types: {','.join(b for b in builds_specs.keys() if b!='default')}\n")

        # Get props for this build type and for a default build
        props   = builds_specs[name]
        default = builds_specs.get('default',{})

        # Set build props
        self.name   = name
        self.longname    = props.get('longname',name)
        self.description = props.get('description',None)
        self.uses_baselines = props.get('uses_baselines',None)
        self.on_by_default  = props.get('on_by_default',None)
        if  self.uses_baselines is None:
            self.uses_baselines = default.get('uses_baselines',True)
        if  self.on_by_default is None:
            self.on_by_default  = default.get('on_by_default',True)

        expect (isinstance(props.get('cmake_args',{}),dict),
                f"Invalid value for cmake_args for build type '{name}'.\n"
                f"  - input value: {props['cmake_args']}\n"
                f"  - input type: {type(props['cmake_args'])}\n"
                 "  - expected type: dict\n")
        expect (isinstance(default.get('cmake_args',{}),dict),
                f"Invalid value for cmake_args for build type 'default'.\n"
                f"  - input value: {default['cmake_args']}\n"
                f"  - input type: {type(default['cmake_args'])}\n"
                 "  - expected type: dict\n")
        self.cmake_args = default.get('cmake_args',{})
        self.cmake_args.update(props.get('cmake_args',{}))

        # Perform substitution of ${..} strings
        objects = {
            'project' : project,
            'machine' : machine,
            'build'   : self
        }
        expand_variables(self,objects)

        # Evaluate remaining bash commands of the form $(...)
        evaluate_commands(self)

        # After vars expansion, these two must be convertible to bool
        if type(self.uses_baselines) is str:
            self.uses_baselines = str_to_bool(self.uses_baselines,f"{name}.uses_baselines")
        if type(self.on_by_default) is str:
            self.on_by_default  = str_to_bool(self.on_by_default,f"{name}.on_by_default")

        # Properties set at runtime by the TestProjBuild
        self.compile_res_count = None
        self.testing_res_count = None
        self.baselines_missing = False
