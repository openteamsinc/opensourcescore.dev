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

### 1. Experimental

### 2. Developing

### 3. Mature

### 4. Legacy

- **Definition**: The project has reached the end of its active development lifecycle. It may still be in use but is no longer actively maintained or updated.
- **Characteristics**:
  - **Limited Updates**: Updates are rare and typically only address critical bugs or security vulnerabilities.
  - **Stable but Outdated**: The project is stable but may not comply with current standards or best practices. New features and improvements are not being added.
  - **Declining User Base**: The community and user base may be shrinking, and finding support or resources can be challenging.
  - **Use Case**: Suitable for systems that depend on it for legacy reasons but should be considered for replacement or upgrade in the near term.

## Health & Risk Categories

1. Healthy
2. Caution Needed
3. High Risk

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







