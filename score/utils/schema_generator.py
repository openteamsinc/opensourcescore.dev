import os
import json
import logging
import pyarrow.parquet as pq

# Configure logging
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set PROJECT_ROOT to the root of your project (Score directory)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define the paths using the project root
BASE_DIR = os.path.join(PROJECT_ROOT, "output", "conda", "channel=conda-forge", "partition=0")
OUTPUT_FILE_NAME = "conda_schema.json"
SCHEMA_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "schemas")


def get_first_parquet_file(partition_dir):
    """Return the path of the first Parquet file found in the specified partition directory."""
    for file_name in os.listdir(partition_dir):
        if file_name.endswith(".parquet"):
            return os.path.join(partition_dir, file_name)
    return None


def schema_to_dict(schema):
    """Convert a pyarrow Schema to a dictionary suitable for JSON serialization."""
    return {
        "fields": [{"name": field.name, "type": str(field.type)} for field in schema]
    }


def save_schema_as_json(parquet_file_path, output_path):
    """Save the schema of a Parquet file as a JSON file."""
    try:
        parquet_file = pq.ParquetFile(parquet_file_path)
        schema = parquet_file.schema.to_arrow_schema()

        # Convert the schema to a JSON-serializable format
        schema_dict = schema_to_dict(schema)

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save to a JSON file
        with open(output_path, "w") as f:
            json.dump(schema_dict, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save schema: {e}")


def main():
    parquet_file_path = get_first_parquet_file(BASE_DIR)
    if parquet_file_path:
        output_path = os.path.join(SCHEMA_OUTPUT_DIR, OUTPUT_FILE_NAME)
        save_schema_as_json(parquet_file_path, output_path)
    else:
        logging.error(f"No Parquet files found in the directory: {BASE_DIR}")


if __name__ == "__main__":
    main()
