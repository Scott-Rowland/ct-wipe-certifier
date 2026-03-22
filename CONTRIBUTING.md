# Contributing to CT-Wipe

Thank you for your interest in improving CT-Wipe.

CT-Wipe is a deterministic cryptographic certification primitive focused on producing
verifiable destruction event certification artifacts.

## Development Principles

Contributions MUST NOT introduce external dependencies, system-level assumptions, or non-deterministic behavior.

Contributions should preserve the following properties:

- deterministic outputs
- canonical serialization
- reproducible verification
- minimal trusted components

Artifact structure, canonicalization rules, and verification semantics are considered part of the verification contract and MUST remain stable within v0.1.  

Changes that alter artifact formats or verification semantics MUST include explicit documentation and versioning considerations.

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with a clear description

Please include:

- purpose of the change
- security implications
- reproducibility considerations

## Security Issues

Security vulnerabilities should **not** be reported through public issues.

Please follow the process described in `SECURITY.md`.
