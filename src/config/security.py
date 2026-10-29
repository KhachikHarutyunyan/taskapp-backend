from datetime import timedelta
from uuid import UUID

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext

from src.api.utils.constants import SPECIAL_CHARACTERS
from src.api.utils.dates_util import get_utc_date
from src.config.logs import logger
from src.config.settings import settings

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_token_payload(token: str, secret: str):
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
        return {"is_expire": False, "payload": payload}
    except ExpiredSignatureError:
        logger.warning("JWT token expired")
        unverified = jwt.get_unverified_claims(token)
        return {"is_expire": True, "payload": unverified}
    except Exception as jwt_exec:
        logger.warning(f"Get token payload fail Exception: {str(jwt_exec)}")
        return {"is_expire": True, "payload": None}


def generate_token(user_id: str, expiry: timedelta, secret: str):
    payload = {"sub": str(user_id)}
    expire = get_utc_date() + expiry
    payload.update({"exp": expire})
    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def create_tokens(user_id: UUID) -> tuple[str, str]:
    """Generate both tokens"""
    access_token = generate_token(
        str(user_id),
        timedelta(minutes=settings.JWT_ACCESS_EXPIRE),
        settings.JWT_ACCESS_SECRET_KEY,
    )

    refresh_token = generate_token(
        str(user_id),
        timedelta(minutes=settings.JWT_REFRESH_EXPIRE),
        settings.JWT_REFRESH_SECRET_KEY,
    )
    return access_token, refresh_token


def is_password_strong_enough(password: str) -> bool:
    if not any(char.isupper() for char in password):
        return False

    if not any(char.islower() for char in password):
        return False

    if not any(char.isdigit() for char in password):
        return False

    if not any(char in SPECIAL_CHARACTERS for char in password):
        return False

    return True
