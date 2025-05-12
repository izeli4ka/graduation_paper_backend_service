from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.database.models import Poster, User
from app.schemas.poster import PosterCreate, PosterUpdate, PosterResponse
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/posters/", response_model=PosterResponse, status_code=status.HTTP_201_CREATED)
def create_poster(
    poster: PosterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_poster = Poster(**poster.dict(), owner_id=current_user.id)
    db.add(db_poster)
    db.commit()
    db.refresh(db_poster)
    return db_poster


@router.get("/posters/", response_model=List[PosterResponse])
def read_posters(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    posters = (
        db.query(Poster)
        .filter(Poster.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return posters


@router.get("/posters/{poster_id}", response_model=PosterResponse)
def read_poster(
    poster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    poster = (
        db.query(Poster)
        .filter(Poster.id == poster_id, Poster.owner_id == current_user.id)
        .first()
    )
    if poster is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poster not found")
    return poster


@router.put("/posters/{poster_id}", response_model=PosterResponse)
def update_poster(
    poster_id: int,
    poster_update: PosterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_poster = (
        db.query(Poster)
        .filter(Poster.id == poster_id, Poster.owner_id == current_user.id)
        .first()
    )
    if db_poster is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poster not found")

    update_data = poster_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_poster, key, value)

    db.commit()
    db.refresh(db_poster)
    return db_poster


@router.delete("/posters/{poster_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poster(
    poster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    poster = (
        db.query(Poster)
        .filter(Poster.id == poster_id, Poster.owner_id == current_user.id)
        .first()
    )
    if poster is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poster not found")
    db.delete(poster)
    db.commit()
    return None
