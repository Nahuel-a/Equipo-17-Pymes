import secrets
import time
from typing import Dict, Tuple


class PasswordResetManager:
    """
    Manages password reset codes and their validation.
    Uses in-memory storage with expiry times for reset codes.
    """
    # Dictionary to store reset codes: {email: (code, expiry_timestamp)}
    _reset_codes: Dict[str, Tuple[str, float]] = {}
    
    # Code expiry time in seconds (default 15 minutes)
    CODE_EXPIRY = 15 * 60
    
    @classmethod
    def generate_reset_code(cls, email: str) -> str:
        """
        Generates a 6-digit reset code for the given email and stores it with expiry time.
        
        Args:
            email: The email address to generate a code for
            
        Returns:
            str: The generated reset code
        """
        # Generate a random 6-digit code
        code = str(secrets.randbelow(1000000)).zfill(6)
        
        # Store the code with its expiry timestamp
        expiry = time.time() + cls.CODE_EXPIRY
        cls._reset_codes[email] = (code, expiry)
        
        return code
    
    @classmethod
    def verify_reset_code(cls, email: str, code: str) -> bool:
        """
        Verifies if the provided code for the email is valid and not expired.
        
        Args:
            email: The email address
            code: The reset code to verify
            
        Returns:
            bool: True if the code is valid and not expired, False otherwise
        """
        if email not in cls._reset_codes:
            return False
            
        stored_code, expiry = cls._reset_codes[email]
        
        # Check if the code is correct and not expired
        if stored_code == code and time.time() < expiry:
            return True
            
        # If expired, remove the code
        if time.time() >= expiry:
            cls._reset_codes.pop(email, None)
            
        return False
    
    @classmethod
    def clear_reset_code(cls, email: str) -> None:
        """
        Clears the reset code for an email after successful use.
        
        Args:
            email: The email address to clear the code for
        """
        cls._reset_codes.pop(email, None)


# Function to use in API endpoints
async def generate_password_reset_code(email: str) -> str:
    """
    Generate a password reset code for a user.
    
    Args:
        email: The email address of the user
        
    Returns:
        str: The generated reset code
    """
    return PasswordResetManager.generate_reset_code(email)


async def verify_password_reset_code(email: str, code: str) -> bool:
    """
    Verify a password reset code.
    
    Args:
        email: The email address of the user
        code: The reset code to verify
        
    Returns:
        bool: True if the code is valid, False otherwise
    """
    return PasswordResetManager.verify_reset_code(email, code)


async def clear_password_reset_code(email: str) -> None:
    """
    Clear a password reset code after successful use.
    
    Args:
        email: The email address of the user
    """
    PasswordResetManager.clear_reset_code(email)