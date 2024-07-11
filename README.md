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







