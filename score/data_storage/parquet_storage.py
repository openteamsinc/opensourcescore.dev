import os
import pandas as pd
from utils.common import get_next_parquet_filename, get_parquet_record_count


def save_to_parquet(df, letter, max_records_per_parquet, output_dir):
    """
    Saves the given DataFrame to a Parquet file. If the Parquet file exceeds the specified maximum
    number of records, a new Parquet file is created.

    Args:
        df (DataFrame): The DataFrame to save.
        letter (str): The starting letter of the package names to include in the filename.
        max_records_per_parquet (int): The maximum number of records allowed in a single Parquet file.
        output_dir (str): The directory to save the Parquet files in.
    """
    # Ensure the directory exists before generating the filename
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Base name for Parquet files
    output_parquet_base = os.path.join(output_dir, f"pypi_packages_{letter}")

    # Find existing Parquet files and sort them
    parquet_files = sorted(
        [
            f
            for f in os.listdir(output_dir)
            if f.startswith(f"pypi_packages_{letter}") and f.endswith(".parquet")
        ]
    )

    # Determine the current Parquet file to write to
    current_parquet = (
        parquet_files[-1]
        if parquet_files
        else os.path.basename(get_next_parquet_filename(output_parquet_base))
    )

    current_parquet_path = os.path.join(output_dir, current_parquet)

    # Check the record count of the current Parquet file
    if os.path.exists(current_parquet_path):
        current_parquet_record_count = get_parquet_record_count(current_parquet_path)
    else:
        current_parquet_record_count = 0

    # If the current Parquet file exceeds the max records, create a new Parquet file
    if current_parquet_record_count + len(df) > max_records_per_parquet:
        current_parquet = os.path.basename(
            get_next_parquet_filename(output_parquet_base)
        )
        current_parquet_path = os.path.join(output_dir, current_parquet)
        current_parquet_record_count = 0

    # Save DataFrame to the current Parquet file
    if os.path.exists(current_parquet_path):
        existing_parquet_df = pd.read_parquet(current_parquet_path)
        combined_df = pd.concat([existing_parquet_df, df], ignore_index=True)
        combined_df.to_parquet(current_parquet_path, index=False)
    else:
        df.to_parquet(current_parquet_path, index=False)

    current_parquet_record_count += len(df)
