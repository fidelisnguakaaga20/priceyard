import bcrypt

BCRYPT_ROUNDS = 12
BCRYPT_MAX_PASSWORD_BYTES = 72


def _password_bytes(password: str) -> bytes:
    value = password.encode("utf-8")
    if not value:
        raise ValueError("Password cannot be empty")
    if len(value) > BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError("Password is too long")
    return value


def hash_password(password: str) -> str:
    """Hash a password with bcrypt without silently truncating long input."""
    return bcrypt.hashpw(
        _password_bytes(password),
        bcrypt.gensalt(rounds=BCRYPT_ROUNDS),
    ).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_password_bytes(password), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False
