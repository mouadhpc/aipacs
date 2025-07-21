# Application IA pour Radiologie avec PACS Interne

## Vue d'ensemble

Cette application développe une solution IA complète pour l'analyse automatique d'images médicales DICOM avec intégration PACS.

## Objectifs

- Réception automatique d'images DICOM (CT, IRM, RX, Mammographie)
- Analyse IA pour détection/segmentation d'anomalies
- Génération de comptes rendus structurés (DICOM SR/PDF)
- Réinjection dans le PACS interne
- Interface de suivi et gestion

## Architecture

```
[ Modalités ] → [ PACS interne ] → [ Serveur IA ] → [ Visualiseur ]
```

## Structure du projet

- `/docs/` - Documentation technique et fonctionnelle
- `/src/` - Code source de l'application
- `/tests/` - Tests unitaires et d'intégration
- `/docker/` - Configuration Docker
- `/config/` - Fichiers de configuration

## Statut actuel

✅ **Phase 1 : Analyse & Cadrage** - Terminée
✅ **Phase 2 : Setup technique** - Terminée
✅ **Phase 3 : Développement DevOps** - Terminée
🎉 **Application fonctionnelle** - PRÊTE

## Installation

### Prérequis

- Python 3.8+
- Docker et Docker Compose
- PostgreSQL 15+
- Redis 7+

### Installation rapide avec Docker

```bash
# Cloner le projet
git clone <repository-url>
cd ai-pacs

# Copier la configuration
cp .env.example .env
# Éditer .env avec vos paramètres

# Démarrer avec Docker Compose
docker-compose up -d
```

### Installation manuelle

```bash
# Installation des dépendances
pip install -r requirements.txt

# Configuration de la base de données
# Créer une base PostgreSQL 'ai_pacs'

# Démarrage de l'application
python main.py
```

## Utilisation

### Démarrage des services

```bash
# Avec Docker
docker-compose up -d

# Manuel
python main.py
```

### Accès aux interfaces

- **API REST**: http://localhost:8000/api/v1/docs
- **Dashboard**: http://localhost:8000
- **Serveur DICOM**: localhost:11112 (AE Title: IA_SERVER)

### Configuration PACS

1. Configurer votre PACS pour envoyer vers `IA_SERVER:11112`
2. Configurer l'application pour renvoyer vers votre PACS
3. Tester la connectivité DICOM

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Modalités  │───▶│ PACS Interne │───▶│ Serveur IA  │
└─────────────┘    └──────────────┘    └─────────────┘
                           ▲                   │
                           │                   ▼
                   ┌──────────────┐    ┌─────────────┐
                   │   OsiriX     │    │ Génération  │
                   │ (Visualiseur)│    │    CR       │
                   └──────────────┘    └─────────────┘
```

## Fonctionnalités

- ✅ Réception DICOM automatique (CT, IRM, RX, Mammographie)
- ✅ Analyse IA avec détection d'anomalies
- ✅ Génération de comptes rendus (DICOM SR/PDF)
- ✅ Réinjection dans le PACS
- ✅ API REST pour monitoring
- ✅ Interface web de gestion
- ✅ Containerisation Docker

## Configuration

Les paramètres principaux sont dans `.env`:

```env
# DICOM
DICOM_AE_TITLE=IA_SERVER
DICOM_PORT=11112
PACS_HOST=192.168.1.100
PACS_PORT=11111

# IA
AI_CONFIDENCE_THRESHOLD=0.8
REPORT_OUTPUT_FORMAT=DICOM_SR
```

## Tests

Le projet utilise pytest pour les tests unitaires et d'intégration. Pour exécuter les tests :

1. Installer les dépendances de développement :
```bash
pip install -r requirements-dev.txt
```

2. Lancer les tests :
```bash
# Tous les tests
pytest

# Tests avec couverture
pytest --cov=src

# Tests spécifiques
pytest tests/test_ai_processor.py
```

### Types de tests

- **Tests unitaires** : Validation des composants individuels
- **Tests d'intégration** : Vérification des interactions entre modules
- **Tests asynchrones** : Validation des opérations async/await

### Qualité du code

Le projet utilise plusieurs outils pour maintenir la qualité du code :

```bash
# Formatage
black src/ tests/

# Tri des imports
isort src/ tests/

# Vérification statique
flake8 src/ tests/
mypy src/

# Analyse de sécurité
bandit -r src/
safety check
```

Les tests sont automatiquement exécutés via GitHub Actions à chaque push et pull request.

## Contribution

1. Fork le projet
2. Créer une branche feature
3. Commiter les changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Support

- Documentation: `/docs/`
- Issues: GitHub Issues
- Email: support@ai-pacs.com