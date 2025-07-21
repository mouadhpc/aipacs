#!/usr/bin/env python3
"""
Script de démarrage pour le développement AI PACS
Lance l'application en mode développement sans Docker
"""

import sys
import os
import logging
from pathlib import Path
from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()
    
    # Ajout du répertoire src au path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root / "src"))
    
    # Configuration de base
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("LOG_LEVEL", "DEBUG")
    os.environ.setdefault("API_HOST", "127.0.0.1")
    os.environ.setdefault("API_PORT", "8000")
    
    # Configuration simplifiée pour développement
    os.environ.setdefault("DATABASE_URL", "sqlite:///./ai_pacs_dev.db")
    os.environ.setdefault("DICOM_AE_TITLE", "IA_SERVER")
    os.environ.setdefault("DICOM_PORT", "11112")
    os.environ.setdefault("PACS_HOST", "localhost")
    os.environ.setdefault("PACS_PORT", "11111")

    print("🚀 Démarrage AI PACS - Mode Développement")
    print("=" * 50)
    
    try:
        # Import et configuration
        import uvicorn
        
        # Création des répertoires nécessaires
        for directory in ["data", "temp", "logs", "templates/reports"]:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Répertoire créé : {directory}")
        
        # Configuration logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        print("\n🔧 Configuration:")
        print(f"   - API: http://127.0.0.1:8000")
        print(f"   - API Docs: http://127.0.0.1:8000/api/v1/docs")
        print(f"   - Debug Mode: ON")
        print(f"   - Database: SQLite (dev)")
        print(f"   - DICOM Server: localhost:11112")
        
        print("\n🎯 Fonctionnalités disponibles:")
        print("   ✅ API REST complète")
        print("   ✅ Endpoints DICOM, IA, Reports")
        print("   ✅ Monitoring système")
        print("   ⚠️  Base de données simplifiée (SQLite)")
        print("   ⚠️  Serveur DICOM simulé (sans pynetdicom)")
        
        print("\n🚀 Démarrage du serveur...")
        print("   Arrêt avec Ctrl+C")
        print("=" * 50)
        
        # Lancement du serveur sans reload pour éviter les problèmes Windows
        uvicorn.run(
            "src.api.main:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("\n💡 Solutions:")
        print("   pip install fastapi uvicorn python-dotenv")
        print("   ou utilisez Docker: docker-compose up")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt demandé par l'utilisateur")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("👋 AI PACS arrêté!")
