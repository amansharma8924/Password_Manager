# generator.py - Password generate karo aur strength check karo

import random
import string
from typing import Tuple, List


def generate_password(
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True
) -> str:
    """
    Generate a strong random password with custom options.
    length: between 8 and 64
    Returns: generated password string.
    """
    # Length validate karo

    length = max(8, min(64, length))

    # Character pool banao user choices se

    pool = ""
    guaranteed = []  # Har category se at least 1 char zaroor

    if use_lower:
        pool += string.ascii_lowercase
        guaranteed.append(random.choice(string.ascii_lowercase))

    if use_upper:
        pool += string.ascii_uppercase
        guaranteed.append(random.choice(string.ascii_uppercase))

    if use_digits:
        pool += string.digits
        guaranteed.append(random.choice(string.digits))

    if use_symbols:
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        pool += symbols
        guaranteed.append(random.choice(symbols))

    # Agar koi option nahi chuna toh default lowercase use karo

    if not pool:
        pool = string.ascii_lowercase
        guaranteed = [random.choice(pool)]

    # Baki characters random pool se bharo
    remaining_length = length - len(guaranteed)
    rest = [random.choice(pool) for _ in range(remaining_length)]

    # Sab combine karo aur shuffle karo (pattern na bane)
    all_chars = guaranteed + rest
    random.shuffle(all_chars)

    return ''.join(all_chars)


def check_strength(password: str) -> Tuple[int, str, List[str]]:
    """
    Check the password strength on a 0-10 scale.
    Returns: (score, level_label, suggestions_list)
    Levels: Very Weak, Weak, Medium, Strong, Very Strong
    """
    score = 0
    suggestions = []

    # --- Length checks ---
    if len(password) >= 8:
        score += 1
    else:
        suggestions.append("Use at least 8 characters")

    if len(password) >= 12:
        score += 1
    else:
        suggestions.append("12+ characters is even better")

    if len(password) >= 16:
        score += 1

    if len(password) >= 20:
        score += 1

    # --- Character type checks ---
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    if has_lower:
        score += 1
    else:
        suggestions.append("Add lowercase letters (a-z)")

    if has_upper:
        score += 1
    else:
        suggestions.append("Add Uppercase letters (A-Z)")

    if has_digit:
        score += 1
    else:
        suggestions.append("Add Numbers (0-9)")

    if has_symbol:
        score += 1
    else:
        suggestions.append("Add Special symbols (!@#$)")

    # --- Pattern checks (negative) ---
    # Common patterns check

    common = ['password', '123456', 'qwerty', 'abc123', 'admin', 'letmein']
    if any(c in password.lower() for c in common):
        score -= 2
        suggestions.append("Avoid common words/patterns")

    # Repeating characters check (jaise: aaaa, 1111)

    if len(set(password)) < len(password) * 0.5:
        score -= 1
        suggestions.append("Don't use too many repeating characters")

    # Score 0 se kam na ho

    score = max(0, score)

    # Score ke hisaab se level decide karo

    if score <= 2:
        level = "Very Weak"
    elif score <= 4:
        level = "Weak"
    elif score <= 6:
        level = "Medium"
    elif score <= 8:
        level = "Strong"
    else:
        level = "Very Strong"

    return score, level, suggestions


def get_strength_color(level: str) -> str:
    """
    Return the color of the strength level for the rich library.
    """
    colors = {
        "Very Weak": "red",
        "Weak": "orange3",
        "Medium": "yellow",
        "Strong": "green",
        "Very Strong": "bright_green"
    }
    return colors.get(level, "white")
