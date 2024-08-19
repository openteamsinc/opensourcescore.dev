import re


def identify_license(license_content: str) -> str:
    # Normalize the license content
    normalized_content = (
        license_content.lower().replace("\n", " ").replace("*", "").strip()
    )

    # Remove excessive whitespace
    normalized_content = re.sub(r"\s+", " ", normalized_content)

    # Quick checks for explicit license tags
    if "mit license" in normalized_content:
        return {"license": "MIT License", "kind": "MIT"}
    elif "apache license, version 2.0" in normalized_content:
        return {"license": "Apache License 2.0", "kind": "Apache"}
    elif "gnu general public license" in normalized_content:
        return {"license": "GNU General Public License (GPL)", "kind": "GPL"}
    elif "gnu lesser general public license" in normalized_content:
        return {"license": "GNU Lesser General Public License (LGPL)", "kind": "LGPL"}
    elif "mozilla public license, v. 2.0" in normalized_content:
        return {"license": "Mozilla Public License 2.0", "kind": "MPL"}
    elif "bsd 3-clause license" in normalized_content:
        return {"license": "BSD 3-Clause License", "kind": "BSD"}

    # Regular expression pattern matching for BSD 3-Clause License
    bsd_pattern = (
        r"redistribution and use .* (source|binary) forms"
        r".* retain .* copyright notice, .* conditions .* disclaimer"
        r".* neither the name of"
    )

    if re.search(bsd_pattern, normalized_content, re.DOTALL):
        return {"license": "BSD 3-Clause License", "kind": "BSD"}

    # If "All Rights Reserved" is present but no specific license pattern is detected, it might be proprietary
    if (
        "all rights reserved" in normalized_content
        and "redistribution and use" not in normalized_content
    ):
        return {"license": "Proprietary", "kind": "Unknown"}

    # If no match, return unknown
    return {"license": "Unknown", "kind": "Unknown"}
