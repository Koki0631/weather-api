from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_auth_service
from app.schemas import LoginRequest, TokenResponse
from app.services.auth import (
    AuthService,
    DatabaseUnavailableError,
    InvalidCredentialsError,
)

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        access_token = service.login(email=body.email, password=body.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return TokenResponse(access_token=access_token, token_type="bearer")
