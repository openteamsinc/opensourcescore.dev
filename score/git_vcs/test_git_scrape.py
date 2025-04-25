from .scrape import create_git_metadata_str


def test_scrape():
    metadata = create_git_metadata_str("https://github.com/numpy/numpy")
    assert metadata
    print(metadata)
    assert metadata.license.kind == "BSD"
    assert metadata.package_destinations == [("pypi/numpy", "/pyproject.toml")]


def test_scrape_flask():
    metadata = create_git_metadata_str("https://github.com/pallets/flask")
    assert metadata
    print(metadata)
    assert metadata.license.kind == "BSD"
    assert metadata.package_destinations[0] == ("pypi/flask", "/pyproject.toml")
