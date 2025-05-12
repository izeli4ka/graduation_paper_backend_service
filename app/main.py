import os
from fastapi import FastAPI, APIRouter, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import httpx

from app.api import auth, users, posters, images  
from app.database.database import engine
from app.database import models
from app.database.models import User
from app.utils.security import get_current_user

# НЕ вызываем create_all в проде — миграции делаем через Alembic
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scientific Poster Generator API",
    description="Backend API for Scientific Poster Generator",
    version="1.0.0"
)

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статика для отдачи загруженных изображений
app.mount("/static", StaticFiles(directory="static"), name="static")

# Прокси к ML-сервису
ml_proxy_router = APIRouter()

@ml_proxy_router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def ml_proxy(
    path: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    ml_service_url = os.getenv("ML_SERVICE_URL", "http://localhost:8001").rstrip("/")
    target_url = f"{ml_service_url}/api/ml/{path.lstrip('/') }"
    body = await request.body()
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    headers["X-User-ID"] = str(current_user.id)

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.query_params,
            content=body,
            timeout=60.0
        )
    return StreamingResponse(
        content=resp.aiter_bytes(),
        status_code=resp.status_code,
        headers=dict(resp.headers),
    )

# Роутеры
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(posters.router, prefix="/api", tags=["posters"])
app.include_router(images.router, prefix="/api", tags=["images"])
app.include_router(ml_proxy_router, prefix="/api/ml-proxy", tags=["ml-proxy"])

@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to Scientific Poster Generator API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "path": request.url.path}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
