from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64

# # Generate keys (do this once per customer or securely)
# private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
# public_key = private_key.public_key()

def firmar_documento(documento_contenido):
    signature = private_key.sign(
        documento_contenido.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')  #Encode for storage

def verificar_firma(documento_contenido, firma, public_key):
    try:
        public_key.verify(
            base64.b64decode(firma),
            documento_contenido.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True  # Valid signature
    except:
        return False  # Invalid signature