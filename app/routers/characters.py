from fastapi import APIRouter, Query

from app.models import Character
from app.services.characters import get_popular_characters, search_characters

router = APIRouter()


@router.get("/characters/popular", response_model=list[Character])
def popular():
    return get_popular_characters()


@router.get("/characters/search", response_model=list[Character])
def search(q: str = Query(..., min_length=1)):
    return search_characters(q)
