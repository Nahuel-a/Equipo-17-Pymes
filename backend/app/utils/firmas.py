
"""Utilities for signing and verifying documents using RSA.

This module provides three helpers used by the digital-signature
router and tests:
- generate_key_pair: generate an RSA keypair and return PEM bytes
- sign_document: sign a string with a private PEM and return base64
- verify_signature: verify a base64 signature using public PEM

Note: keys are generated in-memory for demo/tests. Do not use this
pattern for production key management.
"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64
from typing import Tuple


def generate_key_pair(key_size: int = 2048) -> Tuple[bytes, bytes]:
    """Generate an RSA key pair and return (private_pem, public_pem).

    Returns:
        (private_pem, public_pem) as bytes in PEM format.
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size, backend=default_backend())
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def sign_document(content: str, private_pem: bytes) -> str:
    """Sign the given string using the provided private PEM and return base64 signature."""
    private_key = serialization.load_pem_private_key(private_pem, password=None, backend=default_backend())
    signature = private_key.sign(
        content.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")


def verify_signature(content: str, signature_b64: str, public_pem: bytes) -> bool:
    """Verify a base64 signature for the given content using public PEM.

    Returns True if signature is valid, False otherwise.
    """
    public_key = serialization.load_pem_public_key(public_pem, backend=default_backend())
    try:
        public_key.verify_signature(
            base64.b64decode(signature_b64),
            content.encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False
