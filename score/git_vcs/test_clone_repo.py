import os
import tempfile

import pytest
from git import Repo

from .clone_repo import clone_repo


@pytest.fixture(scope="module")
def git_repo_to_clone():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = os.path.join(tmpdir, "test_repo")
        repo = Repo.init(repo_path)

        # Create files that match sparse checkout patterns
        license_file = os.path.join(repo_path, "LICENSE")
        with open(license_file, "w") as f:
            f.write("MIT License\n")

        package_json_file = os.path.join(repo_path, "package.json")
        with open(package_json_file, "w") as f:
            f.write('{"name": "test-package", "version": "1.0.0"}\n')

        pyproject_file = os.path.join(repo_path, "pyproject.toml")
        with open(pyproject_file, "w") as f:
            f.write('[build-system]\nrequires = ["setuptools"]\n')

        other_file = os.path.join(repo_path, "other_file.txt")
        with open(other_file, "w") as f:
            f.write("Some other stuff\n")

        repo.index.add([license_file, package_json_file, pyproject_file, other_file])
        repo.index.commit("Initial commit")

        yield repo_path

        repo.close()


def test_clone_repo_happy_path(git_repo_to_clone):
    with clone_repo(git_repo_to_clone) as (repo, source):
        assert repo is not None
        assert source is not None
        assert source.error is None
        assert os.path.exists(os.path.join(repo.working_dir, "LICENSE"))


def test_clone_repo_sparse_checkout_files(git_repo_to_clone):
    with clone_repo(git_repo_to_clone) as (repo, source):
        assert repo is not None
        assert os.path.exists(os.path.join(repo.working_dir, "package.json"))
        assert os.path.exists(os.path.join(repo.working_dir, "pyproject.toml"))
        # ---
        assert not os.path.exists(os.path.join(repo.working_dir, "other_file.txt"))


def test_clone_repo_nonexistent_local_path():
    nonexistent_path = "/tmp/definitely/does/not/exist"
    with clone_repo(nonexistent_path) as (repo, source):
        assert repo is None
        assert source is not None
        assert source.error is not None


def test_clone_repo_cleanup_on_success(git_repo_to_clone):
    temp_dirs_before = set(os.listdir(tempfile.gettempdir()))

    with clone_repo(git_repo_to_clone) as (repo, source):
        assert repo is not None
        temp_dir = repo.working_dir
        assert os.path.exists(temp_dir)

    temp_dirs_after = set(os.listdir(tempfile.gettempdir()))
    assert not os.path.exists(temp_dir)
    assert temp_dirs_before == temp_dirs_after


def test_clone_repo_cleanup_on_error():
    temp_dirs_before = set(os.listdir(tempfile.gettempdir()))

    with clone_repo("https://github.com/nonexistent/repo") as (repo, source):
        assert repo is None

    temp_dirs_after = set(os.listdir(tempfile.gettempdir()))
    assert temp_dirs_before == temp_dirs_after


def test_clone_repo_invalid_git_url():
    invalid_git_url = "not-a-valid-url"
    with clone_repo(invalid_git_url) as (repo, source):
        assert repo is None
        assert source is not None
        assert source.error is not None
