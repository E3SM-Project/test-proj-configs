import re

from tpc_utils import expect, expand_variables

###############################################################################
class BuildType(object):
###############################################################################
    """
    Class of predefined build types for the project.
    The script 'test-proj-build' will query this object for runtime info on the build
    """

    def __init__(self, shortname, project, machine, builds_specs):
        # Check inputs
        expect (isinstance(builds_specs,dict),
                f"BuildType constructor expects a dict object for 'builds_specs' (got {type(builds_specs)} instead).\n")
        expect (shortname in builds_specs.keys(),
                f"BuildType '{shortname}' not found in the 'build_types' section of the config file.\n"
                f" - available build types: {','.join(b for b in builds_specs.keys() if b!="default")}\n")

        # Get props for this build type and for a default build
        props   = builds_specs[shortname]
        default = builds_specs.get('default',{})

        # Set build props
        self.shortname   = shortname
        self.longname    = props.get('longname',shortname)
        self.description = props.get('description',None)
        self.uses_baselines = props.get('uses_baselines',None) or default.get('uses_baselines',True)
        self.on_by_default  = props.get('on_by_default',None) or default.get('on_by_default',True)
        expect (isinstance(self.uses_baselines,bool),
                "Invalid value for uses_baselines.\n"
                f"  - build name: {shortname}\n"
                f"  - input value: {self.uses_baselines}\n"
                f"  - input type: {type(self.uses_baselines)}\n"
                 "  - expected type: bool\n")
        expect (isinstance(self.on_by_default,bool),
                "Invalid value for on_by_default.\n"
                f"  - build name: {shortname}\n"
                f"  - input value: {self.on_by_default}\n"
                f"  - input type: {type(self.on_by_default)}\n"
                 "  - expected type: bool\n")

        expect (isinstance(props.get('cmake_args',{}),dict),
                f"Invalid value for cmake_args for build type '{shortname}'.\n"
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

        # Properties set at runtime by the TestProjBuild
        self.compile_res_count = None
        self.testing_res_count = None
        self.baselines_missing = False
