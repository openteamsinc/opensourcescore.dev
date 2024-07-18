import os


def save_to_csv(df, letter, output_dir):
    output_csv = os.path.join(output_dir, f"pypi_packages_{letter}.csv")
    # Ensure the directory exists before saving
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(output_csv):
        df.to_csv(output_csv, mode="w", index=False, header=True)
    else:
        df.to_csv(output_csv, mode="a", index=False, header=False)
