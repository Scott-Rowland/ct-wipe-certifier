#!/usr/bin/env bash
set -euo pipefail

# Demo run for CT-Wipe v0.1
# - creates a fresh out/demo_run_tmp
# - certifies sample WPO
# - verifies hashes + merkle root
# - optionally signs + verifies signature if cryptography is available

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUTDIR="out/demo_run_tmp"
rm -rf "$OUTDIR"
mkdir -p "$OUTDIR"

python3 -m cli.ct_wipe_certify \
  --input examples/sample_wpo.json \
  --policy CT-WIPE-T1-CRYPTO-ERASE \
  --outdir "$OUTDIR"

python3 -m cli.ct_wipe_certify --verify "$OUTDIR"

# optional signing (only if cryptography import works)
if python3 -c "import cryptography" >/dev/null 2>&1; then
  python3 - <<'PY'
import os, base64
from pathlib import Path
Path("out/demo_run_tmp/seckey.demo.b64").write_text(base64.b64encode(os.urandom(32)).decode("ascii") + "\n")
print("WROTE out/demo_run_tmp/seckey.demo.b64 (demo key)")
PY

  python3 -m cli.ct_wipe_certify --verify "$OUTDIR" --sign --seckey "$OUTDIR/seckey.demo.b64"
  python3 -m cli.ct_wipe_certify --verify "$OUTDIR" --verify-signature

  # delete demo key after use
  rm -f "$OUTDIR/seckey.demo.b64"
else
  echo "NOTE: cryptography not installed; skipping sign/verify-signature demo."
fi

echo
echo "DEMO COMPLETE -> $OUTDIR"
