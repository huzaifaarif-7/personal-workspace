"""Symmetric token encryption using Fernet (from the `cryptography` package).

All OAuth access and refresh tokens are stored encrypted in the database.
This module provides the two functions the rest of the codebase uses:

    from server.crypto import encrypt_token, decrypt_token

    ciphertext = encrypt_token(raw_access_token)   # store this in the DB
    plaintext  = decrypt_token(ciphertext)          # use this to call APIs

Key management
--------------
The encryption key MUST be set via the TOKEN_ENCRYPTION_KEY environment
variable.  Generate a valid Fernet key once and store it in .env:

    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

This module raises RuntimeError at import time if the key is absent — it
NEVER falls back to a default or generated key.  A missing key in production
means an immediate startup failure, which is far safer than silently storing
tokens under an ephemeral key (you would lose all stored tokens on restart).

Security notes
--------------
- Fernet guarantees authenticated encryption (AES-128-CBC + HMAC-SHA256).
- The key must be exactly 32 url-safe base64-encoded bytes (Fernet.generate_key() format).
- Rotate the key by decrypting all tokens with the old key and re-encrypting
  with the new one before swapping TOKEN_ENCRYPTION_KEY.
"""
import os

from cryptography.fernet import Fernet, InvalidToken

# ---------------------------------------------------------------------------
# Key loading — hard-fail if missing
# ---------------------------------------------------------------------------

_raw_key = os.environ.get("TOKEN_ENCRYPTION_KEY")
if not _raw_key:
    raise RuntimeError(
        "TOKEN_ENCRYPTION_KEY environment variable is not set.\n"
        "Generate a key with:\n"
        "  python -c \"from cryptography.fernet import Fernet; "
        "print(Fernet.generate_key().decode())\"\n"
        "Then add TOKEN_ENCRYPTION_KEY=<key> to your .env file."
    )

try:
    _fernet = Fernet(_raw_key.encode())
except Exception as exc:
    raise RuntimeError(
        f"TOKEN_ENCRYPTION_KEY is set but is not a valid Fernet key: {exc}\n"
        "Regenerate it with:\n"
        "  python -c \"from cryptography.fernet import Fernet; "
        "print(Fernet.generate_key().decode())\""
    ) from exc


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def encrypt_token(plain: str) -> str:
    """Encrypt a plaintext token string and return a base64 ciphertext string.

    The returned value is safe to store in a TEXT database column.
    It is URL-safe base64 and contains no newlines.

    Args:
        plain: The raw OAuth token (access_token or refresh_token).

    Returns:
        A Fernet-encrypted, base64-encoded string.

    Raises:
        TypeError: If `plain` is not a string.
    """
    if not isinstance(plain, str):
        raise TypeError(f"encrypt_token expects str, got {type(plain).__name__}")
    return _fernet.encrypt(plain.encode()).decode()


def decrypt_token(token: str) -> str:
    """Decrypt a previously encrypted token string.

    Args:
        token: The ciphertext produced by encrypt_token().

    Returns:
        The original plaintext token.

    Raises:
        cryptography.fernet.InvalidToken: If the ciphertext is tampered with,
            the key is wrong, or the token has expired (Fernet supports TTLs).
        TypeError: If `token` is not a string.
    """
    if not isinstance(token, str):
        raise TypeError(f"decrypt_token expects str, got {type(token).__name__}")
    try:
        return _fernet.decrypt(token.encode()).decode()
    except InvalidToken:
        # Re-raise with a slightly more informative message while preserving
        # the original exception type so callers can catch InvalidToken.
        raise InvalidToken(
            "Token decryption failed — the ciphertext may be corrupted, "
            "the encryption key may have changed, or the token has expired."
        )
