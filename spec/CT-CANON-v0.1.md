# CT-CANON-v0.1 — Canonical JSON Contract (Freeze)

## Scope
This contract defines the one and only canonical byte representation used for hashing CT objects
(e.g., WPO, CDR, proofs). Any change requires bumping the version (CT-CANON-v0.2, etc.).

## Canonicalization Rules (MUST)
1) Input is a JSON value (object/array/string/number/bool/null).
2) Serialization MUST be UTF-8 encoded bytes.
3) Objects MUST be serialized with keys sorted lexicographically by Unicode code point.
4) Serialization MUST use no extra whitespace:
   - separators MUST be exactly: comma ',' and colon ':' (no spaces).
5) Strings MUST be JSON-escaped per RFC 8259. (Python json.dumps default escaping is acceptable.)
6) ensure_ascii MUST be false (Unicode preserved, not \\uXXXX escaped by default).
7) The resulting canonical bytes are hashed with SHA-256; digest is lowercase hex.

## Prohibitions (MUST NOT)
- MUST NOT pretty-print.
- MUST NOT reorder arrays.
- MUST NOT coerce numeric types (e.g., 1 vs 1.0 must remain as parsed).
- MUST NOT change Unicode normalization of string values.
- MUST NOT change newline conventions (no trailing newline added).

## Output Formats
- sha256 file stores lowercase hex only (no prefix).
- leaf strings in Merkle are formatted as: "sha256:<lowercase hex>"

## Versioning
- Objects MAY include a field referencing this version (e.g., "canon_version": "CT-CANON-v0.1").
- If canonicalization changes, the version MUST be bumped and all downstream hashes change.
