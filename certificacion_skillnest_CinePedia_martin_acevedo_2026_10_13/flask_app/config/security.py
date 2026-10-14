import hashlib
import hmac
import secrets


def hash_password(password):
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 120000
    ).hex()
    return f"{salt}${password_hash}"


def check_password(password, saved_password):
    try:
        salt, expected_hash = saved_password.split("$", 1)
    except ValueError:
        return False
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 120000
    ).hex()
    return hmac.compare_digest(password_hash, expected_hash)
