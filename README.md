
## Intellectual Property Notice

Certain methods and architectures related to deterministic event certification, artifact canonicalization, and independent verification may be subject to pending patent protection.

This repository provides a reference implementation of a standalone verification primitive for research, evaluation, and integration purposes only.

No rights are granted to any patent claims covering extended architectures, system compositions, or lifecycle integrations.


CT-Wipe is a standalone verification primitive designed to produce reproducible, tamper-evident certification artifacts for data sanitization events.

Most systems can perform a wipe. Very few can prove it in a deterministic, independently verifiable way.

## Why This Exists

# CT-Wipe v0.1

Deterministic cryptographic certification primitive for verifiable destruction events.

## What It Does

CT-Wipe generates tamper-evident certification artifacts for wipe events.

Verification is independent, reproducible, and fail-closed.

## Verify It Yourself (30 seconds)

```bash
git clone https://github.com/Scott-Rowland/ct-wipe-certifier
cd ct-wipe-certifier
python3 -m cli.ct_wipe_certify --verify examples/verified_run
```

## Try to Break It

Do not trust the artifact bundle by default.

Modify any value and re-run verification:

```bash
echo "tamper" >> examples/verified_run/wpo.canonical.json
python3 -m cli.ct_wipe_certify --verify examples/verified_run
```

Expected result:

VERIFY FAIL

## Deterministic Verification Primitive

CT-Wipe is not a workflow, service, or platform.

It is a minimal, standalone primitive that produces deterministic certification artifacts for a single lifecycle event: data sanitization.

For identical inputs:
- Canonical artifacts are identical
- Cryptographic hashes are identical
- Merkle roots are identical

Verification is independent and fail-closed.

No external system state is required to validate results.


## What This Is Not

CT-Wipe does not perform wipe operations.

It does not manage assets, devices, or lifecycle state.

It does not depend on external systems, registries, or orchestration layers.

It does not assume trust in the system that produced the artifact.

CT-Wipe only produces and verifies deterministic certification artifacts for a single event.


