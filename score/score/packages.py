def get_pypi_packages(db, source_url):
    pypi_packages = (
        db.execute("select * from pypi where source_url = ?", [source_url])
        .df()
        .set_index("name")
    )
    packages = [
        {
            "name": package_name,
            "ecosystem": "PyPI",
            "version": package_data.version,
        }
        for package_name, package_data in pypi_packages.iterrows()
    ]
    return packages


def get_conda_packages(conda_packages):

    packages = [
        {
            "name": package_name,
            "ecosystem": "Conda",
            "version": package_data.latest_version,
        }
        for package_name, package_data in conda_packages.iterrows()
    ]
    return packages
