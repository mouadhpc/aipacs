# Gestion de la base de données
import asyncio
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from ..config.settings import settings

logger = logging.getLogger(__name__)

# Configuration des engines
sync_engine = create_engine(settings.database_url, echo=settings.debug)

# Pour PostgreSQL async, on utilise asyncpg
async_database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(async_database_url, echo=settings.debug)

# Sessions
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Initialisation de la base de données"""
    try:
        logger.info("Initialisation de la base de données...")
        
        # Test de connexion
        async with async_engine.begin() as conn:
            # Vérification de la connexion
            result = await conn.execute(text("SELECT 1"))
            logger.info("✅ Connexion à la base de données établie")
        
        # En production, on utiliserait Alembic pour les migrations
        logger.info("Base de données initialisée avec succès")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
        raise

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Générateur de session de base de données"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def check_db_health() -> bool:
    """Vérification de l'état de la base de données"""
    try:
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Erreur de santé de la base de données: {e}")
        return False
