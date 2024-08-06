import pandas as pd


def json_to_parquet(json_data: list, parquet_file_path: str) -> None:
    """
    Converts the JSON data to a DataFrame and writes it to a parquet file.

    Args:
        json_data (list): The JSON data to be converted.
        parquet_file_path (str): The path to the parquet file.

    Returns:
        None
    """
    df = pd.DataFrame(json_data)
    df.to_parquet(parquet_file_path, partition_cols=["initial_letter"])
