# Phase 2 : Architecture Technique

## Vue d'ensemble de l'architecture

### Composants principaux

```
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION IA PACS                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   API REST  │  │ DICOM Server│  │ AI Engine   │  │ Reports │ │
│  │  (FastAPI)  │  │ (pynetdicom)│  │ (PyTorch)   │  │ (SR/PDF)│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ PostgreSQL  │  │    Redis    │  │   Docker    │              │
│  │ (Database)  │  │   (Cache)   │  │(Container)  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Flux de données

### 1. Réception d'images DICOM

```
Modalité → C-STORE → PACS Interne → C-STORE → Serveur IA
```

1. **Modalité** envoie l'image via C-STORE
2. **PACS Interne** reçoit et stocke l'image
3. **PACS Interne** transfère vers le **Serveur IA** (AE: IA_SERVER)
4. **Serveur IA** sauvegarde temporairement l'image

### 2. Traitement IA

```
Image DICOM → Préparation → Modèle IA → Détection → Résultats
```

1. **Préparation** : Normalisation selon la modalité
2. **Modèle IA** : Analyse avec PyTorch/TensorFlow
3. **Détection** : Identification des anomalies
4. **Résultats** : Structuration des findings

### 3. Génération de rapports

```
Résultats IA → Template → DICOM SR/PDF → Stockage
```

1. **Template** : Application du modèle de rapport
2. **DICOM SR** : Génération du Structured Report
3. **PDF** : Génération alternative en PDF
4. **Stockage** : Sauvegarde locale

### 4. Réinjection PACS

```
Rapport → C-STORE → PACS Interne → Indexation → OsiriX
```

1. **C-STORE** : Envoi du rapport vers le PACS
2. **Indexation** : Intégration dans la base PACS
3. **Consultation** : Disponible dans OsiriX

## Modules détaillés

### Module DICOM Handler

**Fichiers :**
- `src/dicom_handler/server.py` - Serveur DICOM principal
- `src/dicom_handler/client.py` - Client pour envoi vers PACS
- `src/dicom_handler/utils.py` - Utilitaires DICOM

**Responsabilités :**
- Réception des images via C-STORE
- Validation des données DICOM
- Gestion des associations DICOM
- Envoi des rapports vers le PACS

**Configuration :**
```python
DICOM_AE_TITLE = "IA_SERVER"
DICOM_PORT = 11112
PACS_HOST = "192.168.1.100"
PACS_PORT = 11111
```

### Module AI Engine

**Fichiers :**
- `src/ai_engine/processor.py` - Processeur principal
- `src/ai_engine/models.py` - Gestion des modèles
- `src/ai_engine/transforms.py` - Transformations d'images

**Responsabilités :**
- Chargement et gestion des modèles IA
- Préparation des images selon la modalité
- Analyse et détection d'anomalies
- Calcul des scores de confiance

**Modalités supportées :**
- **CT** : Détection de nodules, masses
- **IRM** : Lésions cérébrales, anomalies
- **RX** : Pneumonie, fractures
- **Mammographie** : Microcalcifications, masses

### Module Report Generator

**Fichiers :**
- `src/report_generator/generator.py` - Générateur principal
- `src/report_generator/templates.py` - Gestion des templates
- `src/report_generator/formatters.py` - Formatage des données

**Responsabilités :**
- Génération de rapports DICOM SR
- Génération de rapports PDF
- Application des templates
- Structuration des données médicales

**Formats supportés :**
- **DICOM SR** : Structured Report standard
- **PDF** : Rapport lisible avec ReportLab
- **HTML** : Template web (futur)

### Module API

**Fichiers :**
- `src/api/main.py` - Application FastAPI principale
- `src/api/routers/` - Routeurs par domaine
- `src/api/middleware.py` - Middlewares personnalisés

**Endpoints principaux :**
```
GET  /api/v1/health          - État de santé
GET  /api/v1/dicom/status    - Statut serveur DICOM
GET  /api/v1/ai/models       - Modèles disponibles
GET  /api/v1/reports         - Liste des rapports
POST /api/v1/ai/analyze      - Analyse manuelle
```

## Base de données

### Schéma PostgreSQL

```sql
-- Table des études
CREATE TABLE studies (
    id SERIAL PRIMARY KEY,
    study_uid VARCHAR(64) UNIQUE NOT NULL,
    patient_id VARCHAR(64),
    patient_name VARCHAR(255),
    study_date DATE,
    modality VARCHAR(16),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des analyses IA
CREATE TABLE ai_analyses (
    id SERIAL PRIMARY KEY,
    study_id INTEGER REFERENCES studies(id),
    instance_uid VARCHAR(64),
    model_version VARCHAR(32),
    confidence_score FLOAT,
    processing_time FLOAT,
    status VARCHAR(32),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des anomalies détectées
CREATE TABLE findings (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES ai_analyses(id),
    finding_type VARCHAR(64),
    confidence FLOAT,
    location_x INTEGER,
    location_y INTEGER,
    location_width INTEGER,
    location_height INTEGER,
    severity VARCHAR(16),
    description TEXT,
    measurements JSONB
);

-- Table des rapports générés
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES ai_analyses(id),
    report_type VARCHAR(16), -- 'DICOM_SR' ou 'PDF'
    file_path VARCHAR(512),
    sent_to_pacs BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Sécurité

### Authentification
- **JWT** pour l'API REST
- **Tokens** avec expiration configurable
- **RBAC** pour les permissions

### Chiffrement
- **HTTPS** pour l'API
- **TLS** pour DICOM (optionnel)
- **Chiffrement** des données sensibles

### Audit
- **Logs** de toutes les opérations
- **Traçabilité** des analyses IA
- **Monitoring** des accès

## Performance

### Optimisations
- **Cache Redis** pour les résultats fréquents
- **Pool de connexions** pour la base de données
- **Traitement asynchrone** des images
- **Batch processing** pour l'IA

### Métriques
- **Temps de traitement** par modalité
- **Throughput** d'images par heure
- **Taux de détection** d'anomalies
- **Utilisation ressources** (CPU, RAM, GPU)

## Déploiement

### Docker Compose
```yaml
services:
  ai_pacs_app:     # Application principale
  postgres:        # Base de données
  redis:          # Cache
  ai_worker:      # Worker IA
```

### Variables d'environnement
```env
# Base de données
DATABASE_URL=postgresql://user:pass@host:5432/db

# DICOM
DICOM_AE_TITLE=IA_SERVER
DICOM_PORT=11112
PACS_HOST=192.168.1.100
PACS_PORT=11111

# IA
AI_MODEL_PATH=./models/ai_model.pth
AI_CONFIDENCE_THRESHOLD=0.8

# Sécurité
SECRET_KEY=your-secret-key
```

### Monitoring
- **Prometheus** pour les métriques
- **Grafana** pour les dashboards
- **Logs centralisés** avec ELK Stack
- **Alertes** sur les erreurs critiques

## Tests

### Tests unitaires
```bash
pytest tests/unit/
```

### Tests d'intégration
```bash
pytest tests/integration/
```

### Tests DICOM
```bash
python tests/test_dicom_connectivity.py
```

### Tests de charge
```bash
locust -f tests/load/locustfile.py
```

## Maintenance

### Sauvegarde
- **Base de données** : Dump quotidien
- **Modèles IA** : Versioning
- **Logs** : Rotation automatique
- **Rapports** : Archivage mensuel

### Mise à jour
- **Rolling deployment** avec Docker
- **Migration** de base de données
- **Validation** des nouveaux modèles
- **Rollback** en cas de problème

## Prochaines étapes

1. **Phase 3** : Développement du pipeline IA
2. **Phase 4** : Génération des comptes rendus
3. **Phase 5** : Intégration bidirectionnelle PACS
4. **Phase 6** : Interface utilisateur
5. **Phase 7** : Tests et validation clinique
6. **Phase 8** : Déploiement pilote

---

**Document technique - Version 1.0**
**Date : Janvier 2025**
**Statut : Architecture validée**