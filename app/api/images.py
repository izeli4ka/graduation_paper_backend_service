from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Poster, Image, User
from app.schemas.image import ImageResponse
from app.utils.security import get_current_user
import shutil
import os

router = APIRouter()

@router.post("/posters/{poster_id}/images", response_model=ImageResponse)
async def upload_image(
    poster_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверяем владельца
    poster = db.query(Poster).filter_by(id=poster_id, owner_id=current_user.id).first()
    if not poster:
        raise HTTPException(status_code=404, detail="Poster not found")

    # Сохраняем файл
    upload_dir = "static/images"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Сохраняем запись в БД
    image = Image(
        filename=file.filename,
        url=f"/static/images/{file.filename}",
        poster=poster
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image
