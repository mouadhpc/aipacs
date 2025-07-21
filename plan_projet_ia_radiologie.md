## ✅ PLAN DE PROJET — Application IA pour Radiologie (avec PACS Interne)

---

### 🎯 1️⃣ Objectif du projet

Développer une solution IA pour :

- Recevoir automatiquement des images DICOM (toutes modalités : CT, IRM, RX, Mammo).
- Analyser ces images avec un moteur IA pour détecter ou segmenter des anomalies.
- Générer un **compte rendu structuré (CR)** au format **DICOM SR** ou **PDF**.
- Réinjecter ce CR dans le **PACS interne** et le rendre accessible au radiologue via OsiriX ou tout autre visualiseur DICOM.

---

### 📌 2️⃣ Périmètre fonctionnel

| Fonction                  | Description                                                               |
| ------------------------- | ------------------------------------------------------------------------- |
| **Réception d’images**    | Connexion DICOM C-STORE depuis PACS interne ou modalités.                 |
| **Analyse IA**            | Pipeline IA : détection, segmentation, mesures.                           |
| **Structuration CR**      | Génération automatique du rapport (DICOM SR ou PDF encapsulé).            |
| **Réinjection PACS**      | Retour des résultats vers le PACS interne pour archivage et consultation. |
| **Interface utilisateur** | Dashboard web pour suivre les traitements et gérer les rapports.          |
| **Sécurité & conformité** | Authentification, logs, chiffrement, RGPD/HIPAA.                          |

---

### 📌 3️⃣ Architecture cible

```
[ Modalités (CT, IRM, RX, Mammo) ]
               │
         [ PACS interne ]
               │
           ┌───┴────┐
           ▼        ▼
    [ Serveur IA ]  [ Visualiseur (OsiriX) ]
```

**Principe :**

- Le PACS interne joue le rôle de hub DICOM.
- Le serveur IA est configuré comme un nœud DICOM.
- Le CR est renvoyé vers le PACS interne, indexé et consultable dans OsiriX.

---

### 📌 4️⃣ Stack technologique recommandée

| Bloc                | Technologie                             |
| ------------------- | --------------------------------------- |
| **Flux DICOM**      | DCM4CHEE, DCMTK, pynetdicom             |
| **IA**              | Python (PyTorch, TensorFlow, MONAI)     |
| **CR**              | Python NLP + Jinja2 + PDFKit/WeasyPrint |
| **Backend API**     | Python (FastAPI)                        |
| **Frontend**        | React / Vue.js                          |
| **Base de données** | PostgreSQL                              |
| **Déploiement**     | Docker                                  |
| **Sécurité**        | HTTPS, JWT, audit log                   |

---

### 📌 5️⃣ Étapes de développement

1️⃣ **Analyse & cadrage** — Définir cas d’usage, flux DICOM, besoins métier.\
2️⃣ **Setup technique** — Paramétrage PACS interne, AE Titles, tests C-STORE.\
3️⃣ **Pipeline IA** — Développement du modèle IA et workflow.\
4️⃣ **Génération CR** — Automatisation en DICOM SR ou PDF encapsulé.\
5️⃣ **Intégration bidirectionnelle** — Flux PACS interne ↔ Serveur IA.\
6️⃣ **Dashboard utilisateur** — Suivi des jobs et accès aux rapports.\
7️⃣ **Tests & validation clinique** — Tests unitaires, validation par radiologues.\
8️⃣ **Déploiement pilote** — Mise en place en environnement clinique restreint.

---

### 📌 6️⃣ Planning indicatif

| Semaine | Objectif                         |
| ------- | -------------------------------- |
| S1      | Cadrage et cahier des charges    |
| S2      | Setup PACS interne & tests DICOM |
| S3-S5   | Développement IA                 |
| S6      | Génération CR                    |
| S7      | Intégration bidirectionnelle     |
| S8      | Interface utilisateur            |
| S9      | Sécurité & validation            |
| S10     | Déploiement pilote               |

---

### 📌 7️⃣ Livrables finaux

✅ Serveur IA conteneurisé\
✅ Modèle IA packagé\
✅ API REST documentée\
✅ Dashboard utilisateur\
✅ Documentation technique\
✅ Jeu de tests\
✅ Rapport de validation clinique\
✅ Guide d’intégration PACS interne

---

**Contact :** Chef de projet / Consultant / Radiologue référent

**Version :** Juillet 2025 ✅

---

**Ce document peut être annexé au cahier des charges officiel ou utilisé pour présenter le projet aux parties prenantes.**

