from fastapi import FastAPI, APIRouter, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx

from app.api import auth, users, posters
from app.database.database import engine
from app.database import models
from app.config import settings
from app.database.models import User
from app.utils.security import get_current_user

# Инициализация базы данных
models.Base.metadata.create_all(bind=engine)

# Создание экземпляра FastAPI
app = FastAPI(
    title="Scientific Poster Generator API",
    description="Backend API for Scientific Poster Generator",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем роутер для прокси-запросов к ML-сервису
ml_proxy_router = APIRouter()

@ml_proxy_router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def ml_proxy(
    path: str, 
    request: Request, 
    current_user: User = Depends(get_current_user)
):
    """Прокси-маршрутизатор для ML-сервиса"""
    ml_service_url = settings.ML_SERVICE_URL
    target_url = f"{ml_service_url}/api/ml/{path}"
    
    # Копируем оригинальный метод, заголовки и параметры запроса
    body = await request.body()
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    
    # Добавляем ID пользователя в заголовки для авторизации в ML-сервисе
    headers["X-User-ID"] = str(current_user.id)
    
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.query_params,
            content=body,
            timeout=60.0
        )
        
        # Возвращаем ответ от ML-сервиса
        return StreamingResponse(
            content=response.aiter_bytes(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )

# Подключение всех роутеров
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(posters.router, prefix="/api", tags=["posters"])
app.include_router(ml_proxy_router, prefix="/api/ml-proxy", tags=["ml-proxy"])

# Корневой маршрут
@app.get("/", tags=["root"])
async def root():
    """Корневой маршрут API"""
    return {
        "message": "Welcome to Scientific Poster Generator API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Обработчик ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик исключений"""
    return {
        "detail": str(exc),
        "path": request.url.path
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
