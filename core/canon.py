"""
CT Canonicalization Contract
Version: CT-CANON-v0.1

Rules:
- JSON serialization: sort_keys=True
- separators=(",", ":")  (no whitespace)
- ensure_ascii=False (UTF-8, do not escape unicode)
- Output bytes are UTF-8 encoded
"""

from __future__ import annotations
import json
from typing import Any

CT_CANON_VERSION = "CT-CANON-v0.1"

def canonicalize_json(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
