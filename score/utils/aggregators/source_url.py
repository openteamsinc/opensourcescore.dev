import os
import pandas as pd


def get_source_urls(input_dir, output_dir, partition):
    """
    Read parquet files from the input directory, filter based on the partition,
    extract required fields, and write to the output directory.
    """
    aggregated_df = pd.DataFrame()

    dir_path = os.path.join(input_dir, f"partition={partition}")
    if os.path.exists(dir_path):
        df = pd.read_parquet(dir_path)
        if "name" in df.columns and "source_url" in df.columns:
            df_filtered = df[["name", "source_url"]]
            df_filtered = df_filtered.dropna(
                subset=["source_url"]
            )  # Drop rows where source_url is null
            aggregated_df = pd.concat([aggregated_df, df_filtered], ignore_index=True)
        else:
            print(
                f"The required columns are not present in the data for partition {partition}."
            )

    # Write the aggregated data to the output directory
    if not aggregated_df.empty:
        aggregated_df.to_parquet(
            os.path.join(output_dir, f"partition={partition}.parquet")
        )
    else:
        print("No data to write after aggregation.")