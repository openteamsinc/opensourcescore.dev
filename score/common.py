import pandas as pd


def json_to_parquet(json_data: list, parquet_file_path: str) -> None:
    """
    Convert the JSON data to Parquet file

    Args:
        parquet_file_path (str): Path to save the Parquet file

    Returns:
        None
    """
    df = pd.DataFrame(json_data)
    df.to_parquet(parquet_file_path, partition_cols=["initial_letter"])
