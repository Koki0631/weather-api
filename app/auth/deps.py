from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.auth.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise _CREDENTIALS_EXCEPTION
        return int(sub)
    except (JWTError, ValueError, TypeError):
        raise _CREDENTIALS_EXCEPTION from None
