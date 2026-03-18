# importer.py - CSV file se passwords import karo

import csv
import os
from datetime import datetime
from typing import Tuple, List


def import_from_csv(filepath: str, passwords: dict) -> Tuple[int, int, List[str]]:
    """
    Import passwords from a CSV file into the existing vault.
    CSV columns: service, username, password, notes, category, tags
    
    Returns: (imported_count, skipped_count, errors_list)
    """
    imported = 0
    skipped = 0
    errors = []

    # File exist karti hai?

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:

            # CSV reader - headers automatically detect karo

            reader = csv.DictReader(f)

            # Required column check

            if reader.fieldnames is None:
                raise ValueError("The CSV file is empty or does not have headers!")

            # Lowercase mein convert karo comparison ke liye

            headers_lower = [h.lower().strip() for h in reader.fieldnames]
            if 'service' not in headers_lower:
                raise ValueError("The 'service' column must be present in the CSV!")

            for row_num, row in enumerate(reader, start=2):  # Row 2 se (1 = header)
                try:
                    # Service name (required field)
                    service = row.get('service', '').strip()
                    if not service:
                        errors.append(f"Row {row_num}: The service name is empty, skipped")
                        skipped += 1
                        continue

                    # Agar already exist karta hai toh skip
                    if service in passwords:
                        errors.append(f"Row {row_num}: '{service}' already exists, skipped")
                        skipped += 1
                        continue

                    # Tags ko list mein convert karo
                    tags_str = row.get('tags', '')
                    tags = [t.strip() for t in tags_str.split(',') if t.strip()]

                    # Category validate karo
                    valid_categories = ['work', 'personal', 'social', 'banking', 'email', 'other']
                    category = row.get('category', 'other').strip().lower()
                    if category not in valid_categories:
                        category = 'other'  # Invalid category = other

                    # Entry banao
                    now = datetime.now().isoformat()
                    passwords[service] = {
                        'username': row.get('username', '').strip(),
                        'password': row.get('password', '').strip(),
                        'notes': row.get('notes', '').strip(),
                        'category': category,
                        'tags': tags,
                        'favorite': False,
                        'created_at': now,
                        'updated_at': now,
                        'last_used': '',
                        'history': []  # Import mein history empty rahegi
                    }
                    imported += 1

                except Exception as e:
                    errors.append(f"Row {row_num}: Error - {str(e)}")
                    skipped += 1

    except UnicodeDecodeError:
        raise ValueError("File encoding error! Save in UTF-8 format.")

    return imported, skipped, errors
