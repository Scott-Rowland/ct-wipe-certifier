# CT-Wipe v0.1 — VERIFY

This document specifies the third-party verification procedure for CT-Wipe v0.1 artifacts.

CT-Wipe produces deterministic, tamper-evident certification artifacts that can be independently verified without access to the originating system.

---

## What You Are Verifying

A verifier can confirm:

1. File integrity: artifact contents match their recorded SHA-256 digests  
2. Merkle integrity: the Merkle root matches the digests of the expected leaves  
3. (Optional) Signature integrity: an Ed25519 signature validates the Merkle root  

If verification passes, the artifacts are internally consistent and match their recorded cryptographic digests.
No claim is made about the truthfulness of the recorded event.

---

## What You Are NOT Verifying

CT-Wipe verification does NOT prove:

- That the device actually executed a wipe at the hardware level  
- That data is unrecoverable by forensic means  
- That the OS/OEM/MDM procedure was correctly performed  
- That the wipe metadata is truthful  

CT-Wipe verifies the cryptographic integrity of the recorded certification artifacts.

---

## Independent Verification

Verification does not require the CT-Wipe implementation. Verification MUST be reproducible by any independent implementation that follows the canonicalization and hashing rules.

Any independent implementation that follows the canonicalization and hashing rules can reproduce the same results.

---

## Artifact Set (Run Directory)

A CT-Wipe run directory contains:

- wpo.canonical.json — canonicalized WPO payload bytes  
- wpo.sha256 — SHA-256 of wpo.canonical.json (hex)  
- cdr.canonical.json — canonicalized CDR payload bytes  
- cdr.sha256 — SHA-256 of cdr.canonical.json (hex)  
- merkle_proof.json — Merkle root + leaf listing  
- anchor_receipt.json — anchor receipt (local-only in v0.1)  
- signature.json — optional signature record (when signing enabled)  

---

## Canonicalization Contract (v0.1)

Canonicalization MUST be deterministic and byte-for-byte reproducible.

CT-Wipe canonicalization is deterministic and MUST remain stable for v0.1 verification.

Rules:

- JSON keys sorted  
- No whitespace  
- UTF-8 encoding  
- ensure_ascii=false  

This is a versioned verification contract.

---

## Merkle Root Contract (v0.1)

Leaves:

- leaf_wpo = "sha256:" + <wpo_sha256_hex>  
- leaf_cdr = "sha256:" + <cdr_sha256_hex>  

Rules:

- Order: [leaf_wpo, leaf_cdr]  
- Concatenate as UTF-8 → hash with SHA-256  
- If the number of nodes is odd, duplicate the final node.
  
---

## Verification Example (Reference CLI)

```bash
python3 -m cli.ct_wipe_certify --verify examples/verified_run
