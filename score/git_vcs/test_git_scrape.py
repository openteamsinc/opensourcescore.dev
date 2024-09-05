from .scrape import create_git_metadata


def test_scrape():
    metadata = create_git_metadata("https://github.com/numpy/numpy")
    assert metadata
    assert metadata["license"]["kind"] == "BSD"
    assert metadata["py_package"] == "numpy"
