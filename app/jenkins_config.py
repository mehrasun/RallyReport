# JENKINS_URL = "http://192.168.56.23:8080"
# USERNAME = "sunilmehra29"
# PASSWORD = "Suunmoon@123"
# region_map = {
# "SJC": {"view": "SJ", "folder": ["SJC", "scenarios"]},
# "DFW": {"view": "DF", "folder": ["DFW", "scenarios"]},
# "IAD": {"view": "IA", "folder": ["IAD", "scenarios"]}
# # "ORD": {"view": "OR", "folder": ["ORD"]},
# # "SYD": {"view": "SY", "folder": ["SYD"]},
# # "HKG": {"view": "HK", "folder": ["HKG"]}
# }


# ============================================================================
# settings.py
# ============================================================================
"""
Centralised runtime configuration for the Jenkins‑monitor application.

How to supply values
--------------------
All settings come from environment variables or (for REGION_MAP) an optional
JSON file.  No literals are hard‑coded except for the fallback JENKINS_URL.

  • JENKINS_URL          - optional; defaults to dev URL below.
  • JENKINS_USERNAME     - optional; if set, PASSWORD must also be set.
  • JENKINS_PASSWORD     - optional; if set, USERNAME must also be set.
  • REGION_MAP_JSON      - *required* unless REGION_MAP_FILE is provided.
  • REGION_MAP_FILE      - path to JSON file; required if REGION_MAP_JSON
                           is not supplied.

The module raises RuntimeError (or FileNotFoundError) if requirements are
not met, so configuration errors surface immediately at container startup.
"""

import json
import os
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# 1.  Jenkins connection details
# ─────────────────────────────────────────────────────────────────────────────
JENKINS_URL = os.getenv("JENKINS_URL", "http://10.22.226.66:32000")

USERNAME = os.getenv("JENKINS_USERNAME")  # may be None
PASSWORD = os.getenv("JENKINS_PASSWORD")  # may be None

# ─────────────────────────────────────────────────────────────────────────────
# 2.  Region map (must be provided via env‑var or file)
# ─────────────────────────────────────────────────────────────────────────────
if os.getenv("REGION_MAP_JSON"): # Highest priority
    REGION_MAP = json.loads(os.getenv("REGION_MAP_JSON").strip())

elif os.getenv("REGION_MAP_FILE"):                   # Fallback to file
    map_path = Path(os.getenv("REGION_MAP_FILE"))
    if not map_path.exists():
        raise FileNotFoundError(
            f"REGION_MAP_FILE set to {map_path}, but the file does not exist"
        )
    REGION_MAP = json.loads(map_path.read_text())

else:                                                # Nothing supplied → error
    raise RuntimeError(
        "Region map not provided.\n"
        "You must set exactly one of:\n"
        "  • REGION_MAP_JSON   (inline JSON string), or\n"
        "  • REGION_MAP_FILE   (path to a JSON file)"
    )

# OS_SERVICE = []
#
# if os.getenv("REGION_OS_SERVICE"):
#     try:
#         OS_SERVICE = json.loads(os.getenv("REGION_OS_SERVICE").strip())
#         if not isinstance(OS_SERVICE, list):
#             raise ValueError("REGION_OS_SERVICE must be a list")
#     except (json.JSONDecodeError, ValueError) as e:
#         raise RuntimeError(
#             f"Invalid REGION_OS_SERVICE format: {e}\n"
#             "Example of valid value: '[\"nova\", \"glance\", \"neutron\"]'"
#         )
