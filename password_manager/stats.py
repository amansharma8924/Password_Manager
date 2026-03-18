# stats.py - Dashboard ke liye statistics calculate karo

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from generator import check_strength


def calculate_stats(passwords: dict) -> dict:
    """
    Calculate the statistics of the poor password vault.
    Returns: stats dictionary with all metrics.
    """
    total = len(passwords)

    # Agar koi password nahi hai
    if total == 0:
        return {
            'total': 0,
            'weak_passwords': [],
            'duplicate_passwords': [],
            'old_passwords': [],
            'favorites_count': 0,
            'by_category': {}
        }

    # --- Weak passwords dhundho ---
    weak_passwords = []
    for service, entry in passwords.items():
        pwd = entry.get('password', '')
        score, level, _ = check_strength(pwd)
        # Medium se neeche = weak (score <= 4)
        if level in ('Very Weak', 'Weak'):
            weak_passwords.append((service, level))

    # --- Duplicate passwords dhundho ---
    # Password value ko key banao, services list ko value
    pwd_to_services: Dict[str, List[str]] = {}
    for service, entry in passwords.items():
        pwd = entry.get('password', '')
        if pwd not in pwd_to_services:
            pwd_to_services[pwd] = []
        pwd_to_services[pwd].append(service)

    # Jinke liye 2+ services hain woh duplicates hain
    duplicate_passwords = [
        services
        for pwd, services in pwd_to_services.items()
        if len(services) > 1
    ]

    # --- Old passwords dhundho (90+ din se update nahi) ---
    old_passwords = []
    cutoff_date = datetime.now() - timedelta(days=90)

    for service, entry in passwords.items():
        updated_str = entry.get('updated_at', '')
        if updated_str:
            try:
                updated_date = datetime.fromisoformat(updated_str)
                if updated_date < cutoff_date:
                    # Kitne din purana hai
                    days_old = (datetime.now() - updated_date).days
                    old_passwords.append((service, days_old))
            except ValueError:
                pass  # Invalid date format ignore karo

    # --- Favorites count ---
    favorites_count = sum(
        1 for entry in passwords.values()
        if entry.get('favorite', False)
    )

    # --- Category breakdown ---
    by_category: Dict[str, int] = {}
    for entry in passwords.values():
        cat = entry.get('category', 'other')
        by_category[cat] = by_category.get(cat, 0) + 1

    return {
        'total': total,
        'weak_passwords': weak_passwords,           # [(service, level), ...]
        'duplicate_passwords': duplicate_passwords, # [[service1, service2], ...]
        'old_passwords': old_passwords,             # [(service, days_old), ...]
        'favorites_count': favorites_count,
        'by_category': by_category                  # {'work': 3, 'personal': 5, ...}
    }
