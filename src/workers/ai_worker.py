# Worker pour le traitement IA en arrière-plan
import asyncio
import logging
import sys
from pathlib import Path

# Ajout du répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from ai_engine.processor import AIProcessor

logger = logging.getLogger(__name__)

class AIWorker:
    """Worker pour le traitement des tâches IA en arrière-plan"""
    
    def __init__(self):
        self.ai_processor = AIProcessor()
        self.running = False
        
    async def start(self):
        """Démarrage du worker"""
        logger.info("🤖 Démarrage du worker IA...")
        
        # Chargement du modèle IA
        await self.ai_processor.load_model()
        
        self.running = True
        logger.info("✅ Worker IA démarré et prêt")
        
        # Boucle principale du worker
        while self.running:
            try:
                # Ici on traiterait les tâches en file d'attente
                # En production, on utiliserait Redis/Celery
                await asyncio.sleep(5)
                logger.debug("Worker IA en attente...")
                
            except Exception as e:
                logger.error(f"Erreur dans le worker IA: {e}")
                await asyncio.sleep(10)
    
    def stop(self):
        """Arrêt du worker"""
        logger.info("🛑 Arrêt du worker IA...")
        self.running = False

async def main():
    """Point d'entrée du worker"""
    # Configuration du logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    worker = AIWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        worker.stop()
        logger.info("Worker IA arrêté par l'utilisateur")

if __name__ == "__main__":
    asyncio.run(main())
