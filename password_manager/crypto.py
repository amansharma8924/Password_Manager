# crypto.py - Encryption aur Decryption ka poora kaam yahan hota hai

import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Fixed salt - same salt = same key for same master password
SALT = b'PM_SALT_2024_SECURE_FIXED_KEY_01'


def derive_key(master_password: str) -> bytes:
    """
    Create a 256-bit Fernet key from the master password using PBKDF2HMAC.
    Same password = always produces the saem key (deterministic).
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),   # SHA256 hashing algorithm
        length=32,                   # 32 bytes = 256-bit key
        salt=SALT,                   # Fixed salt use kar rahe hain
        iterations=100000,           # 100k iterations = brute force slow ho jaata hai
    )
    # Password encode karo -> key derive karo -> base64 encode karo (Fernet format)
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode('utf-8')))
    return key


def encrypt_data(plaintext: str, master_password: str) -> bytes:
    """
    Encrypt the plain text string with Fernet.
    Returns: encrypted bytes which will be saved in the file.
    """
    key = derive_key(master_password)                      # Step 1: Key banao
    fernet = Fernet(key)                                   # Step 2: Fernet object banao
    encrypted = fernet.encrypt(plaintext.encode('utf-8'))  # Step 3: Encrypt karo
    return encrypted


def decrypt_data(encrypted_bytes: bytes, master_password: str) -> str:
    """
    Decrypt the encrypted bytes.
    Raises a ValueError on wrong password.
    Returns: decrypted plain text string.
    """
    key = derive_key(master_password)
    fernet = Fernet(key)
    try:
        decrypted = fernet.decrypt(encrypted_bytes)  # Decrypt attempt
        return decrypted.decode('utf-8')             # Bytes se string banao
    except InvalidToken:
        raise ValueError("Wrong master password or corrupted file!")
