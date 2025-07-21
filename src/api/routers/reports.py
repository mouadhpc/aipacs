# Router pour les endpoints des rapports
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging
from datetime import datetime

from ..database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def list_reports(limit: int = 10, offset: int = 0):
    """Lister les rapports générés"""
    try:
        # En production, cette liste viendrait de la base de données
        return {
            "reports": [
                {
                    "id": 1,
                    "study_uid": "1.2.3.4.5.6.7.8.9.10",
                    "patient_id": "PATIENT001",
                    "report_type": "DICOM_SR",
                    "generated_at": "2025-01-21T14:35:00Z",
                    "sent_to_pacs": True,
                    "findings_count": 1,
                    "confidence": 0.85
                }
            ],
            "total": 1,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des rapports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_id}")
async def get_report(report_id: int):
    """Obtenir un rapport spécifique"""
    try:
        # En production, le rapport serait récupéré de la base de données
        return {
            "id": report_id,
            "study_uid": "1.2.3.4.5.6.7.8.9.10",
            "patient_id": "PATIENT001",
            "patient_name": "DOE^JOHN",
            "modality": "CT",
            "report_type": "DICOM_SR",
            "generated_at": "2025-01-21T14:35:00Z",
            "sent_to_pacs": True,
            "findings": [
                {
                    "type": "nodule_pulmonaire",
                    "confidence": 0.85,
                    "location": [100, 150, 25, 25],
                    "description": "Nodule pulmonaire suspect détecté",
                    "severity": "medium",
                    "measurements": {
                        "diameter_mm": 12.5,
                        "volume_mm3": 817.5
                    }
                }
            ],
            "summary": "Nodule pulmonaire détecté nécessitant un suivi",
            "conclusion": "Évaluation par un radiologue recommandée"
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du rapport {report_id}: {e}")
        raise HTTPException(status_code=404, detail="Rapport non trouvé")

@router.post("/{report_id}/resend")
async def resend_report(report_id: int):
    """Renvoyer un rapport vers le PACS"""
    try:
        # En production, cette action renverrait réellement le rapport
        return {
            "status": "success",
            "report_id": report_id,
            "sent_at": datetime.now().isoformat(),
            "pacs_response": "Report sent successfully"
        }
    except Exception as e:
        logger.error(f"Erreur lors du renvoi du rapport {report_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/summary")
async def get_report_statistics():
    """Obtenir les statistiques des rapports"""
    return {
        "total_reports": 0,
        "today": {
            "generated": 0,
            "sent_to_pacs": 0,
            "with_findings": 0
        },
        "this_week": {
            "generated": 0,
            "sent_to_pacs": 0,
            "with_findings": 0
        },
        "by_modality": {
            "CT": 0,
            "MR": 0,
            "CR": 0,
            "DX": 0,
            "MG": 0
        },
        "by_severity": {
            "high": 0,
            "medium": 0,
            "low": 0
        }
    }
