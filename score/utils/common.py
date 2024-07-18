import os
import pandas as pd
from config import OUTPUT_DIR


def get_next_parquet_filename(base_name, extension=".parquet"):
    index = 1
    filename = f"{base_name}_{index}{extension}"
    while os.path.exists(os.path.join(OUTPUT_DIR, filename)):
        index += 1
        filename = f"{base_name}_{index}{extension}"
    return filename


def get_parquet_record_count(file_path):
    if os.path.exists(file_path):
        df = pd.read_parquet(file_path)
        return len(df)
    return 0
