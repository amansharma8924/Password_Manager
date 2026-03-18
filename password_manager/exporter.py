# exporter.py - Passwords ko alag formats mein export karo

import csv
import shutil
from datetime import datetime
from storage import DATA_FILE


def export_to_txt(passwords: dict, filename: str = "export.txt") -> str:
    """
    Export all passwords to a readable plain text file.
    WARNING: This file WILL NOT BE ENCRYPTED!
    Returns: saved filename.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        # Header aur warning likho
        f.write("=" * 60 + "\n")
        f.write("       PASSWORD MANAGER - PLAIN TEXT EXPORT\n")
        f.write("=" * 60 + "\n")
        f.write("⚠️ WARNING: THIS FILE IS NOT ENCRYPTED!\n")
        f.write("       Safely store this file or delete it.\n")
        f.write(f"       Export time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        if not passwords:
            f.write("No password is saved.\n")
        else:
            # Har entry likh o
            for i, (service, entry) in enumerate(passwords.items(), 1):
                f.write(f"[{i}] Service  : {service}\n")
                f.write(f"    Username : {entry.get('username', 'N/A')}\n")
                f.write(f"    Password : {entry.get('password', 'N/A')}\n")
                f.write(f"    Category : {entry.get('category', 'N/A')}\n")
                f.write(f"    Tags     : {', '.join(entry.get('tags', []))}\n")
                f.write(f"    Notes    : {entry.get('notes', 'N/A')}\n")
                f.write(f"    Favorite : {'⭐ Yes' if entry.get('favorite') else 'No'}\n")
                f.write(f"    Created  : {entry.get('created_at', 'N/A')}\n")
                f.write(f"    Updated  : {entry.get('updated_at', 'N/A')}\n")
                f.write("-" * 40 + "\n")

        f.write(f"\nTotal: {len(passwords)} passwords\n")

    return filename


def export_to_csv(passwords: dict, filename: str = "export.csv") -> str:
    """
   Export passwords to a CSV file (it will open in Excel).
    Returns: saved filename.
    """
    fieldnames = ['service', 'username', 'password', 'notes', 'category', 'tags', 'favorite', 'created_at', 'updated_at']

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()  # Column headers

        for service, entry in passwords.items():

            # Tags ko comma-separated string banao

            tags_str = ', '.join(entry.get('tags', []))
            writer.writerow({
                'service': service,
                'username': entry.get('username', ''),
                'password': entry.get('password', ''),
                'notes': entry.get('notes', ''),
                'category': entry.get('category', 'other'),
                'tags': tags_str,
                'favorite': 'Yes' if entry.get('favorite') else 'No',
                'created_at': entry.get('created_at', ''),
                'updated_at': entry.get('updated_at', ''),
            })

    return filename


def export_encrypted_backup() -> str:
    """
    Make a backup of the current encrypted file (.enc) with a timestamp.
    This file will remain encrypted — the safest option.
    Returns: backup filename.
    """
    import os
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError("No passwords.enc file found!")

    # Date aur time se unique backup naam

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}.enc"

    # Simply copy karo (encryption intact rahegi)
    
    shutil.copy2(DATA_FILE, backup_name)
    return backup_name
