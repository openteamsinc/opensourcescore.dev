from typing import List
from ..utils.request_session import get_session
from hashlib import sha256

CONDA_URL_TEMPLATE = "https://conda.anaconda.org/{channel}/linux-64/repodata.json"


def get_all_conda_package_names(channel: str) -> List[str]:
    s = get_session()
    res = s.get(CONDA_URL_TEMPLATE.format(channel=channel))
    res.raise_for_status()

    data = res.json()
    return list({p["name"] for p in data["packages"].values()})


def get_conda_package_names(
    num_partitions: int, partition: int, channel: str
) -> List[str]:
    all_packages = get_all_conda_package_names(channel)

    def is_in_partition(name: str):
        package_hash = sha256(name.encode()).hexdigest()
        return (int(package_hash, base=16) % num_partitions) == partition

    return [p for p in all_packages if is_in_partition(p)]
