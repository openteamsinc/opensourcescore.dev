from .license_name_to_kind import KIND_MAP

common_license_names_to_kind = {
    "BSD-2-Clause": "BSD",
    "The-Unlicense-(Unlicense)": "UNLICENSE",
    "Mozilla-Public-License-2.0-(MPL-2.0)": "MPL",
}

common_license_names_to_kind.update(KIND_MAP)
common_license_names_to_kind = {
    k.lower(): v for (k, v) in common_license_names_to_kind.items()
}


def get_kind_from_common_license_name(license_name: str):

    license_name = license_name.lower()
    if license_name.endswith(" license"):
        license_name = license_name[:-8]

    license_name.replace(" ", "-")

    return common_license_names_to_kind.get(license_name, license_name)
