import pandas as pd
from hashlib import sha256


def get_git_urls(input: str, num_partitions: int, partition: int) -> list:
    df = pd.read_parquet(input).dropna()

    def is_in_partition(name: str):
        package_hash = sha256(name.encode()).hexdigest()
        return (int(package_hash, base=16) % num_partitions) == partition

    filtered_df = df[df.source_url.apply(is_in_partition)]

    print(filtered_df)
    print(filtered_df.index.size)
    return filtered_df.source_url.to_list()
