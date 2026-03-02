import base64
#!/usr/bin/env python3

import argparse
# v0.2 signing
try:
    from core.signing import sign_detached, verify_detached, write_signature_json
except Exception:
    sign_detached = None
    verify_detached = None
    write_signature_json = None

import json
import hashlib
import sys
from datetime import datetime, timezone

CT_CANON_VERSION = "CT-CANON-v0.1"

from pathlib import Path
from typing import List, Dict, Tuple
from core.canon import canonicalize_json, CT_CANON_VERSION


def canonicalize_json(obj) -> bytes:
    """
    Deterministic JSON serialization (v0.1).
    Sorted keys, no whitespace, UTF-8.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm_sha(x: str) -> str:
    x = (x or "").strip()
    return x[7:] if x.startswith("sha256:") else x


def _load_key_bytes(path_str: str) -> bytes:
    import base64
    fp = Path(path_str)
    b = fp.read_bytes()
    if len(b) in (32, 64):
        return b
    s = b.decode('ascii', errors='ignore').strip()
    bb = base64.b64decode(s.encode('ascii'))
    if len(bb) not in (32, 64):
        raise ValueError(f'Decoded key must be 32 or 64 bytes (got {len(bb)})')
    return bb

def merkle_root_from_two(a: str, b: str) -> str:
    # a/b can be "sha256:..." or raw hex; normalize to raw hex
    return merkle_root(sorted([norm_sha(a), norm_sha(b)]))


def merkle_root(hashes: List[str]) -> str:
    """
    Deterministic Merkle root builder.
    If odd count, duplicate last hash.
    """
    if not hashes:
        raise ValueError("No hashes provided for Merkle tree.")

    layer = hashes[:]

    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])

        next_layer: List[str] = []
        for i in range(0, len(layer), 2):
            combined = (layer[i] + layer[i + 1]).encode("utf-8")
            next_layer.append(sha256_hex(combined))
        layer = next_layer

    return layer[0]


def evaluate_policy_minimal(wpo: Dict) -> Tuple[str, List[Dict]]:
    """
    Minimal v0.1 policy stub:
    Requires:
      - wpo_id (string)
      - device.device_class (string)
    """
    failures: List[Dict] = []

    if not isinstance(wpo.get("wpo_id"), str) or not wpo.get("wpo_id"):
        failures.append({
            "code": "MISSING_REQUIRED_FIELD",
            "path": "wpo_id",
            "detail": "wpo_id is required"
        })

    device = wpo.get("device", {})
    if not isinstance(device, dict) or not isinstance(device.get("device_class"), str) or not device.get("device_class"):
        failures.append({
            "code": "MISSING_REQUIRED_FIELD",
            "path": "device.device_class",
            "detail": "device.device_class is required"
        })

    if failures:
        return "NOT_CERTIFIED", failures

    return "CERTIFIED", []



def verify_mode(run_dir: str, args=None) -> int:
    """
    Minimal verify (MUST match certify exactly):
    - recompute sha256 of wpo.canonical.json and cdr.canonical.json
    - compare to wpo.sha256 and cdr.sha256
    - recompute merkle root using leaf strings INCLUDING 'sha256:' prefix
      and in the SAME ORDER as certify: [leaf_wpo, leaf_cdr] (NO sorting)
    - compare to merkle_proof.json merkle_root
    """
    run_dir = Path(run_dir)

    required = [
        "wpo.canonical.json", "wpo.sha256",
        "cdr.canonical.json", "cdr.sha256",
        "merkle_proof.json", "anchor_receipt.json",
    ]
    missing = [f for f in required if not (run_dir / f).exists()]
    if missing:
        print("VERIFY FAIL: missing files:", ", ".join(missing))
        return 2

    def read_text(fp: Path) -> str:
        return fp.read_text(encoding="utf-8").strip()

    def norm_sha(x: str) -> str:
        x = (x or "").strip()
        return x[7:] if x.startswith("sha256:") else x

    wpo_canonical = (run_dir / "wpo.canonical.json").read_bytes()
    cdr_canonical = (run_dir / "cdr.canonical.json").read_bytes()

    wpo_sha_calc = sha256_hex(wpo_canonical)
    cdr_sha_calc = sha256_hex(cdr_canonical)

    wpo_sha_file = read_text(run_dir / "wpo.sha256")
    cdr_sha_file = read_text(run_dir / "cdr.sha256")

    ok = True
    if wpo_sha_file != wpo_sha_calc:
        ok = False
        print(f"VERIFY FAIL: wpo.sha256 mismatch\n  file: {wpo_sha_file}\n  calc: {wpo_sha_calc}")
    if cdr_sha_file != cdr_sha_calc:
        ok = False
        print(f"VERIFY FAIL: cdr.sha256 mismatch\n  file: {cdr_sha_file}\n  calc: {cdr_sha_calc}")

    # === CRITICAL: match certify root computation exactly ===
    leaf_wpo = f"sha256:{wpo_sha_calc}"
    leaf_cdr = f"sha256:{cdr_sha_calc}"
    merkle_root_calc = merkle_root([leaf_wpo, leaf_cdr])  # NO SORT, includes prefix

    merkle_proof = json.loads((run_dir / "merkle_proof.json").read_text(encoding="utf-8"))
    anchor_receipt = json.loads((run_dir / "anchor_receipt.json").read_text(encoding="utf-8"))

    mp_root = norm_sha(merkle_proof.get("merkle_root", ""))
    if mp_root != merkle_root_calc:
        ok = False
        print(f"VERIFY FAIL: merkle_proof merkle_root mismatch\n  file: {mp_root}\n  calc: {merkle_root_calc}")

    # Optional: verify leaves match (handles dict or string leaves)
    leaves = merkle_proof.get("leaves", [])
    leaf_hashes = []
    if isinstance(leaves, list):
        for item in leaves:
            if isinstance(item, str):
                leaf_hashes.append((item or "").strip())
            elif isinstance(item, dict):
                h = item.get("hash") or item.get("digest") or item.get("sha256") or ""
                leaf_hashes.append((h or "").strip())

    expected = sorted([leaf_wpo, leaf_cdr])
    if leaf_hashes and sorted(leaf_hashes) != expected:
        ok = False
        print("VERIFY FAIL: merkle_proof leaves mismatch")

    # anchor_receipt merkle root optional: allow either 'merkle_root' or 'anchor_id'
    ar_candidate = anchor_receipt.get("merkle_root") or anchor_receipt.get("anchor_id") or ""
    if ar_candidate and norm_sha(ar_candidate) != merkle_root_calc:
        ok = False
        print("VERIFY FAIL: anchor_receipt merkle_root mismatch")


    # Optional: write detached signature over merkle_root (signature.json in run_dir)
    # Enabled when --sign is passed (works with --verify to sign an existing run dir).
    if getattr(args, "sign", False):
        if not sign_detached or not write_signature_json:
            ok = False
            print("SIGN FAIL: signing unavailable (core.signing not importable)")
        elif not getattr(args, "seckey", ""):
            ok = False
            print("SIGN FAIL: --seckey required for --sign")
        else:
            try:
                sig = sign_detached(merkle_root_calc.encode('utf-8'), _load_key_bytes(args.seckey))
                write_signature_json(run_dir / "signature.json", merkle_root=merkle_root_calc, signature_b64=sig.signature_b64, pubkey_b64=sig.pubkey_b64)
                print("SIGN OK: wrote", run_dir / "signature.json")
            except Exception as e:
                ok = False
                print(f"SIGN FAIL: {e}")

    # Optional: verify detached signature over merkle_root (signature.json in run_dir)
    # Enabled when --verify-signature is passed.
    if getattr(args, "verify_signature", False):
        if not verify_detached:
            ok = False
            print("VERIFY FAIL: signature verify unavailable (core.signing not importable)")
        else:
            sig_path = Path(run_dir) / "signature.json"
            if not sig_path.exists():
                ok = False
                print("VERIFY FAIL: signature.json missing")
            else:
                try:
                    sig_obj = json.loads(sig_path.read_text(encoding="utf-8"))
                    sig_b64 = sig_obj.get("signature_b64", "")
                    pub_b64 = sig_obj.get("pubkey_b64", "")
                    signed_field = sig_obj.get("signed_field", "merkle_root")
                    mr = sig_obj.get("merkle_root", "")
                    if signed_field != "merkle_root":
                        ok = False
                        print("VERIFY FAIL: signature signed_field not merkle_root")
                    elif norm_sha(mr) != merkle_root_calc:
                        ok = False
                        print("VERIFY FAIL: signature merkle_root mismatch")
                    elif not verify_detached(mr.encode('utf-8'), sig_b64, base64.b64decode(pub_b64.encode('ascii'))):
                        ok = False
                        print("VERIFY FAIL: signature invalid")
                except Exception as e:
                    ok = False
                    print(f"VERIFY FAIL: signature parse error: {e}")
    if ok:
        print("VERIFY PASS")
        print("Run dir:", run_dir)
        print("WPO:", wpo_sha_calc)
        print("CDR:", cdr_sha_calc)
        print("Merkle Root:", merkle_root_calc)
        return 0

    return 1

def main() -> int:
    parser = argparse.ArgumentParser(description="CT-Wipe v0.1 Minimal Certifier")
    parser.add_argument("--input", help="Path to WPO JSON")
    parser.add_argument("--policy", help="Policy ID (stub validation only)")
    parser.add_argument("--verify", help="Run directory to verify")
    parser.add_argument("--outdir", default="", help="Output directory (default: current working directory)")
    # Signing (v0.2)
    parser.add_argument("--sign", action="store_true",
                        help="Write Ed25519 detached signature over merkle_root")
    parser.add_argument("--seckey", default="",
                        help="Path to raw 32/64-byte Ed25519 secret key (required for --sign)")
    parser.add_argument("--pubkey", default="",
                        help="Path to raw 32-byte Ed25519 public key (used for verify)")
    parser.add_argument("--verify-signature", action="store_true",
                        help="Verify signature.json in run dir")

    args = parser.parse_args()

    if args.verify:
        return verify_mode(args.verify, args)

    if not args.input or not args.policy:
        parser.error("--input and --policy are required unless --verify is used")

    input_path = Path(args.input)

    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}")
        return 2

    try:
        wpo = json.loads(input_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: invalid JSON input: {e}")
        return 2

    
    outdir = Path(args.outdir) if args.outdir else Path(".")
    outdir.mkdir(parents=True, exist_ok=True)

# Canonicalize + hash WPO
    wpo_canonical = canonicalize_json(wpo)
    wpo_sha = sha256_hex(wpo_canonical)

    (outdir / "wpo.canonical.json").write_bytes(wpo_canonical)
    (outdir / "wpo.sha256").write_text(wpo_sha, encoding="utf-8")

    # Minimal policy evaluation
    result, failures = evaluate_policy_minimal(wpo)

    now = datetime.now(timezone.utc).isoformat()

    # Build CDR (minimal)
    cdr = {
        "cdr_version": "1.0",
        "canon": {"version": CT_CANON_VERSION},
        "object_type": "CT.CDR",
        "created_utc": now,
        "inputs": {
            "wpo_id": wpo.get("wpo_id"),
            "wpo_payload_sha256": f"sha256:{wpo_sha}",
            "policy_id": args.policy
        },
        "decision": {
            "result": result,
            "failures": failures
        }
    }

    cdr_canonical = canonicalize_json(cdr)
    cdr_sha = sha256_hex(cdr_canonical)

    (outdir / "cdr.canonical.json").write_bytes(cdr_canonical)
    (outdir / "cdr.sha256").write_text(cdr_sha, encoding="utf-8")

    # Merkle root
    leaf_wpo = f"sha256:{wpo_sha}"
    leaf_cdr = f"sha256:{cdr_sha}"
    root = merkle_root([leaf_wpo, leaf_cdr])

    merkle_proof = {
        "proof_version": "1.0",
        "merkle_root": f"sha256:{root}",
        "leaves": [
            {"artifact": "CT.WPO", "hash": leaf_wpo},
            {"artifact": "CT.CDR", "hash": leaf_cdr}
        ]
    }

    (outdir / "merkle_proof.json").write_text(json.dumps(merkle_proof, indent=2), encoding="utf-8")

    anchor_receipt = {
        "anchor_type": "LOCAL_ONLY",
        "anchor_id": f"sha256:{root}",
        "anchor_utc": now
    }

    (outdir / "anchor_receipt.json").write_text(json.dumps(anchor_receipt, indent=2), encoding="utf-8")
    # Optional: detached signature over merkle_root
    if args.sign:
        if not sign_detached or not write_signature_json:
            print("ERROR: signing unavailable (core.signing not importable)")
            return 2
        if not args.seckey:
            print("ERROR: --seckey is required with --sign")
            return 2
        seckey_path = Path(args.seckey)
        if not seckey_path.exists():
            print(f"ERROR: secret key not found: {seckey_path}")
            return 2
        key_bytes = seckey_path.read_bytes()
        merkle_root_str = f"sha256:{root}"
        sig = sign_detached(merkle_root_str.encode("utf-8"), key_bytes)
        write_signature_json(outdir / "signature.json",
                             merkle_root=merkle_root_str,
                             signature_b64=sig.signature_b64,
                             pubkey_b64=sig.pubkey_b64)
        print("Signature: signature.json")


    print("CT-Wipe v0.1 complete")
    print("Decision:", result)
    print("WPO:", leaf_wpo)
    print("CDR:", leaf_cdr)
    print("Merkle Root:", f"sha256:{root}")

    return 0 if result == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())