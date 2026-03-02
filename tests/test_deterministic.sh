#!/usr/bin/env bash
set -e

RUN="out/run_test_$(date -u +%Y%m%dT%H%M%SZ)"

python3 cli/ct_wipe_certify.py \
  --input examples/sample_wpo.json \
  --policy CT-WIPE-T1-CRYPTO-ERASE \
  --outdir "$RUN"

python3 cli/ct_wipe_certify.py --verify "$RUN"

echo "Deterministic test PASSED"
