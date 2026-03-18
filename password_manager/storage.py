# storage.py - Passwords ko encrypted file mein save aur load karna

import json
import os
import shutil
from datetime import datetime
from typing import Optional
from crypto import encrypt_data, decrypt_data

# Default file jahan sab passwords encrypted store honge
DATA_FILE = "passwords.enc"


def load_passwords(master_password: str) -> Optional[dict]:
    """
    Load passwords from the encrypted file.
    Returns: dict of passwords, {} if file does not exist, None if password is wrong.
    """
    # Agar file hi nahi hai (pehli baar) toh empty dict do
    if not os.path.exists(DATA_FILE):
        return {}

    # File read karo binary mode mein
    with open(DATA_FILE, "rb") as f:
        encrypted_bytes = f.read()

    # Agar file empty hai
    if not encrypted_bytes:
        return {}

    try:
        # Decrypt karo aur JSON parse karo
        decrypted_str = decrypt_data(encrypted_bytes, master_password)
        return json.loads(decrypted_str)
    except ValueError:
        # Galat master password
        return None
    except json.JSONDecodeError:
        # File corrupted hai
        return None


def save_passwords(passwords: dict, master_password: str) -> bool:
    """
    Make the passwords dictionary into JSON, encrypt it, write it to a file.
    Returns: True on success, False on failure.
    """
    try:
        # Dictionary ko JSON string banao (pretty format)
        json_str = json.dumps(passwords, indent=2, ensure_ascii=False)
        # Encrypt karo
        encrypted = encrypt_data(json_str, master_password)
        # Binary mode mein file mein likho
        with open(DATA_FILE, "wb") as f:
            f.write(encrypted)
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False


def create_encrypted_backup(master_password: str) -> str:
    """
    Make a backup of the current encrypted file with the date in the filename.
    Returns: backup filename.
    """
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError("No data file was found for backup!")

    # Backup filename mein aaj ki date daalo
    today = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{today}.enc"

    # Simply encrypted file copy karo (already encrypted hai)
    shutil.copy2(DATA_FILE, backup_name)
    return backup_name


def file_exists() -> bool:
    """Check whether the password file exists or not (check for the first time)."""
    return os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0
