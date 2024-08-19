def get_pypi_packages(db, source_url):
    pypi_packages = (
        db.query(f"select * from pypi where source_url = '{source_url}'")
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


def get_conda_packages(db, source_url):
    conda_packages = (
        db.query(f"select * from conda where source_url = '{source_url}'")
        .df()
        .set_index("full_name")
    )
    packages = [
        {
            "name": package_name,
            "ecosystem": "Conda",
            "version": package_data.latest_version,
        }
        for package_name, package_data in conda_packages.iterrows()
    ]
    return packages
