from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError,
    InvalidHashError,
)
from argon2.profiles import RFC_9106_LOW_MEMORY


ph = PasswordHasher.from_parameters(RFC_9106_LOW_MEMORY)


def hash(password: str) -> str:
    """
    Generates a secure hash from a password.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The password hash.
    """
    return ph.hash(password)


def verify(plain_password: str, hashed_password: str) -> tuple[bool, bool]:
    """
    Checks if a password matches a stored hash.

    Args:
        plain_password (str): The password provided by the user.
        hash_password (str): The hash of the password stored in the database.

    Returns:
        bool: True if the password matches, false otherwise.
    """
    try:
        match = ph.verify(hashed_password, plain_password)
        needs_rehash = ph.check_needs_rehash(hashed_password)
        return match, needs_rehash

    except VerifyMismatchError:
        return False, False

    except (InvalidHashError, VerificationError):
        # hash corrupto, incompatible o malformado
        return False, False
