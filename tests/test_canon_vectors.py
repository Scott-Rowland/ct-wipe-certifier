import hashlib
from core.canon import canonicalize_json, CT_CANON_VERSION

VECTOR = {
  "z": 2,
  "a": {"b": 1, "A": 2},
  "arr": [3, {"k": "v"}, "µ"],
  "s": "line\nbreak",
  "n": 1,
  "f": 1.0,
  "t": True,
  "null": None
}

EXPECTED_SHA256 = "34c9670d7d44a552f714a6fb5f96456cc2689b2cb2e9a627f5ccf802cfc5fc4d"

def test_canon_v0_1_vector():
    assert CT_CANON_VERSION == "CT-CANON-v0.1"
    got = hashlib.sha256(canonicalize_json(VECTOR)).hexdigest()
    assert got == EXPECTED_SHA256
