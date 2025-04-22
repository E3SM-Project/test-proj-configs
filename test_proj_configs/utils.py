"""
Utilities
"""

import os
import sys
import re
import subprocess
import psutil
import site
import argparse
import importlib
import importlib.util

###############################################################################
def expect(condition, error_msg, exc_type=Exception, error_prefix="ERROR:"):
###############################################################################
    """
    Similar to assert except doesn't generate an ugly stacktrace. Useful for
    checking user error, not programming error.

    >>> expect(True, "error1")
    >>> expect(False, "error2")
    Traceback (most recent call last):
        ...
    SystemExit: ERROR: error2
    """
    if not condition:
        msg = error_prefix + " " + error_msg
        raise exc_type(msg)

###############################################################################
def run_cmd(cmd, from_dir=None, verbose=None, dry_run=False, env_setup=None,
            output_file=None,error_file=None,
            output_to_screen=False,error_to_screen=False,
            combine_output=False):
###############################################################################
    """
    Wrapper around subprocess to make it much more convenient to run shell commands

    >>> run_cmd('ls file_i_hope_doesnt_exist')[0] != 0
    True
    """

    expect (not (combine_output and (error_file or error_to_screen)),
            "Makes no sense to request combined output, and then provide a special handle for stderr.\n")

    # If the cmd needs some env setup, the user can pass the setup string, which will be
    # executed right before the cmd
    if env_setup:
        cmd = f"{env_setup} && {cmd}"

    # When outputing to screen, it is much easier to listen to only one between
    # stdout and stderr, so we force combine_output to be True
    if output_to_screen:
        combine_output=True

    arg_stdout = subprocess.PIPE
    if combine_output:
        arg_stderr = subprocess.STDOUT
    else:
        arg_stderr = subprocess.PIPE

    from_dir = str(from_dir) if from_dir else from_dir

    if verbose:
        print(f"RUN: {cmd}\nFROM: {os.getcwd() if from_dir is None else from_dir}")

    if dry_run:
        return 0, "", ""

    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=arg_stdout,
                            stderr=arg_stderr,
                            stdin=None,
                            text=True, # automatically decode output bytes to string
                            cwd=from_dir)

    output = ""
    errput = ""

    if output_to_screen:
        # We are forcing combined outpu, so just parse stdout
        for line in iter(proc.stdout.readline,''):
            output += line
            print(line,end='')

        proc.wait()
    else:
        # Parse stdout and stderr separately
        output, errput = proc.communicate()

        if output:
            output = output.strip()

        if errput:
            errput = errput.strip()

    # If we need to write to file, do so
    if output_file:
        with open(output_file,'w') as fd:
            fd.write(output)
    if not combine_output and error_file:
        with open(error_file,'w') as fd:
            fd.write(error)

    return proc.returncode, output, errput

###############################################################################
def run_cmd_no_fail(cmd, from_dir=None, verbose=None, dry_run=False, env_setup=None,
                    output_file=None,error_file=None,
                    output_to_screen=False,error_to_screen=False,
                    combine_output=False):
###############################################################################
    """
    Wrapper around subprocess to make it much more convenient to run shell commands.
    Expects command to work. Just returns output string.
    """
    stat, output, errput = run_cmd(cmd, from_dir=from_dir,verbose=verbose,dry_run=dry_run,env_setup=env_setup,
                                   output_file=output_file,error_file=error_file,
                                   output_to_screen=output_to_screen,error_to_screen=error_to_screen,
                                   combine_output=combine_output)
    expect (stat==0,
            "Command failed unexpectedly"
            f"  - command: {cmd}"
            f"  - error: {errput if errput else output}"
            f"  - from dir: {from_dir or os.getcwd()}")

    return output

###############################################################################
def check_minimum_python_version(major, minor):
###############################################################################
    """
    Check your python version.

    >>> check_minimum_python_version(sys.version_info[0], sys.version_info[1])
    >>>
    """
    msg = "Python " + str(major) + ", minor version " + str(minor) + " is required, you have " + str(sys.version_info[0]) + "." + str(sys.version_info[1])
    expect(sys.version_info[0] > major or
           (sys.version_info[0] == major and sys.version_info[1] >= minor), msg)


