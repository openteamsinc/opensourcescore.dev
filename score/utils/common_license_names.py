from .licence_name_to_kind import KIND_MAP

common_license_names_to_kind = {
    "BSD License": "BSD",
    "The Unlicense (Unlicense)": "UNLICENSE",
    "BSD-2-Clause": "BSD",
    "MIT License": "MIT",
    "Mozilla Public License 2.0 (MPL 2.0)": "MPL",
}


common_license_names_to_kind.update(KIND_MAP)
