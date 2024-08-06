import os
import pandas as pd


def aggregate(input_dir, output_dir, letters_to_scrape):
    """
    Read parquet files from the input directory, filter based on the first letter,
    extract required fields, and write to the output directory with partitioning.
    """
    aggregated_df = pd.DataFrame()

    for letter in letters_to_scrape:
        dir_path = os.path.join(input_dir, f"first_letter={letter}")
        if os.path.exists(dir_path):
            df = pd.read_parquet(dir_path)
            df["first_letter"] = letter  # Add the first_letter column manually
            if "name" in df.columns and "source_url" in df.columns:
                df_filtered = df[["name", "source_url", "first_letter"]]
                df_filtered = df_filtered.dropna(
                    subset=["source_url"]
                )  # Drop rows where source_url is null
                aggregated_df = pd.concat(
                    [aggregated_df, df_filtered], ignore_index=True
                )
            else:
                print(
                    f"The required columns are not present in the data for letter {letter}."
                )

    # Write the aggregated data to the output directory with partitioning by 'first_letter'
    if not aggregated_df.empty:
        aggregated_df.to_parquet(output_dir, partition_cols=["first_letter"])
    else:
        print("No data to write after aggregation.")
