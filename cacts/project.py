from .utils import expect, evaluate_commands

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
        self.root_dir = root_dir

        # If left to None, ALL tests are run during baselines generation
        self.baselines_gen_label = project_specs.get('baseline_gen_label',None)

        # If set, when -b <dir> is NOT used (signaling NO baselines tests),
        # tests with this label are NOT run. Defaults to baselines_gen_label
        self.baselines_cmp_label = project_specs.get('baseline_cmp_label',self.baselines_gen_label)

        # Projects can dump in this file (relative to cmake build dir) the list of
        # baselines files that need to be copied to the baseline dir. This allows
        # CACTS to ensure that ALL baselines tests complete sucessfully before copying
        # any file to the baselines directory
        self.baselines_summary_file = project_specs.get('baselines_summary_file',None)

        # Allow to use a project cmake var that can turn on/off baseline-related code/tests.
        # Can help to limit build time
        # NOTE: projects may have an option to ENABLE such code or an optio to DISABLE it.
        # Hence, we ooffer both alternatives
        self.cmake_vars_names = project_specs.get('cmake_vars_names',{})

        self.cdash = project_specs.get('cdash',{})

        # Evaluate remaining bash commands of the form $(...)
        evaluate_commands(self)