###############################################################################
def ensure_pip():
###############################################################################
    """
    Ensures that pip is available. Notice that we cannot use the _ensure_pylib_impl
    function below, since it would cause circular dependencies. This one has to
    be done by hand.
    """
    try:
        import pip # pylint: disable=unused-import

    except ModuleNotFoundError:
        # Use ensurepip for installing pip
        import ensurepip
        ensurepip.bootstrap(user=True)

        # needed to "rehash" available libs
        site.main() # pylint: disable=no-member

        import pip # pylint: disable=unused-import

###############################################################################
def pip_install_lib(pip_libname):
###############################################################################
    """
    Ask pip to install a version of a package which is >= min_version
    """
    # Installs will use pip, so we need to ensure it is available
    ensure_pip()

    # Note: --trusted-host may not work for ancient versions of python
    #       --upgrade makes sure we get the latest version, even if one is already installed
    stat, _, err = run_cmd("{} -m pip install --upgrade {} --trusted-host files.pythonhosted.org --user".format(sys.executable, pip_libname))
    expect(stat == 0, "Failed to install {}, cannot continue:\n{}".format(pip_libname, err))

    # needed to "rehash" available libs
    site.main() # pylint: disable=no-member

###############################################################################
def package_version_ok(pkg, min_version=None):
###############################################################################
    """
    Checks that the loaded package's version is >= that the minimum required one.
    If no minimum version is passed, then return True
    """
    if min_version is not None:
        try:
            from pkg_resources import parse_version

            return parse_version(pkg.__version__) >= parse_version(min_version)
        except ImportError:
            # Newer versions of python cannot use pkg_resources
            ensure_packaging()
            from packaging.version import parse

            return parse(pkg.__version__) >= parse(min_version)

    else:
        return True

###############################################################################
def _ensure_pylib_impl(libname, min_version=None, pip_libname=None):
###############################################################################
    """
    Internal method, clients should not call this directly; please use of the
    public ensure_XXX methods. If one does not exist, we will need to evaluate
    if we want to add a new outside dependency.
    """

    install = False
    try:
        pkg = importlib.import_module(libname)

        if not package_version_ok(pkg,min_version):
            print("Detected version for package {} is too old: detected {}, required >= {}. Will attempt to upgrade the package locally".format(libname, pkg.__version__,min_version))
            install = True

    except ImportError:
        print("Detected missing package {}. Will attempt to install locally".format(libname))
        pip_libname = pip_libname if pip_libname else libname

        install = True

    if install:
        pip_install_lib(pip_libname)
        pkg = importlib.import_module(libname)

    expect(package_version_ok(pkg,min_version),
           "Error! Could not find version {} for package {}.".format(min_version,libname))

# We've accepted these outside dependencies
def ensure_yaml():      _ensure_pylib_impl("yaml", pip_libname="pyyaml",min_version='5.1')
def ensure_pylint():    _ensure_pylib_impl("pylint")
def ensure_psutil():    _ensure_pylib_impl("psutil")
def ensure_netcdf4():   _ensure_pylib_impl("netCDF4")
def ensure_packaging(): _ensure_pylib_impl("packaging")

###############################################################################
class GoodFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter
):
###############################################################################
    """
    We want argument default info to be added but we also want to
    preserve formatting in the description string.
    """

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
def logical_cores_per_physical_core():
###############################################################################
    return psutil.cpu_count() // psutil.cpu_count(logical=False)

###############################################################################
def get_cpu_ids_from_slurm_env_var():
###############################################################################
    """
    Parse the SLURM_CPU_BIND_LIST, and use the hexadecimal value to determine
    which CPUs on this node are assigned to the job
    NOTE: user should check that the var is set BEFORE calling this function
    """

    cpu_bind_list = os.getenv('SLURM_CPU_BIND_LIST')

    expect (cpu_bind_list is not None,
            "SLURM_CPU_BIND_LIST environment variable is not set. Check, before calling this function")

    # Remove the '0x' prefix and convert to an integer
    mask_int = int(cpu_bind_list, 16)

    # Generate the list of CPU IDs
    cpu_ids = []
    for i in range(mask_int.bit_length()):  # Check each bit position
        if mask_int & (1 << i):  # Check if the i-th bit is set
            cpu_ids.append(i)

    return cpu_ids

