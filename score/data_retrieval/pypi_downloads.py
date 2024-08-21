import pandas as pd
from google.cloud import bigquery
import logging

log = logging.getLogger(__name__)


def get_bulk_download_counts() -> pd.DataFrame:
    """
    Fetches download counts for all packages over the last month from BigQuery and returns it as a DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing the download counts. The DataFrame includes the following fields:
        
        - `name` (str): The name of the package.
        - `last_day` (int): The number of downloads for the package on the last day.
        - `last_week` (int): The number of downloads for the package over the last 7 days (excluding today).
        - `last_month` (int): The number of downloads for the package over the last 30 days (excluding today).
    """
    client = bigquery.Client(project="openteams-score")

    query = """
    SELECT
      file.project AS package_name,
      COUNTIF(DATE(timestamp) = CURRENT_DATE() - 1) AS last_day,
      COUNTIF(DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND CURRENT_DATE() - 1) AS last_week,
      COUNTIF(DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) AND CURRENT_DATE() - 1) AS last_month
    FROM
      `bigquery-public-data.pypi.file_downloads`
    WHERE
      DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    GROUP BY
      package_name
    ORDER BY
      package_name;
    """

    query_job = client.query(query)
    results = query_job.result()

    download_data = {
        row.package_name: {
            "last_day": row.last_day,
            "last_week": row.last_week,
            "last_month": row.last_month,
        }
        for row in results
    }

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame.from_dict(download_data, orient="index").reset_index()

    # Rename the index column to "name"
    df.rename(columns={"index": "name"}, inplace=True)

    return df
