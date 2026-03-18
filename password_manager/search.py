# search.py - Passwords ko search, filter aur sort karne ka logic

from typing import Dict, List, Tuple


def search_passwords(
    passwords: dict,
    query: str
) -> List[Tuple[str, dict]]:
    """
    Search for the query in service name, username, or notes (case-insensitive partial match).
    Returns: list of (service_name, entry_dict) tuples.
    """
    query = query.lower().strip()  # Case-insensitive ke liye lowercase
    results = []

    for service, entry in passwords.items():
        # Teen jagah dhundho: service name, username, notes
        service_match = query in service.lower()
        username_match = query in entry.get('username', '').lower()
        notes_match = query in entry.get('notes', '').lower()
        tags_match = query in ' '.join(entry.get('tags', [])).lower()

        # Koi bhi match mile toh result mein add karo
        if service_match or username_match or notes_match or tags_match:
            results.append((service, entry))

    return results


def filter_by_category(
    passwords: dict,
    category: str
) -> List[Tuple[str, dict]]:
    """
    Return all passwords of a specific category.
    category: work, personal, social, banking, email, other
    """
    category = category.lower().strip()
    results = []

    for service, entry in passwords.items():
        # Entry ki category match karo
        if entry.get('category', 'other').lower() == category:
            results.append((service, entry))

    return results


def filter_favorites(passwords: dict) -> List[Tuple[str, dict]]:
    """
    Return only favorite marked passwords.
    """
    return [
        (service, entry)
        for service, entry in passwords.items()
        if entry.get('favorite', False)  # favorite = True wale
    ]


def sort_entries(
    entries: List[Tuple[str, dict]],
    sort_by: str = 'name'
) -> List[Tuple[str, dict]]:
    """
    Sort the password entries.
    sort_by options: 'name', 'created', 'last_used'
    """
    if sort_by == 'name':
        # A-Z alphabetical order by service name
        return sorted(entries, key=lambda x: x[0].lower())

    elif sort_by == 'created':
        # Naye pehle (descending)
        return sorted(
            entries,
            key=lambda x: x[1].get('created_at', ''),
            reverse=True
        )

    elif sort_by == 'last_used':
        # Haal mein use kiye gaye pehle
        return sorted(
            entries,
            key=lambda x: x[1].get('last_used', ''),
            reverse=True
        )

    # Default: naam se sort
    return sorted(entries, key=lambda x: x[0].lower())


def get_all_entries(passwords: dict) -> List[Tuple[str, dict]]:
    """SNow return the passwords in a list of tuples."""
    return list(passwords.items())
