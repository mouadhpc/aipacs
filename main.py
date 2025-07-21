#!/usr/bin/env python3
# Script principal de démarrage de l'application IA PACS

import asyncio
import logging
import signal
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import uvicorn

# Ajout du répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import settings
from src.dicom_handler.server import DICOMServer
from src.api.main import app

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(settings.log_directory) / 'ai_pacs.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class AIPACSApplication:
    """Application principale IA PACS"""
    
    def __init__(self):
        self.dicom_server = None
        self.api_server = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.running = False
        
    async def start(self):
        """Démarrage de l'application complète"""
        try:
            logger.info("🚀 Démarrage de l'application IA PACS")
            logger.info(f"Version: {settings.app_version}")
            logger.info(f"Mode debug: {settings.debug}")
            
            # Vérification des répertoires
            self._ensure_directories()
            
            # Démarrage du serveur DICOM en arrière-plan
            logger.info("Démarrage du serveur DICOM...")
            self.dicom_server = DICOMServer()
            dicom_task = asyncio.create_task(
                asyncio.to_thread(self.dicom_server.start_server)
            )
            
            # Attente pour s'assurer que le serveur DICOM est démarré
            await asyncio.sleep(2)
            
            # Démarrage du serveur API
            logger.info("Démarrage du serveur API...")
            config = uvicorn.Config(
                app,
                host=settings.api_host,
                port=settings.api_port,
                log_level=settings.log_level.lower(),
                reload=settings.debug
            )
            
            api_server = uvicorn.Server(config)
            api_task = asyncio.create_task(api_server.serve())
            
            self.running = True
            logger.info("✅ Application IA PACS démarrée avec succès")
            logger.info(f"📡 Serveur DICOM: {settings.dicom_host}:{settings.dicom_port} (AE: {settings.dicom_ae_title})")
            logger.info(f"🌐 API REST: http://{settings.api_host}:{settings.api_port}{settings.api_prefix}/docs")
            logger.info(f"🏥 PACS cible: {settings.pacs_host}:{settings.pacs_port} (AE: {settings.pacs_ae_title})")
            
            # Attente des tâches
            await asyncio.gather(dicom_task, api_task, return_exceptions=True)
            
        except KeyboardInterrupt:
            logger.info("Arrêt demandé par l'utilisateur")
        except Exception as e:
            logger.error(f"Erreur lors du démarrage: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Arrêt propre de l'application"""
        if not self.running:
            return
            
        logger.info("🛑 Arrêt de l'application IA PACS...")
        
        try:
            # Arrêt du serveur DICOM
            if self.dicom_server:
                self.dicom_server.stop_server()
                logger.info("Serveur DICOM arrêté")
            
            # Arrêt de l'executor
            self.executor.shutdown(wait=True)
            logger.info("Executor arrêté")
            
            self.running = False
            logger.info("✅ Application arrêtée proprement")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt: {e}")
    
    def _ensure_directories(self):
        """Création des répertoires nécessaires"""
        directories = [
            settings.data_directory,
            settings.temp_directory,
            settings.log_directory,
            Path(settings.data_directory) / "reports",
            Path(settings.data_directory) / "images",
            settings.report_template_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Répertoire vérifié: {directory}")

# Instance globale de l'application
app_instance = AIPACSApplication()

def signal_handler(signum, frame):
    """Gestionnaire de signaux pour arrêt propre"""
    logger.info(f"Signal {signum} reçu, arrêt en cours...")
    asyncio.create_task(app_instance.stop())

async def main():
    """Point d'entrée principal"""
    # Configuration des gestionnaires de signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Démarrage de l'application
    await app_instance.start()

if __name__ == "__main__":
    try:
        # Vérification de Python 3.8+
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ requis")
            sys.exit(1)
        
        # Affichage de la bannière
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    IA PACS - RADIOLOGIE                     ║
║              Application d'Analyse Automatique              ║
║                     Version 1.0.0                          ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Démarrage de l'application
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)