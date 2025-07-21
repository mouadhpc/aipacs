# Middlewares personnalisés pour l'API
import time
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.gzip import GZipMiddleware
from typing import Callable

from ..config.settings import settings

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware pour le logging des requêtes"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log de la requête entrante
        logger.info(f"🔍 {request.method} {request.url.path} - Client: {request.client.host if request.client else 'Unknown'}")
        
        # Traitement de la requête
        response = await call_next(request)
        
        # Calcul du temps de traitement
        process_time = time.time() - start_time
        
        # Log de la réponse
        logger.info(f"✅ {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
        
        # Ajout du header de temps de traitement
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware pour ajouter les headers de sécurité"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Ajout des headers de sécurité
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

def setup_middleware(app: FastAPI) -> None:
    """Configuration de tous les middlewares"""
    
    # Middleware de compression GZIP
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Middleware de session (si nécessaire pour l'authentification)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        max_age=settings.access_token_expire_minutes * 60
    )
    
    # Middlewares personnalisés
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    logger.info("🔧 Middlewares configurés avec succès")
