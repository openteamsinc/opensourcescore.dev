from functools import lru_cache
from google.cloud import logging
import os
import requests
import logging as normal_logging

log = normal_logging.getLogger(__name__)

DEFAULT_PROJECT = "openteams-score"
DEFAULT_LOCATION = "us-west1"


@lru_cache
def get_project_id():
    project_id = os.environ.get("GOOGLE_PROJECT_ID")
    if project_id:
        return project_id

    metadata_url = "http://metadata.google.internal"
    project_id_url = f"{metadata_url}/computeMetadata/v1/project/project-id"
    headers = {"Metadata-Flavor": "Google"}
    try:
        response = requests.get(project_id_url, headers=headers)
        response.raise_for_status()
        project_id = response.text
    except requests.RequestException as e:
        log.error(f"Failed to fetch project ID: {e}")
        return DEFAULT_PROJECT
    return project_id


@lru_cache
def get_location():
    location = os.environ.get("GOOGLE_LOCATION")
    if location:
        return location
    metadata_url = "http://metadata.google.internal"
    location_url = f"{metadata_url}/computeMetadata/v1/instance/zone"
    headers = {"Metadata-Flavor": "Google"}
    try:
        response = requests.get(location_url, headers=headers)
        response.raise_for_status()
        zone = response.text
        location = zone.split("/")[1]
    except requests.RequestException as e:
        log.error(f"Failed to fetch location: {e}")
        return DEFAULT_LOCATION
    return location


@lru_cache
def get_client():

    logging_client = logging.Client(project=get_project_id())
    return logging_client


K_SERVICE = os.environ.get("K_SERVICE", "score")


def get_recent_packages(limit=10):

    filter_ = f"""
    resource.type = "cloud_run_revision"
    resource.labels.service_name = "{K_SERVICE}"
    resource.labels.location = "{get_location()}"
    severity>=DEFAULT
    jsonPayload.package_lookup="yes"
    """

    results = set()
    for entry in get_client().list_entries(filter_=filter_, page_size=20):
        ecosystem = entry.payload.get("ecosystem", None)
        package_name = entry.payload.get("package_name", None)
        if ecosystem and package_name:
            results.add((ecosystem, package_name))
        if len(results) >= limit:
            break

    return list(results)
