import pandas as pd
from google.cloud import bigquery
import logging

log = logging.getLogger(__name__)


def get_bulk_download_counts() -> pd.DataFrame:
    """
    Fetches download counts for all packages over the last month from BigQuery and returns it as a DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing the download counts.
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

    # Convert the dictionary to a DataFrame and return it
    df = pd.DataFrame.from_dict(download_data, orient="index")
    return df
