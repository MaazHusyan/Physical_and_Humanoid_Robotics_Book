from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta
from app.core.config import settings
import secrets
import hashlib

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def verify_access_token(token: str) -> dict:
    """Verify and decode an access token, returning the payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except InvalidTokenError:
        raise InvalidTokenError("Could not validate credentials")

def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def cleanup_expired_tokens(db):
    """
    Remove expired and revoked refresh tokens from the database.
    This function should be called periodically as a background task.
    """
    from sqlalchemy import delete
    from app.models.user import RefreshToken
    from datetime import datetime

    # Delete expired or revoked tokens
    stmt = delete(RefreshToken).where(
        (RefreshToken.expires_at < datetime.utcnow()) |
        (RefreshToken.revoked == True)
    )

    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount  # Return number of deleted tokens