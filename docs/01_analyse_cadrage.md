# Phase 1 : Analyse & Cadrage

## 1. Définition des cas d'usage

### Cas d'usage principal
**Analyse automatique d'images DICOM avec génération de compte rendu**

**Acteurs :**
- Radiologue
- Système PACS interne
- Serveur IA
- Modalités d'imagerie (CT, IRM, RX, Mammographie)

**Scénario nominal :**
1. Une modalité envoie une image DICOM vers le PACS interne
2. Le PACS interne transfère automatiquement l'image vers le serveur IA
3. Le serveur IA analyse l'image et détecte les anomalies
4. Un compte rendu structuré est généré (DICOM SR ou PDF)
5. Le compte rendu est renvoyé vers le PACS interne
6. Le radiologue consulte l'image et le compte rendu via OsiriX

### Cas d'usage secondaires
- Consultation des rapports via dashboard web
- Gestion des files d'attente de traitement
- Monitoring des performances IA
- Administration des paramètres système

## 2. Flux DICOM

### Configuration AE Titles
- **PACS_INTERNE** : AE Title du PACS principal
- **IA_SERVER** : AE Title du serveur d'analyse IA
- **MODALITES** : AE Titles des différentes modalités

### Flux de données
```
Modalité → C-STORE → PACS_INTERNE
PACS_INTERNE → C-STORE → IA_SERVER
IA_SERVER → C-STORE → PACS_INTERNE (avec CR)
```

## 3. Besoins métier

### Besoins fonctionnels
- **Réception automatique** : Support de toutes les modalités DICOM
- **Analyse IA** : Détection d'anomalies avec score de confiance
- **Génération CR** : Format structuré et lisible
- **Intégration PACS** : Transparence pour le radiologue
- **Interface de suivi** : Dashboard temps réel

### Besoins non-fonctionnels
- **Performance** : Traitement < 5 minutes par étude
- **Disponibilité** : 99.9% de temps de fonctionnement
- **Sécurité** : Chiffrement des données, authentification
- **Conformité** : RGPD, HIPAA, normes DICOM
- **Scalabilité** : Support de 100+ études/jour

## 4. Contraintes techniques

### Contraintes d'infrastructure
- Intégration avec PACS existant
- Réseau hospitalier sécurisé
- Stockage des données sensibles
- Sauvegarde et archivage

### Contraintes réglementaires
- Marquage CE médical (si applicable)
- Validation clinique
- Traçabilité des traitements
- Audit et logs

## 5. Critères d'acceptation

### Phase 1 (Cadrage)
- [x] Cas d'usage définis
- [x] Flux DICOM spécifiés
- [x] Besoins métier identifiés
- [ ] Architecture technique validée
- [ ] Planning détaillé établi

### Prochaines étapes
- Validation de l'architecture avec l'équipe technique
- Setup de l'environnement de développement
- Configuration du PACS interne pour les tests