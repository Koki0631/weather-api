from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.deps import get_current_user
from app.dependencies import get_favorites_service
from app.schemas import FavoriteCreateRequest, FavoriteItem, FavoriteListResponse
from app.services.favorites import (
    DatabaseUnavailableError,
    FavoriteNotFoundError,
    FavoritesService,
)

router = APIRouter(tags=["favorites"])


@router.post("/favorites", response_model=FavoriteItem)
async def add_favorite(
    body: FavoriteCreateRequest,
    user_id: int = Depends(get_current_user),
    service: FavoritesService = Depends(get_favorites_service),
) -> FavoriteItem:
    try:
        return service.add_favorite(user_id=user_id, city=body.city)
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/favorites", response_model=FavoriteListResponse)
async def list_favorites(
    user_id: int = Depends(get_current_user),
    service: FavoritesService = Depends(get_favorites_service),
) -> FavoriteListResponse:
    try:
        return service.list_favorites(user_id=user_id)
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.delete("/favorites/{city}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    city: str,
    user_id: int = Depends(get_current_user),
    service: FavoritesService = Depends(get_favorites_service),
) -> None:
    try:
        service.remove_favorite(user_id=user_id, city=city)
    except FavoriteNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
