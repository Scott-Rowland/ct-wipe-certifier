# CT-Wipe v0.1

Deterministic cryptographic wipe certification primitive.

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
