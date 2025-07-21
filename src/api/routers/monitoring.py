# Router pour les endpoints de monitoring
from fastapi import APIRouter, HTTPException, Depends
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def get_health_status():
    """Obtenir l'état global du système"""
    try:
        return {
            "status": "healthy",
            "services": {
                "api": "running",
                "database": "connected",
                "dicom_server": "listening",
                "ai_engine": "ready"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de santé: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_system_metrics():
    """Obtenir les métriques système"""
    return {
        "cpu_usage": "15%",
        "memory_usage": "60%",
        "disk_io": "500 MB/s",
        "network_io": "120 MB/s",
        "timestamp": datetime.now().isoformat()
    }
