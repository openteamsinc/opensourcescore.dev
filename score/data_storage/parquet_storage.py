import os
import pandas as pd
from utils.common import get_next_parquet_filename, get_parquet_record_count
from config import OUTPUT_DIR

def save_to_parquet(df, letter, max_records_per_parquet):
    output_parquet_base = f'pypi_packages_{letter}'
    parquet_files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.startswith(output_parquet_base) and f.endswith('.parquet')])
    current_parquet = parquet_files[-1] if parquet_files else get_next_parquet_filename(output_parquet_base)
    
    current_parquet_path = os.path.join(OUTPUT_DIR, current_parquet)
    if os.path.exists(current_parquet_path):
        current_parquet_record_count = get_parquet_record_count(current_parquet_path)
    else:
        current_parquet_record_count = 0

    if current_parquet_record_count + len(df) > max_records_per_parquet:
        current_parquet = get_next_parquet_filename(output_parquet_base)
        current_parquet_path = os.path.join(OUTPUT_DIR, current_parquet)
        current_parquet_record_count = 0

    if os.path.exists(current_parquet_path):
        existing_parquet_df = pd.read_parquet(current_parquet_path)
        combined_df = pd.concat([existing_parquet_df, df], ignore_index=True)
        combined_df.to_parquet(current_parquet_path, index=False)
    else:
        df.to_parquet(current_parquet_path, index=False)
    
    current_parquet_record_count += len(df)