###############################################################################
def get_available_cpu_count(logical=True):
###############################################################################
    """
    Get number of CPUs available to this process and its children. logical=True
    will include hyperthreads, logical=False will return only physical cores
    """
    if 'SLURM_CPU_BIND_LIST' in os.environ:
        cpu_count = len(get_cpu_ids_from_slurm_env_var())
    else:
        cpu_count = len(psutil.Process().cpu_affinity())

    if not logical:
        hyperthread_ratio = logical_cores_per_physical_core()
        return int(cpu_count / hyperthread_ratio)
    else:
        return cpu_count

###############################################################################
class SharedArea(object):
###############################################################################
    """
    Enable 0002 umask within this manager
    """

    def __init__(self, new_perms=0o002):
        self._orig_umask = None
        self._new_perms  = new_perms

    def __enter__(self):
        self._orig_umask = os.umask(self._new_perms)

    def __exit__(self, *_):
        os.umask(self._orig_umask)

###############################################################################
def expand_variables(tgt_obj, src_obj_dict):
###############################################################################

    # Only user-defined types have the __dict__ attribute
    if hasattr(tgt_obj,'__dict__'):
        for name,val in vars(tgt_obj).items():
            setattr(tgt_obj,name,expand_variables(val,src_obj_dict))

    elif isinstance(tgt_obj,dict):
        for name,val in tgt_obj.items():
            tgt_obj[name] = expand_variables(val,src_obj_dict)

    elif isinstance(tgt_obj,list):
        for i,val in enumerate(tgt_obj):
            tgt_obj[i] = expand_variables(val,src_obj_dict)

    elif isinstance(tgt_obj,str):
        pattern = r'\$\{(\w+)\.(\w+)\}'

        matches = re.findall(pattern,tgt_obj)
        for obj_name, att_name in matches:
            expect (obj_name in src_obj_dict.keys(),
                    f"Invalid configuration ${{{obj_name}.{att_name}}}. Must be ${{obj.attr}}, with obj in {src_obj_dict.keys()}")
            obj = src_obj_dict[obj_name]

            try:
                value = getattr(obj,att_name)
                expect (not value is None,
                        f"Cannot use attribute {obj_name}.{att_name} in configuration, since it is None.\n")
                value_str = str(value)
                old = tgt_obj
                tgt_obj = tgt_obj.replace(f"${{{obj_name}.{att_name}}}",value_str)
            except AttributeError:
                print (f"{obj_name} has no attribute '{att_name}'\n")
                print (f"  - existing attributes: {dir(obj)}\n")
                raise

        expect (not re.findall(pattern,tgt_obj),
                f"Something went wrong while replacing ${{..}} patterns in string '{tgt_obj}'\n")

    return tgt_obj

###############################################################################
def evaluate_commands(tgt_obj):
###############################################################################

    # Only user-defined types have the __dict__ attribute
    if hasattr(tgt_obj,'__dict__'):
        for name,val in vars(tgt_obj).items():
            setattr(tgt_obj,name,evaluate_commands(val))

    elif isinstance(tgt_obj,dict):
        for name,val in tgt_obj.items():
            tgt_obj[name] = evaluate_commands(val)

    elif isinstance(tgt_obj,list):
        for i,val in enumerate(tgt_obj):
            tgt_obj[i] = evaluate_commands(val)

    elif isinstance(tgt_obj,str):
        pattern = r'\$\((.*?)\)'

        matches = re.findall(pattern,tgt_obj)
        for cmd in matches:
            stat,out,err = run_cmd(cmd)
            expect (stat==0,
                    "Could not evaluate the command.\n"
                    f"  - original string: {tgt_obj}\n"
                    f"  - command: {cmd}\n"
                    f"  - error: {err}\n")

            tgt_obj = tgt_obj.replace(f"$({cmd})",out)

    return tgt_obj

###############################################################################
def is_git_repo(repo=None):
###############################################################################
    """
    Check that the folder is indeed a git repo
    """

    stat, _, _ = run_cmd("git rev-parse --is-inside-work-tree",from_dir=repo)

    return stat==0

###############################################################################
def get_current_ref(repo=None):
###############################################################################
    """
    Return the name of the current branch for a repository
    If in detached HEAD state, returns None
    """

    return run_cmd_no_fail("git rev-parse --abbrev-ref HEAD",from_dir=repo)

###############################################################################
def get_current_sha(short=False,repo=None):
###############################################################################
    """
    Return the sha1 of the current HEAD commit

    >>> get_current_commit() is not None
    True
    """

    return run_cmd_no_fail(f"git rev-parse {'--short' if short else ''} HEAD",from_dir=repo)
