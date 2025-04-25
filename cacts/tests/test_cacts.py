import pytest
from cacts.cacts import Driver, parse_command_line

class TestDriver:
    def test_initialization(self):
        driver = Driver(config_file="config.yaml", machine_name="test_machine", local=False, build_types=["debug"],
                        work_dir="work_dir", root_dir="root_dir", baseline_dir="baseline_dir", cmake_args=["arg1"],
                        test_regex="test_*", test_labels=["label1"], config_only=False, build_only=False,
                        skip_config=False, skip_build=False, generate=False, submit=False, parallel=False, verbose=False)
        assert driver._config_file == "config.yaml"
        assert driver._machine.name == "test_machine"
        assert driver._local == False
        assert driver._builds[0].name == "debug"
        assert driver._work_dir == "work_dir"
        assert driver._root_dir == "root_dir"
        assert driver._baselines_dir == "baseline_dir"
        assert driver._cmake_args == ["arg1"]
        assert driver._test_regex == "test_*"
        assert driver._test_labels == ["label1"]
        assert driver._config_only == False
        assert driver._build_only == False
        assert driver._skip_config == False
        assert driver._skip_build == False
        assert driver._generate == False
        assert driver._submit == False
        assert driver._parallel == False
        assert driver._verbose == False

    def test_run(self):
        driver = Driver(config_file="config.yaml", machine_name="test_machine", local=False, build_types=["debug"],
                        work_dir="work_dir", root_dir="root_dir", baseline_dir="baseline_dir", cmake_args=["arg1"],
                        test_regex="test_*", test_labels=["label1"], config_only=False, build_only=False,
                        skip_config=False, skip_build=False, generate=False, submit=False, parallel=False, verbose=False)
        success = driver.run()
        assert success == True

    def test_generate_cmake_config(self):
        driver = Driver(config_file="config.yaml", machine_name="test_machine", local=False, build_types=["debug"],
                        work_dir="work_dir", root_dir="root_dir", baseline_dir="baseline_dir", cmake_args=["arg1"],
                        test_regex="test_*", test_labels=["label1"], config_only=False, build_only=False,
                        skip_config=False, skip_build=False, generate=False, submit=False, parallel=False, verbose=False)
        build = driver._builds[0]
        cmake_config = driver.generate_cmake_config(build)
        assert "CMAKE_BUILD_TYPE" in cmake_config

    def test_generate_ctest_cmd(self):
        driver = Driver(config_file="config.yaml", machine_name="test_machine", local=False, build_types=["debug"],
                        work_dir="work_dir", root_dir="root_dir", baseline_dir="baseline_dir", cmake_args=["arg1"],
                        test_regex="test_*", test_labels=["label1"], config_only=False, build_only=False,
                        skip_config=False, skip_build=False, generate=False, submit=False, parallel=False, verbose=False)
        build = driver._builds[0]
        cmake_config = driver.generate_cmake_config(build)
        ctest_cmd = driver.generate_ctest_cmd(build, cmake_config)
        assert "ctest" in ctest_cmd

def test_parse_command_line():
    args = ["cacts.py", "-f", "config.yaml", "-m", "test_machine", "-t", "debug", "-w", "work_dir", "-r", "root_dir",
            "-b", "baseline_dir", "-c", "arg1", "--test-regex", "test_*", "--test-labels", "label1", "--config-only",
            "--build-only", "--skip-config", "--skip-build", "-g", "--submit", "-p", "-v"]
    parsed_args = parse_command_line(args, "description", "version")
    assert parsed_args.config_file == "config.yaml"
    assert parsed_args.machine_name == "test_machine"
    assert parsed_args.build_types == ["debug"]
    assert parsed_args.work_dir == "work_dir"
    assert parsed_args.root_dir == "root_dir"
    assert parsed_args.baseline_dir == "baseline_dir"
    assert parsed_args.cmake_args == ["arg1"]
    assert parsed_args.test_regex == "test_*"
    assert parsed_args.test_labels == ["label1"]
    assert parsed_args.config_only == True
    assert parsed_args.build_only == True
    assert parsed_args.skip_config == True
    assert parsed_args.skip_build == True
    assert parsed_args.generate == True
    assert parsed_args.submit == True
    assert parsed_args.parallel == True
    assert parsed_args.verbose == True
