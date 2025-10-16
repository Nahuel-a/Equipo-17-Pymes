from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64


def generar_par_claves(key_size: int = 2048):
    """Genera un par de claves RSA y devuelve (private_pem, public_pem) como bytes."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size, backend=default_backend())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def firmar_documento(documento_contenido: str, private_pem: bytes) -> str:
    """Firma el texto usando la clave privada en PEM y devuelve la firma en base64."""
    private_key = serialization.load_pem_private_key(private_pem, password=None, backend=default_backend())
    signature = private_key.sign(
        documento_contenido.encode("utf-8"),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")


def verificar_firma(documento_contenido: str, firma_b64: str, public_pem: bytes) -> bool:
    """Verifica que la firma (base64) es válida para el contenido y la clave pública PEM."""
    try:
        public_key = serialization.load_pem_public_key(public_pem, backend=default_backend())
        public_key.verify(
            base64.b64decode(firma_b64),
            documento_contenido.encode("utf-8"),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False
"""Utilities for signing and verifying documents using RSA.

This module provides three helpers used by the digital-signature
router and tests:
- generar_par_claves: generate an RSA keypair and return PEM bytes
- firmar_documento: sign a string with a private PEM and return base64
- verificar_firma: verify a base64 signature using public PEM

Note: keys are generated in-memory for demo/tests. Do not use this
pattern for production key management.
"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64
from typing import Tuple


def generar_par_claves(key_size: int = 2048) -> Tuple[bytes, bytes]:
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


def firmar_documento(contenido: str, private_pem: bytes) -> str:
    """Sign the given string using the provided private PEM and return base64 signature."""
    private_key = serialization.load_pem_private_key(private_pem, password=None, backend=default_backend())
    signature = private_key.sign(
        contenido.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")


def verificar_firma(contenido: str, firma_b64: str, public_pem: bytes) -> bool:
    """Verify a base64 signature for the given content using public PEM.

    Returns True if signature is valid, False otherwise.
    """
    public_key = serialization.load_pem_public_key(public_pem, backend=default_backend())
    try:
        public_key.verify(
            base64.b64decode(firma_b64),
            contenido.encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False
