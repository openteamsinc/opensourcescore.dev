import os
import pandas as pd
from config import OUTPUT_DIR

def save_to_csv(df, letter):
    output_csv = os.path.join(OUTPUT_DIR, f'pypi_packages_{letter}.csv')
    df.to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False)
