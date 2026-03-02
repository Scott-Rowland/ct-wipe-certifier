# CT-Wipe v0.1 — VERIFY

This document specifies the third-party verification procedure for CT-Wipe v0.1 artifacts.

CT-Wipe produces deterministic, tamper-evident certification outputs that can be verified
without access to any internal system.

---

## What You Are Verifying

A verifier can confirm:

1. **File integrity**: artifact contents match their recorded SHA-256 digests
2. **Merkle integrity**: the Merkle root matches the digests of the expected leaves
3. **(Optional) Signature integrity**: an Ed25519 signature validates the Merkle root

If verification passes, the artifacts are internally consistent and have not been modified
since they were generated.

---

## What You Are NOT Verifying

CT-Wipe verification does NOT prove:

- That the device actually executed a wipe at the hardware level
- That data is unrecoverable by forensic means
- That the OS/OEM/MDM procedure was correctly performed
- That the wipe metadata is truthful

CT-Wipe verifies the **cryptographic integrity** of the recorded certification artifacts.

---

## Artifact Set (Run Directory)

A CT-Wipe run directory contains:

- `wpo.canonical.json` — canonicalized WPO payload bytes
- `wpo.sha256` — SHA-256 of `wpo.canonical.json` (hex)
- `cdr.canonical.json` — canonicalized CDR payload bytes
- `cdr.sha256` — SHA-256 of `cdr.canonical.json` (hex)
- `merkle_proof.json` — Merkle root + leaf listing
- `anchor_receipt.json` — anchor receipt (local-only in v0.1)
- `signature.json` — optional signature record (when signing enabled)

---

## Canonicalization Contract (v0.1)

CT-Wipe canonicalization is deterministic and MUST remain stable for v0.1 verification.

Rules (v0.1):

- JSON keys are sorted (`sort_keys=true`)
- No whitespace (`separators=(",", ":")`)
- UTF-8 encoding
- `ensure_ascii=false`

**Important:** If canonicalization rules change, previously generated hashes will not match.
For that reason, canonicalization is versioned and treated as a freeze contract.

---

## Merkle Root Contract (v0.1)

CT-Wipe computes a deterministic Merkle root over two leaves:

- `leaf_wpo = "sha256:" + <wpo_sha256_hex>`
- `leaf_cdr = "sha256:" + <cdr_sha256_hex>`

Root computation rules (v0.1):

- Leaves are provided in this exact order: `[leaf_wpo, leaf_cdr]`
- Each pair is concatenated as UTF-8 string bytes and hashed with SHA-256
- If an odd node count occurs at any layer, duplicate the last element

This contract MUST match between generation and verification.

---

## Verification Using the CT-Wipe CLI

From the project root:

### Verify a run directory

```bash
python3 -m cli.ct_wipe_certify --verify out/run_TIMESTAMP