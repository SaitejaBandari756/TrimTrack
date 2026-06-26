"""
Base62 Encoding / Decoding
━━━━━━━━━━━━━━━━━━━━━━━━━━
Encodes integers to compact URL-safe strings and back.

Character set: 0-9, a-z, A-Z (62 characters)
Example: 1000 → "g8"
"""

CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(CHARSET)


def encode(number: int) -> str:
    """
    Encode an integer to a Base62 string.

    Args:
        number: Non-negative integer to encode

    Returns:
        Base62-encoded string (minimum 1 character)

    Raises:
        ValueError: if number is negative
    """
    if number < 0:
        raise ValueError("Cannot encode negative numbers")
    if number == 0:
        return CHARSET[0]

    chars = []
    while number > 0:
        chars.append(CHARSET[number % BASE])
        number //= BASE

    return "".join(reversed(chars))


def decode(encoded: str) -> int:
    """
    Decode a Base62 string back to an integer.

    Args:
        encoded: Base62-encoded string

    Returns:
        Decoded integer

    Raises:
        ValueError: if string contains invalid characters
    """
    number = 0
    for char in encoded:
        idx = CHARSET.find(char)
        if idx == -1:
            raise ValueError(f"Invalid Base62 character: '{char}'")
        number = number * BASE + idx
    return number
