# OpenTeams Score

## Overview

OpenTeams Score is a Python-based tool designed to evaluate and categorize open source projects. 
It provides users with valuable insights to assess the suitability of open source dependencies for their projects.

The end product of this repo is a score dataset

## Features

- Dual-category scoring system: Maturity and Health & Risk
- Data export to BigQuery for easy access and analysis
- Open-source scraping scripts for transparency and collaboration

## Sources 

- PyPI (Python Package Index) - The official repository for Python packages
- Conda - The package manager for the Anaconda distribution of Python packages
- GitHub - The world's leading software development platform for open source projects
- GitLab - A web-based DevOps lifecycle tool for open source projects
- NPM (Node Package Manager) - The package manager for JavaScript and Node.js packages
- SourceForge - A web-based source code repository for open source projects

## Maturity Categories

### 1. Experimental

- **Definition**: The project is in the initial phase of its development lifecycle. It is primarily aimed at early adopters and developers interested in the latest features or in contributing to the project's development.
- **Characteristics**:
  - **Frequent Breaking Changes**: The API or core functionality may change often, requiring adjustments in dependent code with each update.
  - **Small User Base**: Typically has a smaller community of users and contributors, which can affect the speed of issue resolution and feature requests.
- **Use Case**: Best suited for development and testing environments, or for research and exploration of new concepts.

### 2. Developing

- **Definition**: The project has progressed beyond the experimental stage and is in active development. It is becoming more stable but may still undergo significant changes.
- **Characteristics**:
  - **Moderate Stability**: The core API and features are more stable than in the experimental stage, but some changes and enhancements are still occurring.
  - **Expanding User Base**: The community of users and contributors is growing, leading to more feedback, bug reports, and feature requests.
- **Use Case**: Suitable for projects that can accommodate some changes and are not critically dependent on absolute stability.

### 3. Mature

- **Definition**: The project is stable and has reached a level of maturity where major changes are infrequent. It is suitable for production use.
- **Characteristics**:
  - **High Stability**: Core features and APIs are stable, with changes primarily focused on bug fixes, security improvements, and minor enhancements.
  - **Large User Base**: Has a large and active community providing extensive support, which contributes to a robust ecosystem of plugins, integrations, and tools.
- **Use Case**: Ideal for production environments where reliability and stability are paramount.

### 4. Legacy

- **Definition**: The project has reached the end of its active development lifecycle. It may still be in use but is no longer actively maintained or updated.
- **Characteristics**:
  - **Limited Updates**: Updates are rare and typically only address critical bugs or security vulnerabilities.
  - **Stable but Outdated**: The project is stable but may not comply with current standards or best practices. New features and improvements are not being added.
  - **Declining User Base**: The community and user base may be shrinking, and finding support or resources can be challenging.
- **Use Case**: Suitable for systems that depend on it for legacy reasons but should be considered for replacement or upgrade in the near term.


## Health & Risk Categories

### 1. Healthy

- **Definition**: This category signifies that the project or system is in an optimal state of operation. It is stable, actively maintained, and has minimal issues or vulnerabilities that affect its functionality or security.
- **Characteristics**:
  - **Stability and Reliability**: Demonstrates consistent performance and reliability under various conditions.
  - **Active Development and Maintenance**: Regular updates and active development indicate ongoing improvements and timely bug fixes.
  - **Low Security Risks**: Security measures are robust, with regular patches for vulnerabilities, ensuring a secure environment for users.
  - **Broad Adoption**: Widely adopted by users, indicating trust and dependability in real-world applications.
- **Use Case**: Ideal for critical applications where reliability and security are paramount. Suitable for both development and production environments.

### 2. Caution Needed

- **Definition**: This category indicates that while the project or system may be functional, there are known issues or potential vulnerabilities that require attention. Users should proceed with caution, especially in production environments.
- **Characteristics**:
  - **Moderate Stability**: Generally stable but may have known bugs or performance issues that could impact its reliability.
  - **Irregular Updates**: Updates and maintenance may be less frequent, potentially leaving some issues unresolved for longer periods.
  - **Potential Security Concerns**: Some security vulnerabilities may have been identified, and while they may not be critical, they necessitate vigilance and regular monitoring.
  - **Selective Adoption**: Used by a community of users, but its adoption may be limited to specific scenarios or environments where its known issues do not pose significant risks.
- **Use Case**: Suitable for non-critical applications or environments where users can manage or mitigate known risks. Caution and additional testing are advised before deployment in production.

### 3. High Risk

- **Definition**: This category is assigned to projects or systems that have significant issues or vulnerabilities that pose serious risks to stability, security, or performance. It may be in a state of neglect or facing challenges that critically impact its viability.
- **Characteristics**:
  - **Unstable and Unreliable**: Frequent crashes, data loss, or critical bugs significantly impair functionality and reliability.
  - **Lack of Maintenance**: Little to no active development, with outstanding critical issues and vulnerabilities left unaddressed.
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







