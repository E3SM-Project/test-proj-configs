from .utils import expect

###############################################################################
class Project(object):
###############################################################################
    """
    Parent class for objects describing a project
    """

    def __init__ (self,project_specs,root_dir):
        expect (isinstance(project_specs,dict),
                f"Project constructor expects a dict object (got {type(project_specs)} instead).\n")

        expect ('name' in project_specs.keys(),
                "Missing required field 'name' in 'project' section.\n")
        self.name = project_specs['name']

        # If left to None, ALL tests are run during baselines generation
        self.baselines_gen_label = project_specs.get('baseline_gen_label',None)

        # Projects can dump in this file (relative to cmake build dir) the list of
        # baselines files that need to be copied to the baseline dir. This allows
        # TPC to ensure that ALL baselines tests complete sucessfully before copying
        # any file to the baselines directory
        self.baselines_summary_file = project_specs.get('baselines_summary_file',None)

        # If the proj has a cmake var that can turn on/off baselines tests, we can use it
        self.enable_baselines_cmake_option = project_specs.get('enable_baselines_cmake_option',None)

        self.root_dir = root_dir
