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
    # Ensure the directory exists before generating the filename
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Add the letter column to the DataFrame for partitioning
    df["letter"] = letter

    # Define the DuckDB connection
    con = duckdb.connect()  # Connect to an in-memory DuckDB instance
    parquet_file = os.path.join(output_dir, f"pypi_packages_{letter}.parquet")

    # Check if the parquet file for the letter exists
    if os.path.exists(parquet_file):
        # Read the existing Parquet file into DuckDB
        con.execute(f"CREATE TABLE existing_data AS SELECT * FROM '{parquet_file}'")

        # Fetch the column names and types of the existing data
        existing_columns = con.execute("PRAGMA table_info(existing_data)").fetchall()
        existing_column_names = [col[1] for col in existing_columns]
        existing_column_types = {col[1]: col[2] for col in existing_columns}

        # Ensure the new DataFrame has the same columns as the existing data
        df = df.reindex(columns=existing_column_names, fill_value=None)

        # Convert the columns in the new DataFrame to match the existing data types
        for column, dtype in existing_column_types.items():
            if column in df.columns:
                if "INT" in dtype.upper():
                    df[column] = (
                        pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)
                    )
                elif "FLOAT" in dtype.upper():
                    df[column] = (
                        pd.to_numeric(df[column], errors="coerce")
                        .fillna(0.0)
                        .astype(float)
                    )
                elif "BOOLEAN" in dtype.upper():
                    df[column] = df[column].astype(bool)
                else:
                    df[column] = df[column].astype(str).fillna("")

        # Register the new DataFrame as a DuckDB table
        con.register("df_table", df)

        # Combine the new data with existing data in DuckDB
        con.execute("INSERT INTO existing_data SELECT * FROM df_table")

        # Write the combined data back to the Parquet file with overwrite
        con.execute(
            f"""
            COPY existing_data TO '{parquet_file}' (FORMAT PARQUET, OVERWRITE)
        """
        )
    else:
        # If no existing file, write the new DataFrame to the Parquet file
        con.register("df_table", df)  # Register the DataFrame as a DuckDB table
        con.execute(
            f"""
            COPY df_table TO '{parquet_file}' (FORMAT PARQUET)
        """
        )

    con.close()
