import pytest
import distutils
import subprocess
import os
import atexit
from filelock import FileLock
from tests.utils import get_config_file_path

@pytest.fixture(scope="session", autouse=True)
def test_setup(tmp_path_factory, worker_id):
    def _test_setup():
        if distutils.spawn.find_executable("docker") and distutils.spawn.find_executable("terraform"):
            print("Setting up docker/terraform")
            # We can spin up Vault inside docker and use terraform to do some base configuration
            docker_file = get_config_file_path("vault-ldap/docker-compose.yml")
            try:
                subprocess.check_call(f"docker compose -f '{docker_file}' up -d --wait vault openldap", shell=True)
            except Exception as e:
                print("Failed to setup docker/terraform for test, you must have Vault installed locally. Error: " + str(e))

    def _test_teardown():
        if distutils.spawn.find_executable("docker") and distutils.spawn.find_executable("terraform"):
            print("Tearing down docker/terraform")
            docker_file = get_config_file_path("vault-ldap/docker-compose.yml")
            subprocess.check_call(f"docker compose -f '{docker_file}' down vault openldap", shell=True)

    if worker_id == "master":
        _test_teardown()
        _test_setup()
        atexit.register(_test_teardown)
        return

    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    fn = root_tmp_dir / "setup"
    with FileLock(str(fn) + ".lock"):
        if fn.is_file():
            return
        else:
            if os.path.exists('../../vault.json'): os.unlink('../../vault.json')
            if os.path.exists('../../vault.json.lock'): os.unlink('../../vault.json.lock')
            _test_teardown()
            _test_setup()
            atexit.register(_test_teardown)
            fn.write_text(".")
    