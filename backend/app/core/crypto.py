"""Fernet-based symmetric encryption helpers for sensitive values (e.g. API keys).

The Fernet key is derived deterministically from settings.secret_key so that
tokens survive application restarts as long as the secret hasn't changed.
"""

import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import settings


def _fernet() -> Fernet:
    """Build a Fernet instance whose key is derived from the app secret."""
    raw = hashlib.sha256(settings.secret_key.encode()).digest()
    key = base64.urlsafe_b64encode(raw)
    return Fernet(key)


def encrypt(plaintext: str) -> str:
    """Encrypt *plaintext* and return a URL-safe base64 token string."""
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt(token: str) -> str:
    """Decrypt a token previously produced by :func:`encrypt`."""
    return _fernet().decrypt(token.encode()).decode()
