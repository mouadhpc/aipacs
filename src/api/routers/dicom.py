# Router pour les endpoints DICOM
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import logging
from datetime import datetime

from ..database import get_db
from ...dicom_handler.server import DICOMServer
from ...config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Instance globale du serveur DICOM
dicom_server_instance = None

def get_dicom_server():
    """Dépendance pour obtenir l'instance du serveur DICOM"""
    global dicom_server_instance
    if dicom_server_instance is None:
        dicom_server_instance = DICOMServer()
    return dicom_server_instance

@router.get("/status")
async def get_dicom_status(server: DICOMServer = Depends(get_dicom_server)):
    """Obtenir le statut du serveur DICOM"""
    try:
        return {
            "status": "running",
            "ae_title": settings.dicom_ae_title,
            "port": settings.dicom_port,
            "host": settings.dicom_host,
            "pacs_target": {
                "ae_title": settings.pacs_ae_title,
                "host": settings.pacs_host,
                "port": settings.pacs_port
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut DICOM: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connections")
async def get_dicom_connections():
    """Obtenir la liste des connexions DICOM actives"""
    return {
        "active_connections": 0,
        "total_connections_today": 0,
        "last_connection": None,
        "supported_sop_classes": [
            "CT Image Storage",
            "MR Image Storage",
            "Digital X-Ray Image Storage",
            "Digital Mammography X-Ray Image Storage"
        ]
    }

@router.post("/test-connection")
async def test_pacs_connection():
    """Tester la connexion au PACS interne"""
    try:
        # Simulation du test de connexion
        # En production, on ferait un vrai C-ECHO vers le PACS
        return {
            "status": "success",
            "pacs_host": settings.pacs_host,
            "pacs_port": settings.pacs_port,
            "pacs_ae_title": settings.pacs_ae_title,
            "response_time_ms": 125,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur lors du test de connexion PACS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/received-studies")
async def get_received_studies(limit: int = 10, offset: int = 0):
    """Obtenir la liste des études reçues récemment"""
    try:
        # En production, cette liste viendrait de la base de données
        return {
            "studies": [
                {
                    "study_uid": "1.2.3.4.5.6.7.8.9.10",
                    "patient_id": "PATIENT001",
                    "patient_name": "DOE^JOHN",
                    "modality": "CT",
                    "study_date": "20250121",
                    "study_time": "143000",
                    "received_at": "2025-01-21T14:30:15Z",
                    "processed": True,
                    "ai_analysis_status": "completed"
                }
            ],
            "total": 1,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des études: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_dicom_statistics():
    """Obtenir les statistiques DICOM"""
    return {
        "today": {
            "studies_received": 0,
            "images_processed": 0,
            "reports_generated": 0
        },
        "this_week": {
            "studies_received": 0,
            "images_processed": 0,
            "reports_generated": 0
        },
        "this_month": {
            "studies_received": 0,
            "images_processed": 0,
            "reports_generated": 0
        },
        "by_modality": {
            "CT": 0,
            "MR": 0,
            "CR": 0,
            "DX": 0,
            "MG": 0
        }
    }
