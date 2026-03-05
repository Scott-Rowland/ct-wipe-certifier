# CT-Wipe v0.1  

## Design Principle

CT-Wipe is implemented as a **deterministic verification primitive**, not a wipe utility.
The system does not perform device wiping.  

Instead it produces **cryptographically verifiable state-transition artifacts** that allow independent systems or auditors to prove that a wipe event occurred and was recorded without tampering.
Deterministic Cryptographic Wipe Certification

CT-Wipe is a command-line tool that produces tamper-evident,
deterministic certification artifacts for device wipe and cryptographic erase events.

It generates reproducible hash-linked records and optional Ed25519 signatures
that can be independently verified.

---

## What Problem This Solves

Most device wipe processes produce logs — not cryptographic proof.

CT-Wipe provides:

- Deterministic canonicalization of wipe metadata
- SHA-256 artifact hashing
- Merkle root anchoring
- Optional Ed25519 signature
- Reproducible verification

The same input produces identical certification artifacts.

---

## Quick Demo

Generate a certification run:

```bash
RUN="out/run_$(date -u +%Y%m%dT%H%M%SZ)"

python3 -m cli.ct_wipe_certify \
  --input examples/sample_wpo.json \
  --policy CT-WIPE-T1-CRYPTO-ERASE \
  --outdir "$RUN"
```

Verify artifacts:

```bash
python3 -m cli.ct_wipe_certify --verify "$RUN"
```

Sign artifacts (optional):

```bash
python3 -m cli.ct_wipe_certify \
  --verify "$RUN" \
  --sign \
  --seckey seckey.b64
```

Verify signature:

```bash
python3 -m cli.ct_wipe_certify \
  --verify "$RUN" \
  --verify-signature
```

---

## Output Structure

Each run produces:

```
out/run_TIMESTAMP/
├── wpo.json
├── cdr.json
├── merkle.json
└── signature.json   (optional)
```

Where:

- **WPO** — Wipe Proof Object  
- **CDR** — Certification Digest Record  
- **Merkle Root** — Deterministic root hash over artifacts  
- **Signature** — Ed25519 signature over Merkle root  

---

## Deterministic Guarantee

For identical input:

- WPO hash is identical  
- CDR hash is identical  
- Merkle root is identical  

Verification recomputes all hashes and validates integrity.

---

## Security Model

CT-Wipe certifies the integrity of reported wipe metadata.

It does **not**:

- Verify physical data destruction
- Guarantee hardware-level erase execution
- Replace forensic validation

It provides cryptographic integrity over the recorded event.

---

## Technical Details

- Canonical JSON serialization
- SHA-256 hashing
- Deterministic Merkle root construction
- Ed25519 signatures
- CLI-based reproducibility

---

## Status

Version: v0.1  
Stability: Demo-ready  
License: TBD  

---

## Roadmap (Non-binding)

- Timestamp authority integration
- Transparency log anchoring
- Centralized verification service
- Enterprise policy layers
