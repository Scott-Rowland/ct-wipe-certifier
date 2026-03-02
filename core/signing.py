import base64
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Minimal Ed25519 signing via cryptography (preferred).
# If cryptography isn't installed, we'll handle that at runtime in the CLI.

SIG_VERSION = "CT-SIG-v0.1"

@dataclass
class SigResult:
    signature_b64: str
    pubkey_b64: str

def _b64(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")

def _b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))

def load_pubkey_b64(path: Path) -> str:
    # expects raw 32-byte public key file
    b = path.read_bytes()
    if len(b) != 32:
        raise ValueError(f"pubkey must be 32 bytes (got {len(b)})")
    return _b64(b)

def load_seckey_b64(path: Path) -> str:
    # expects raw 32-byte seed OR 64-byte private key. We'll accept 32 as seed.
    b = path.read_bytes()
    if len(b) not in (32, 64):
        raise ValueError(f"seckey must be 32 or 64 bytes (got {len(b)})")
    return _b64(b)

def sign_detached(message: bytes, seckey_raw: bytes) -> SigResult:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    # If seed (32), derive private key. If 64, treat first 32 as seed.
    seed = seckey_raw[:32]
    sk = Ed25519PrivateKey.from_private_bytes(seed)
    pk = sk.public_key()
    sig = sk.sign(message)

    # Export pubkey raw (32 bytes)
    from cryptography.hazmat.primitives import serialization
    pk_raw = pk.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return SigResult(signature_b64=_b64(sig), pubkey_b64=_b64(pk_raw))

def verify_detached(message: bytes, signature_b64: str, pubkey_raw: bytes) -> bool:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    pk = Ed25519PublicKey.from_public_bytes(pubkey_raw)
    sig = _b64d(signature_b64)
    try:
        pk.verify(sig, message)
        return True
    except Exception:
        return False

def write_signature_json(out_path: Path, *, merkle_root: str, signature_b64: str, pubkey_b64: str) -> None:
    obj = {
        "sig_version": SIG_VERSION,
        "object_type": "CT.SIGNATURE",
        "signing_alg": "ed25519",
        "signed_field": "merkle_root",
        "merkle_root": merkle_root,
        "signature_b64": signature_b64,
        "pubkey_b64": pubkey_b64,
    }
    out_path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
