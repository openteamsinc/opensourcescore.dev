import re

def identify_license(license_content: str) -> str:
    # Normalize the license content
    normalized_content = license_content.lower().replace("\n", " ").replace("*", "").strip()
    
    # Remove excessive whitespace
    normalized_content = re.sub(r'\s+', ' ', normalized_content)

    # Quick checks for explicit license tags
    if "mit license" in normalized_content:
        return "MIT License"
    elif "apache license, version 2.0" in normalized_content:
        return "Apache License 2.0"
    elif "gnu general public license" in normalized_content:
        return "GNU General Public License (GPL)"
    elif "gnu lesser general public license" in normalized_content:
        return "GNU Lesser General Public License (LGPL)"
    elif "mozilla public license, v. 2.0" in normalized_content:
        return "Mozilla Public License 2.0"
    elif "bsd 3-clause license" in normalized_content:
        return "BSD 3-Clause License"

    # Regular expression pattern matching for BSD 3-Clause License
    bsd_pattern = (
        r"redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met"
        r".*redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer"
        r".*redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution"
        r".*neither the name of"
    )

    if re.search(bsd_pattern, normalized_content, re.DOTALL):
        return "BSD 3-Clause License"

    # If "All Rights Reserved" is present but no specific license pattern is detected, it might be proprietary
    if "all rights reserved" in normalized_content and "redistribution and use" not in normalized_content:
        return "Proprietary License (All Rights Reserved)"

    # If no match, return unknown
    return "Unknown License"
