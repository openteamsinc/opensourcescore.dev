import logging

from common import get_requests_soup, json_to_parquet, requests_get

# Set up logging
logging.basicConfig(level=logging.INFO)

packages_name_list = list()
packages_data_json = dict()

all_packages_name_json_url = "https://raw.githubusercontent.com/conda-forge/feedstock-outputs/single-file/feedstock-outputs.json"

response = requests_get(all_packages_name_json_url)
packages_name_list = response.json() if response else []
logging.info("Total Packages : %s", len(packages_name_list.keys()))


for package_name in list(packages_name_list.keys())[:1]:
    logging.info("Package Name : %s", package_name)

    package_url = f"https://anaconda.org/conda-forge/{package_name}"

    soup = get_requests_soup(package_url)

    if soup:
        license = (
            str(soup.select_one('[title="License"]').text).split(":")[-1].strip()
            if soup.select_one('[title="License"]')
            else None
        )
        print(license)

        homepage_element = soup.select_one('[title="Home Page"]')
        homepage_url = (
            homepage_element.attrs["href"]
            if homepage_element and "href" in homepage_element.attrs
            else None
        )
        print(homepage_url)

        development_element = soup.select_one('[title="Development Url"]').select_one(
            "a"
        )
        development_url = (
            development_element.attrs["href"]
            if development_element and "href" in development_element.attrs
            else None
        )
        print(development_url)

        documentation_element = soup.select_one(
            '[title="Documentation Url"]'
        ).select_one("a")
        documentation_url = (
            documentation_element.attrs["href"]
            if documentation_element and "href" in documentation_element.attrs
            else None
        )
        print(documentation_url)

        download_count_element = soup.select_one('[title="Download Count"]')
        download_count = (
            int(str(download_count_element.select_one("span").text).strip())
            if download_count_element.select_one("span")
            else None
        )
        print(download_count)

        last_upload = (
            str(soup.select_one('[title="Last upload"]').text).split(":")[-1].strip()
            if soup.select_one('[title="Last upload"]')
            else None
        )
        print(last_upload)

        packages_data_json[package_name] = {
            "license": license,
            "homepage_url": homepage_url,
            "development_url": development_url,
            "documentation_url": documentation_url,
            "download_count": download_count,
            "last_upload": last_upload,
        }

    soup = get_requests_soup(f"{package_url}/files")
    if soup:
        versions_list = [
            str(i.text).strip()
            for i in soup.select("#Version > li")
            if str(i.text).strip() != "All"
        ]
        packages_data_json[package_name]["latest_version"] = versions_list[0]
        packages_data_json[package_name]["first_version"] = versions_list[-1]
        packages_data_json[package_name]["version_list"] = versions_list


print(packages_data_json)
