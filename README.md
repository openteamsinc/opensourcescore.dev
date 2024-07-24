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

- **Definition**: This category indicates that while the project or system may be functional, there are known issues or potential vulnerabilities that require attention. Users should proceed with caution, especially in production environments.
- **Characteristics**:
  - **Moderate Stability**: Generally stable but may have known bugs or performance issues that could impact its reliability.
  - **Irregular Updates**: Updates and maintenance may be less frequent, potentially leaving some issues unresolved for longer periods.
  - **Adequate Documentation and Support**: Documentation covers most aspects, but there may be gaps. Support is available but may not be as responsive or comprehensive.
  - **Potential Security Concerns**: Some security vulnerabilities may have been identified, and while they may not be critical, they necessitate vigilance and regular monitoring.
  - **Selective Adoption**: Used by a community of users, but its adoption may be limited to specific scenarios or environments where its known issues do not pose significant risks.
- **Use Case**: Suitable for non-critical applications or environments where users can manage or mitigate known risks. Caution and additional testing are advised before deployment in production.

### 3. High Risk

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







