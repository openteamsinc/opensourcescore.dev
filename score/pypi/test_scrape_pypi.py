from .json_scraper import get_package_data


def test_scrape_pypi():
    data = get_package_data("Flask")
    print(data)
    assert data
