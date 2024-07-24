import os
import pandas as pd
import duckdb


def save_to_parquet(df, letter, output_dir):
    """
    Saves the given DataFrame to a Parquet file using DuckDB for Hive-style partitioning.

    Args:
        df (DataFrame): The DataFrame to save.
        letter (str): The starting letter of the package names to include in the filename.
        output_dir (str): The directory to save the Parquet files in.
    """
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Add the letter column to the DataFrame for partitioning
    df["letter"] = letter

    # Define the DuckDB connection
    con = duckdb.connect()  # Connect to an in-memory DuckDB instance
    partitioned_dir = os.path.join(output_dir, f"letter={letter}")

    # Ensure the partitioned directory exists
    if not os.path.exists(partitioned_dir):
        os.makedirs(partitioned_dir)

    parquet_file = os.path.join(partitioned_dir, "pypi_packages.parquet")

    # Check if the Parquet file for the partition exists
    if os.path.exists(parquet_file):
        # Read the existing Parquet file into a DataFrame
        existing_df = con.execute(f"SELECT * FROM '{parquet_file}'").fetchdf()

        # Combine the existing data with the new data
        combined_df = pd.concat([existing_df, df], ignore_index=True)
    else:
        combined_df = df

    # Register the combined DataFrame as a DuckDB table
    con.register("combined_df", combined_df)

    # Write the combined data back to the Parquet file with overwrite
    con.execute(
        f"""
        COPY combined_df TO '{parquet_file}' (FORMAT PARQUET, OVERWRITE)
        """
    )

    # Close the DuckDB connection
    con.close()
