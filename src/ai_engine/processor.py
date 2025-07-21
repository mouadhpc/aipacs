# Processeur IA pour l'analyse des images médicales
import asyncio
import logging
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import pydicom
from pydicom.dataset import Dataset
import cv2
from skimage import measure, morphology
import monai.transforms as transforms
from monai.data import MetaTensor

from ..config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class Finding:
    """Représentation d'une anomalie détectée"""
    type: str  # Type d'anomalie (nodule, fracture, etc.)
    confidence: float  # Score de confiance (0-1)
    location: Tuple[int, int, int, int]  # Coordonnées (x, y, width, height)
    description: str  # Description textuelle
    severity: str  # Sévérité (low, medium, high)
    measurements: Optional[Dict] = None  # Mesures (taille, volume, etc.)

@dataclass
class AIResults:
    """Résultats de l'analyse IA"""
    study_uid: str
    series_uid: str
    instance_uid: str
    modality: str
    findings: List[Finding]
    overall_confidence: float
    processing_time: float
    model_version: str
    timestamp: str

class AIProcessor:
    """Processeur principal pour l'analyse IA des images médicales"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.transforms = self._setup_transforms()
        self.model_version = "1.0.0"
        
        logger.info(f"Processeur IA initialisé sur: {self.device}")
        
    def _setup_transforms(self):
        """Configuration des transformations d'images"""
        return transforms.Compose([
            transforms.LoadImage(image_only=True),
            transforms.EnsureChannelFirst(),
            transforms.Orientation(axcodes="RAS"),
            transforms.Spacing(pixdim=(1.0, 1.0, 1.0), mode="bilinear"),
            transforms.ScaleIntensityRange(
                a_min=-1000, a_max=1000, b_min=0.0, b_max=1.0, clip=True
            ),
            transforms.Resize(spatial_size=(512, 512, -1)),
            transforms.ToTensor()
        ])
    
    async def load_model(self, model_path: Optional[str] = None):
        """Chargement du modèle IA"""
        try:
            model_path = model_path or settings.ai_model_path
            
            if not Path(model_path).exists():
                logger.warning(f"Modèle non trouvé: {model_path}. Utilisation du modèle de démonstration.")
                self.model = self._create_demo_model()
            else:
                self.model = torch.load(model_path, map_location=self.device)
                logger.info(f"Modèle chargé depuis: {model_path}")
            
            self.model.eval()
            self.model.to(self.device)
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            self.model = self._create_demo_model()
    
    def _create_demo_model(self):
        """Création d'un modèle de démonstration simple"""
        logger.info("Création d'un modèle de démonstration")
        
        class DemoModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = torch.nn.Conv2d(1, 16, 3, padding=1)
                self.conv2 = torch.nn.Conv2d(16, 32, 3, padding=1)
                self.pool = torch.nn.AdaptiveAvgPool2d((1, 1))
                self.fc = torch.nn.Linear(32, 2)  # Normal vs Anomalie
                
            def forward(self, x):
                x = torch.relu(self.conv1(x))
                x = torch.relu(self.conv2(x))
                x = self.pool(x)
                x = x.view(x.size(0), -1)
                x = torch.sigmoid(self.fc(x))
                return x
        
        return DemoModel()
    
    async def analyze_image(self, image_path: Path, dicom_ds: Dataset) -> Optional[AIResults]:
        """Analyse principale d'une image DICOM"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Chargement du modèle si nécessaire
            if self.model is None:
                await self.load_model()
            
            logger.info(f"Début de l'analyse IA pour: {image_path}")
            
            # Préparation de l'image
            image_tensor = await self._prepare_image(image_path, dicom_ds)
            
            if image_tensor is None:
                logger.error("Impossible de préparer l'image pour l'analyse")
                return None
            
            # Analyse selon la modalité
            modality = dicom_ds.get('Modality', 'Unknown')
            findings = await self._analyze_by_modality(image_tensor, modality, dicom_ds)
            
            # Calcul du temps de traitement
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Calcul de la confiance globale
            overall_confidence = self._calculate_overall_confidence(findings)
            
            # Création des résultats
            results = AIResults(
                study_uid=dicom_ds.get('StudyInstanceUID', ''),
                series_uid=dicom_ds.get('SeriesInstanceUID', ''),
                instance_uid=dicom_ds.get('SOPInstanceUID', ''),
                modality=modality,
                findings=findings,
                overall_confidence=overall_confidence,
                processing_time=processing_time,
                model_version=self.model_version,
                timestamp="2025-01-27T10:00:00Z"
            )
            
            logger.info(f"Analyse terminée en {processing_time:.2f}s. {len(findings)} anomalies détectées.")
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse IA: {e}")
            return None
    
    async def _prepare_image(self, image_path: Path, dicom_ds: Dataset) -> Optional[torch.Tensor]:
        """Préparation de l'image pour l'analyse"""
        try:
            # Lecture de l'image DICOM
            ds = pydicom.dcmread(image_path)
            pixel_array = ds.pixel_array
            
            # Normalisation selon la modalité
            modality = ds.get('Modality', 'Unknown')
            
            if modality == 'CT':
                # Application de la fenêtre CT appropriée
                pixel_array = self._apply_ct_window(pixel_array, ds)
            elif modality in ['MR', 'MRI']:
                # Normalisation pour IRM
                pixel_array = self._normalize_mr_image(pixel_array)
            elif modality in ['CR', 'DX']:
                # Normalisation pour radiographie
                pixel_array = self._normalize_xray_image(pixel_array)
            
            # Conversion en tensor PyTorch
            if len(pixel_array.shape) == 2:
                pixel_array = pixel_array[np.newaxis, ...]  # Ajout dimension channel
            
            tensor = torch.from_numpy(pixel_array.astype(np.float32))
            tensor = tensor.unsqueeze(0)  # Ajout dimension batch
            
            return tensor.to(self.device)
            
        except Exception as e:
            logger.error(f"Erreur lors de la préparation de l'image: {e}")
            return None
    
    def _apply_ct_window(self, pixel_array: np.ndarray, ds: Dataset) -> np.ndarray:
        """Application de la fenêtre CT"""
        # Valeurs par défaut pour fenêtre abdominale
        window_center = ds.get('WindowCenter', 40)
        window_width = ds.get('WindowWidth', 400)
        
        if isinstance(window_center, (list, tuple)):
            window_center = window_center[0]
        if isinstance(window_width, (list, tuple)):
            window_width = window_width[0]
        
        min_val = window_center - window_width // 2
        max_val = window_center + window_width // 2
        
        pixel_array = np.clip(pixel_array, min_val, max_val)
        pixel_array = (pixel_array - min_val) / (max_val - min_val)
        
        return pixel_array
    
    def _normalize_mr_image(self, pixel_array: np.ndarray) -> np.ndarray:
        """Normalisation pour images IRM"""
        # Normalisation percentile pour IRM
        p1, p99 = np.percentile(pixel_array, [1, 99])
        pixel_array = np.clip(pixel_array, p1, p99)
        pixel_array = (pixel_array - p1) / (p99 - p1)
        return pixel_array
    
    def _normalize_xray_image(self, pixel_array: np.ndarray) -> np.ndarray:
        """Normalisation pour radiographies"""
        # Normalisation min-max pour radiographies
        min_val = pixel_array.min()
        max_val = pixel_array.max()
        pixel_array = (pixel_array - min_val) / (max_val - min_val)
        return pixel_array
    
    async def _analyze_by_modality(self, image_tensor: torch.Tensor, modality: str, dicom_ds: Dataset) -> List[Finding]:
        """Analyse spécifique selon la modalité"""
        findings = []
        
        try:
            with torch.no_grad():
                # Prédiction du modèle
                output = self.model(image_tensor)
                
                # Simulation de détection d'anomalies pour la démonstration
                if modality == 'CT':
                    findings.extend(await self._detect_ct_findings(image_tensor, output, dicom_ds))
                elif modality in ['MR', 'MRI']:
                    findings.extend(await self._detect_mr_findings(image_tensor, output, dicom_ds))
                elif modality in ['CR', 'DX']:
                    findings.extend(await self._detect_xray_findings(image_tensor, output, dicom_ds))
                elif modality == 'MG':
                    findings.extend(await self._detect_mammo_findings(image_tensor, output, dicom_ds))
                
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse par modalité: {e}")
        
        return findings
    
    async def _detect_ct_findings(self, image_tensor: torch.Tensor, output: torch.Tensor, dicom_ds: Dataset) -> List[Finding]:
        """Détection d'anomalies en CT"""
        findings = []
        
        # Simulation de détection de nodules pulmonaires
        confidence = float(output[0, 1])  # Probabilité d'anomalie
        
        if confidence > settings.ai_confidence_threshold:
            finding = Finding(
                type="nodule_pulmonaire",
                confidence=confidence,
                location=(100, 150, 25, 25),  # x, y, width, height
                description=f"Nodule pulmonaire suspect détecté avec une confiance de {confidence:.2f}",
                severity="medium" if confidence > 0.9 else "low",
                measurements={"diameter_mm": 12.5, "volume_mm3": 817.5}
            )
            findings.append(finding)
        
        return findings
    
    async def _detect_mr_findings(self, image_tensor: torch.Tensor, output: torch.Tensor, dicom_ds: Dataset) -> List[Finding]:
        """Détection d'anomalies en IRM"""
        findings = []
        
        confidence = float(output[0, 1])
        
        if confidence > settings.ai_confidence_threshold:
            finding = Finding(
                type="lesion_cerebrale",
                confidence=confidence,
                location=(200, 180, 30, 30),
                description=f"Lésion cérébrale détectée avec une confiance de {confidence:.2f}",
                severity="high" if confidence > 0.95 else "medium",
                measurements={"diameter_mm": 15.2}
            )
            findings.append(finding)
        
        return findings
    
    async def _detect_xray_findings(self, image_tensor: torch.Tensor, output: torch.Tensor, dicom_ds: Dataset) -> List[Finding]:
        """Détection d'anomalies en radiographie"""
        findings = []
        
        confidence = float(output[0, 1])
        
        if confidence > settings.ai_confidence_threshold:
            finding = Finding(
                type="pneumonie",
                confidence=confidence,
                location=(150, 200, 80, 60),
                description=f"Opacité pulmonaire évocatrice de pneumonie (confiance: {confidence:.2f})",
                severity="medium",
                measurements={"surface_mm2": 1200}
            )
            findings.append(finding)
        
        return findings
    
    async def _detect_mammo_findings(self, image_tensor: torch.Tensor, output: torch.Tensor, dicom_ds: Dataset) -> List[Finding]:
        """Détection d'anomalies en mammographie"""
        findings = []
        
        confidence = float(output[0, 1])
        
        if confidence > settings.ai_confidence_threshold:
            finding = Finding(
                type="microcalcifications",
                confidence=confidence,
                location=(180, 220, 15, 15),
                description=f"Groupe de microcalcifications suspectes (confiance: {confidence:.2f})",
                severity="high" if confidence > 0.9 else "medium",
                measurements={"count": 8, "cluster_size_mm": 12}
            )
            findings.append(finding)
        
        return findings
    
    def _calculate_overall_confidence(self, findings: List[Finding]) -> float:
        """Calcul de la confiance globale"""
        if not findings:
            return 0.0
        
        # Moyenne pondérée des confidences
        total_confidence = sum(f.confidence for f in findings)
        return total_confidence / len(findings)