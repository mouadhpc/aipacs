# Router pour les endpoints AI
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging
from datetime import datetime

from ..database import get_db
from ...ai_engine.processor import AIProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

# Instance globale du processeur IA
ai_processor_instance = None

def get_ai_processor():
    """Dépendance pour obtenir l'instance du processeur IA"""
    global ai_processor_instance
    if ai_processor_instance is None:
        ai_processor_instance = AIProcessor()
    return ai_processor_instance

@router.get("/models")
async def list_models():
    """Lister les modèles IA disponibles"""
    return {
        "models": ["DemoModel v1"]
    }

@router.post("/analyze")
async def analyze_image(file_id: str, processor: AIProcessor = Depends(get_ai_processor)):
    """Analyser une image spécifique (manuel)"""
    try:
        # Simulation de l'analyse (doit être remplacée par un traitement réel)
        return {
            "status": "success",
            "file_id": file_id,
            "timestamp": datetime.now().isoformat(),
            "findings": []
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_ai_status():
    """Obtenir le statut de l'IA"""
    return {
        "status": "ready",
        "model_version": "1.0.0",
        "device": "cuda" if ai_processor_instance.device.type == "cuda" else "cpu"
    }
