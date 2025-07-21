# Serveur DICOM pour la réception des images
import asyncio
import logging
from pathlib import Path
from typing import Optional

from pynetdicom import AE, evt, StoragePresentationContexts
from pynetdicom.sop_class import (
    CTImageStorage,
    MRImageStorage,
    DigitalXRayImageStorageForPresentation,
    DigitalMammographyXRayImageStorageForPresentation
)
from pydicom import dcmread
from pydicom.dataset import Dataset

from ..config.settings import settings
from ..ai_engine.processor import AIProcessor
from ..report_generator.generator import ReportGenerator

logger = logging.getLogger(__name__)

class DICOMServer:
    """Serveur DICOM pour la réception et le traitement des images"""
    
    def __init__(self):
        self.ae = AE(ae_title=settings.dicom_ae_title)
        self.ai_processor = AIProcessor()
        self.report_generator = ReportGenerator()
        
        # Configuration des contextes de présentation supportés
        self.ae.supported_contexts = StoragePresentationContexts
        
        # Ajout des SOP Classes spécifiques
        self.ae.add_supported_context(CTImageStorage)
        self.ae.add_supported_context(MRImageStorage)
        self.ae.add_supported_context(DigitalXRayImageStorageForPresentation)
        self.ae.add_supported_context(DigitalMammographyXRayImageStorageForPresentation)
        
        # Configuration des gestionnaires d'événements
        self.ae.on_c_store = self.handle_store
        
    def handle_store(self, event):
        """Gestionnaire pour les requêtes C-STORE"""
        try:
            # Récupération du dataset DICOM
            ds = event.dataset
            ds.file_meta = event.file_meta
            
            logger.info(f"Réception d'une image DICOM: {ds.SOPInstanceUID}")
            logger.info(f"Modalité: {ds.get('Modality', 'Unknown')}")
            logger.info(f"Patient ID: {ds.get('PatientID', 'Unknown')}")
            
            # Sauvegarde temporaire de l'image
            temp_path = self._save_temp_image(ds)
            
            # Traitement asynchrone de l'image
            asyncio.create_task(self._process_image_async(ds, temp_path))
            
            # Retour du statut de succès
            return 0x0000  # Success
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement C-STORE: {e}")
            return 0xC000  # Failure
    
    def _save_temp_image(self, ds: Dataset) -> Path:
        """Sauvegarde temporaire de l'image DICOM"""
        temp_dir = Path(settings.temp_directory)
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{ds.SOPInstanceUID}.dcm"
        temp_path = temp_dir / filename
        
        ds.save_as(temp_path, write_like_original=False)
        logger.debug(f"Image sauvegardée temporairement: {temp_path}")
        
        return temp_path
    
    async def _process_image_async(self, ds: Dataset, image_path: Path):
        """Traitement asynchrone de l'image avec IA"""
        try:
            logger.info(f"Début du traitement IA pour: {ds.SOPInstanceUID}")
            
            # Analyse IA de l'image
            ai_results = await self.ai_processor.analyze_image(image_path, ds)
            
            if ai_results:
                logger.info(f"Analyse IA terminée. Anomalies détectées: {len(ai_results.get('findings', []))}")
                
                # Génération du compte rendu
                report = await self.report_generator.generate_report(ds, ai_results)
                
                if report:
                    # Envoi du rapport vers le PACS
                    await self._send_report_to_pacs(report)
                    logger.info(f"Rapport envoyé au PACS pour: {ds.SOPInstanceUID}")
            
            # Nettoyage du fichier temporaire
            if image_path.exists():
                image_path.unlink()
                logger.debug(f"Fichier temporaire supprimé: {image_path}")
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement asynchrone: {e}")
    
    async def _send_report_to_pacs(self, report_path: Path):
        """Envoi du rapport vers le PACS interne"""
        try:
            # Configuration de l'association avec le PACS
            ae_client = AE(ae_title=settings.dicom_ae_title)
            ae_client.add_requested_context(CTImageStorage)  # Ou le bon SOP Class pour les rapports
            
            # Lecture du rapport DICOM
            report_ds = dcmread(report_path)
            
            # Établissement de l'association
            assoc = ae_client.associate(
                settings.pacs_host,
                settings.pacs_port,
                ae_title=settings.pacs_ae_title
            )
            
            if assoc.is_established:
                # Envoi du rapport
                status = assoc.send_c_store(report_ds)
                
                if status:
                    logger.info(f"Rapport envoyé avec succès au PACS: {status.Status}")
                else:
                    logger.error("Échec de l'envoi du rapport au PACS")
                
                # Fermeture de l'association
                assoc.release()
            else:
                logger.error(f"Impossible d'établir une association avec le PACS {settings.pacs_host}:{settings.pacs_port}")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi au PACS: {e}")
    
    def start_server(self):
        """Démarrage du serveur DICOM"""
        logger.info(f"Démarrage du serveur DICOM sur {settings.dicom_host}:{settings.dicom_port}")
        logger.info(f"AE Title: {settings.dicom_ae_title}")
        
        try:
            self.ae.start_server(
                (settings.dicom_host, settings.dicom_port),
                block=True
            )
        except KeyboardInterrupt:
            logger.info("Arrêt du serveur DICOM")
        except Exception as e:
            logger.error(f"Erreur du serveur DICOM: {e}")
    
    def stop_server(self):
        """Arrêt du serveur DICOM"""
        logger.info("Arrêt du serveur DICOM...")
        self.ae.shutdown()

if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Démarrage du serveur
    server = DICOMServer()
    server.start_server()