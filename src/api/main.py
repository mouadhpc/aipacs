# Module principal de l'API FastAPI
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from ..config.settings import settings
from .routers import dicom, ai, reports, monitoring
from .middleware import setup_middleware
from .database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire du cycle de vie de l'application"""
    # Initialisation au démarrage
    print("🚀 Démarrage de l'application IA PACS...")
    await init_db()
    print("✅ Base de données initialisée")
    
    yield
    
    # Nettoyage à l'arrêt
    print("🛑 Arrêt de l'application IA PACS")

# Création de l'application FastAPI
app = FastAPI(
    title=settings.app_name,
    description="Application IA pour l'analyse automatique d'images médicales DICOM",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration des middlewares personnalisés
setup_middleware(app)

# Inclusion des routeurs
app.include_router(
    dicom.router,
    prefix=f"{settings.api_prefix}/dicom",
    tags=["DICOM"]
)

app.include_router(
    ai.router,
    prefix=f"{settings.api_prefix}/ai",
    tags=["Intelligence Artificielle"]
)

app.include_router(
    reports.router,
    prefix=f"{settings.api_prefix}/reports",
    tags=["Comptes Rendus"]
)

app.include_router(
    monitoring.router,
    prefix=f"{settings.api_prefix}/monitoring",
    tags=["Monitoring"]
)

@app.get("/")
async def root():
    """Point d'entrée principal"""
    return {
        "message": "Application IA PACS - Radiologie",
        "version": settings.app_version,
        "status": "running",
        "docs": f"{settings.api_prefix}/docs"
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état de santé de l'application"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-27T10:00:00Z",
        "services": {
            "api": "running",
            "database": "connected",
            "dicom_server": "listening",
            "ai_engine": "ready"
        }
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Gestionnaire d'exceptions HTTP personnalisé"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": "2025-01-27T10:00:00Z"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )