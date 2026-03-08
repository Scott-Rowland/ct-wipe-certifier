# CT-Wipe v0.1  

![CI](https://github.com/Scott-Rowland/ct-wipe-certifier/actions/workflows/python-app.yml/badge.svg)

Deterministic certification primitive for cryptographic proof of device wipe and erase state transitions.

CT-Wipe is a deterministic **state-transition certification primitive** specialized for device wipe and cryptographic erase lifecycle events.

Category: **verification infrastructure / cryptographic provenance**

---

## Why CT-Wipe Exists

Many infrastructure systems destroy data or retire hardware, but most environments
cannot produce **cryptographically verifiable evidence** that these destructive
operations actually occurred.

Traditional wipe tools generate logs. Logs can be altered.

CT-Wipe instead produces **deterministic cryptographic certification artifacts**
that allow independent systems or auditors to verify that a sanitization event
was recorded without tampering.

---

### Design Principle

CT-Wipe is implemented as a **deterministic verification primitive**, not a wipe utility.
The system does not perform device wiping.  

Instead it produces **cryptographically verifiable state-transition artifacts** that allow independent systems or auditors to prove that a wipe event occurred and was recorded without tampering.

---

## Problems CT-Wipe Helps Solve

Engineers and security teams often need deterministic proof that a data sanitization event occurred.

CT-Wipe can help when answering questions such as:

- How can we **prove a device wipe occurred** after decommissioning hardware?
- How can we generate **tamper-evident wipe logs** that auditors can verify independently?
- How can we produce **cryptographic proof of data sanitization** for compliance workflows?
- How can infrastructure pipelines create **deterministic verification artifacts** for destructive lifecycle events?
- How can security teams validate that a **crypto-erase or wipe operation was recorded without modification**?

CT-Wipe addresses these needs by generating deterministic certification artifacts that can be independently verified using cryptographic hashing and optional signatures.

---

## Design Goals

CT-Wipe is designed to provide a minimal, deterministic primitive for producing verifiable state-transition artifacts.

The design prioritizes:

- Deterministic cryptographic artifact generation  
- Independent verification by third parties  
- Reproducible outputs from identical inputs  
- Compatibility with automated infrastructure workflows  
- Minimal trusted components

---

## Use Cases

CT-Wipe is a **deterministic certification primitive** designed for systems that must prove that a destructive or sanitization event occurred.  
It generates cryptographically verifiable artifacts that can be independently validated during audits, investigations, or compliance reviews.

Typical applications include:

### Enterprise Device Decommissioning
Organizations regularly retire laptops, servers, storage devices, and mobile hardware that previously contained sensitive data.  
CT-Wipe artifacts can be generated during the wipe process to produce a **verifiable certification record** showing that the sanitization event occurred and was recorded without tampering.

### Data Center Server Lifecycle
Large data centers frequently decommission and replace servers and storage infrastructure.  

CT-Wipe enables deterministic certification artifacts when systems transition from:

```
active infrastructure
→ decommissioned
→ sanitized
```

These artifacts allow operators or auditors to later verify the wipe event independently.

### IT Asset Disposition (ITAD)
IT asset disposition providers process large volumes of enterprise hardware for resale, recycling, or destruction.  

CT-Wipe artifacts provide a **machine-verifiable wipe certification layer** that can accompany asset transfer records or compliance documentation.

### Compliance and Audit Evidence
Regulatory frameworks often require proof that sensitive storage media was sanitized.  

CT-Wipe produces artifacts suitable for inclusion in audit workflows where independent verification of wipe events is required.

### Security and Incident Response
In security investigations, teams may need to demonstrate that devices or storage media were properly wiped after containing sensitive or compromised data.  

Deterministic certification artifacts make it possible to verify that the wipe record itself has not been altered.

---

### Important Design Principle

CT-Wipe **does not perform device wiping**.

It is a **verification primitive** that generates deterministic certification artifacts describing wipe events performed by external tools or systems.

---

## Non-Goals

CT-Wipe is intentionally minimal and focused. The following capabilities are **explicitly outside the scope** of this primitive.

### Performing Device Wipes
CT-Wipe does **not** execute data erasure or sanitization operations.  
It certifies wipe events performed by external tools or systems.

### Hardware Control
CT-Wipe does not interact with storage devices, firmware, operating systems, or hardware controllers.

### Policy Enforcement
CT-Wipe does not enforce organizational wipe policies or compliance frameworks.  
Policy decisions should be handled by upstream systems or orchestration layers.

### Asset Lifecycle Management
CT-Wipe does not manage inventory, ownership records, or device lifecycle tracking.

### Chain-of-Custody Systems
CT-Wipe does not attempt to replace full asset tracking or logistics platforms.  
It produces deterministic artifacts that may be incorporated into those systems.

### Identity or Authorization Management
CT-Wipe does not provide identity management, authentication services, or access control mechanisms.

---

CT-Wipe is designed as a **small, deterministic certification primitive** that can integrate into larger systems without introducing operational dependencies.

---

## Relationship to Other Primitives

CT-Wipe is designed as a **standalone verification primitive** focused on certification of wipe and sanitization events.

Within broader lifecycle systems, CT-Wipe represents a specific type of **state-transition certification**: the transition of a storage device or asset from a state containing data to a verified sanitized state.

The primitive is intentionally minimal so it can operate independently or be composed with other lifecycle primitives.

In larger architectures, similar primitives may exist for other lifecycle events such as:

```
event declaration
custody transfer
state transition verification
destruction certification
```

CT-Wipe focuses exclusively on the **sanitization transition** and the deterministic generation of verifiable certification artifacts for that event.

This separation allows CT-Wipe to remain:

- deterministic  
- composable  
- infrastructure-friendly  
- usable across multiple operational domains

without introducing dependencies on broader asset management or lifecycle systems.

---

### Deterministic Cryptographic Wipe Certification

CT-Wipe is a command-line tool that produces tamper-evident,
deterministic certification artifacts for device wipe and cryptographic erase events.

It generates reproducible hash-linked records and optional Ed25519 signatures
that can be independently verified.

### Example Automation Pipeline

CT-Wipe is designed to operate as a verification primitive within automated lifecycle workflows.

```

Device / Asset
↓
Wipe or Crypto-Erase Operation
↓
CT-Wipe Certification Artifact
↓
Hash / Merkle Root Anchoring
↓
Independent Verification (audit, compliance, or automation systems)

```

### What Problem This Solves

Most device wipe processes produce logs — not cryptographic proof.

CT-Wipe provides:

- Deterministic canonicalization of wipe metadata
- SHA-256 artifact hashing
- Merkle root anchoring
- Optional Ed25519 signature
- Reproducible verification

The same input produces identical certification artifacts.

---

## Intellectual Property Notice

Certain methods and architectures related to CT-Wipe are subject to patent filings.

Patent Status: **Patent Pending**

This repository provides a reference implementation of the CT-Wipe deterministic verification primitive for research, evaluation, and integration purposes.

Use of this repository does not grant rights to any patent claims that may exist now or in the future covering related architectures or extended capabilities.

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

## Repository Structure

cli/        command-line interface  
core/       core certification and verification logic  
examples/   sample inputs and example artifacts  
registry/   registry alignment and related metadata  
schemas/    artifact schemas  
scripts/    helper scripts and demo workflows  
spec/       design notes and specifications  
tests/      deterministic and verification tests

---

### Verify a Certification Artifact

After generating a certification artifact, it can be independently verified.

```bash 
python3 -m cli.ct_wipe_certify --verify artifact.json

```

Expected output:

```
artifact hash: verified
merkle root: verified
signature: valid
```

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
