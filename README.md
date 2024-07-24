# OpenTeams Score

## Overview

OpenTeams Score is a Python-based tool designed to evaluate and categorize open source projects. 
It provides users with valuable insights to assess the suitability of open source dependencies for their projects.

The end product of this repo is a score dataset

## Features

- Dual-category scoring system: Maturity and Health & Risk
- Data export to BigQuery for easy access and analysis
- Open-source scraping scripts for transparency and collaboration

## Maturity Categories

1. Mature
2. Developing
3. Experimental
4. Legacy

## Health & Risk Categories

### 1. Healthy

### 2. Caution Needed

### 3. High Risk

- **Definition**: This category is assigned to projects or systems that have significant issues or vulnerabilities that pose serious risks to stability, security, or performance. It may be in a state of neglect or facing challenges that critically impact its viability.
- **Characteristics**:
  - **Unstable and Unreliable**: Frequent crashes, data loss, or critical bugs significantly impair functionality and reliability.
  - **Lack of Maintenance**: Little to no active development, with outstanding critical issues and vulnerabilities left unaddressed.
  - **Insufficient Documentation and Support**: Documentation is outdated or incomplete, and support resources are scarce or non-existent.
  - **Critical Security Vulnerabilities**: Known security vulnerabilities are severe and may compromise user data or system integrity.
  - **Limited to No Adoption**: Very few users, if any, due to the risks and issues associated with its use.
- **Use Case**: Not recommended for any new projects or production environments. Existing users should seek alternatives or plan for significant mitigation measures if continued use is absolutely necessary.

## Datasets:

### PyPI Packages

`gs://openteams-score/pypi.parquet`

Parquet Table columns:

* `source_location`: (primary ID) The URI of the source code 
* `name`: The name of the package
* `version`: the version


### Scores Result 

The Scores Result is a JSON object that provides detailed information about the evaluated open source project. This includes metadata about the project, the packages it contains, and the scores assigned to it based on maturity and health & risk categories.

#### JSON Structure

```json
    {
        "source_url": "https://pypi.org/project/python-asdf/",
        "project_name": "asdf",
        "source_type": "pypi",
        "homepage_url": "https://foo.com",
        "packages": [
            {
                "package_type": "pypi",
                "package_id": "python-asdf",
                "latest_version": "2.7.1",
                "release_date": "2023-09-15"
            },
        ],
        "scores": {
            "maturity": {
                "value": "developing",
                "notes": [
                    "Package is over 2 years old",
                    "Regular updates and releases"
                ]
            },
            "health_risk": {
                "value": "healthy",
                "notes": [
                    "Package has a low number of contributors",
                    "No known vulnerabilities",
                    "Good test coverage"
                ]
            }
        }
    }
```

#### Fields Description

- **source_url**: The URL to the project's page on the source platform (e.g., PyPI).
- **project_name**: The name of the project.
- **source_type**: The type of source platform (e.g., PyPI).
- **homepage_url**: The URL to the project's homepage.
- **packages**: A list of packages associated with the project.
  - **package_type**: The type of package (e.g., PyPI).
  - **package_id**: The unique identifier of the package.
  - **latest_version**: The latest version of the package.
  - **release_date**: The release date of the latest version.
- **scores**: The scores assigned to the project.
  - **maturity**: The maturity score of the project.
    - **value**: The maturity category (e.g., developing).
    - **notes**: Additional notes explaining the maturity score.
  - **health_risk**: The health & risk score of the project.
    - **value**: The health & risk category (e.g., healthy).
    - **notes**: Additional notes explaining the health & risk score.







