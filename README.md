# Système de Diagnostic des Maladies des Plantes de Tomates

Application full-stack de diagnostic automatique des maladies des feuilles de tomates par Machine Learning et Computer Vision.

---

## Table des Matières

- [Aperçu](#aperçu)
- [Maladies Détectées](#maladies-détectées)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation Backend](#installation-backend-django)
- [Installation Frontend](#installation-frontend-angular)
- [Pipeline de Traitement](#pipeline-de-traitement)
- [Performances](#performances)
- [Structure du Projet](#structure-du-projet)

---

## Aperçu

Ce projet implémente une solution complète de diagnostic automatique des maladies des plantes de tomates basée sur l'analyse d'images.

**Fonctionnalités clés :**
- Détection automatique des maladies en **< 1 seconde**
- Précision de **91.7%** (Random Forest + 166 features)
- Visualisation des zones affectées sur la feuille
- Recommandations de traitement personnalisées
- Historique complet des diagnostics
- Interface drag & drop intuitive

---

## Maladies Détectées

| Classe | Nom | Gravité | Zone Affectée |
|--------|-----|---------|---------------|
| `Tomato___healthy` | Feuille Saine | Aucune | 0–10% |
| `Tomato___Septoria_leaf_spot` | Septoriose | Moyenne | 15–35% |
| `Tomato___Tomato_mosaic_virus` | Virus de la Mosaïque | Élevée | 20–40% |
| `Tomato___Bacterial_spot` | Tache Bactérienne | Élevée | 20–50% |

---

## Architecture

```
+--------------------------------------------------+
|              Frontend Angular 21.1.0              |
|   Upload | Résultat Diagnostic | Historique       |
|              http://localhost:4200                |
+----------------------+---------------------------+
                       | HTTP / REST API
+----------------------+---------------------------+
|              Backend Django + DRF                 |
|  preprocessing | feature_extraction | model       |
|              http://localhost:8000                |
+----------------------+---------------------------+
                       |
          +------------+------------+
          |   best_model.pkl        |
          |   (Random Forest ML)    |
          +-------------------------+
```

### Stack Technologique

**Backend**
| Composant | Version | Rôle |
|-----------|---------|------|
| Python | 3.11.9 | Langage principal |
| Django + DRF | Dernière | Framework web + API REST |
| OpenCV | Dernière | Vision par ordinateur |
| Scikit-learn | Dernière | Machine Learning |
| NumPy / Pandas | Dernière | Calcul scientifique |

**Frontend**
| Composant | Version | Rôle |
|-----------|---------|------|
| Angular | 21.1.0 | Framework frontend |
| TypeScript | Dernière | Langage typé |
| Node.js | 18+ | Runtime JavaScript |
| npm | 9+ | Gestionnaire de paquets |

---

## Prérequis

Assure-toi d'avoir installé :

- [Python 3.11.9](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [npm 9+](https://www.npmjs.com/)
- [Angular CLI 21.1.0](https://angular.dev/)

---

## Installation Backend Django

**Étape 1 — Créer et activer l'environnement virtuel**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS
```

**Étape 2 — Installer les dépendances**
```bash
pip install -r requirements.txt
```

**Étape 3 — Placer le modèle entraîné**
```bash
mkdir models
# Copier best_model.pkl dans le dossier models/
```

**Étape 4 — Appliquer les migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Étape 5 — Lancer le serveur**
```bash
python manage.py runserver
```

> API disponible sur : **http://localhost:8000**

---

## Installation Frontend Angular

**Étape 1 — Installer Angular CLI**
```bash
npm install -g @angular/cli@21.1.0
```

**Étape 2 — Installer les dépendances**
```bash
npm install
```

**Étape 3 — Vérifier la configuration de l'API**

Dans `src/app/services/diagnosis.service.ts`, vérifier :
```typescript
private readonly API_URL = 'http://localhost:8000/api';
```

**Étape 4 — Lancer l'application**
```bash
ng serve
```

> Application disponible sur : **http://localhost:4200**

---

## Configuration CORS

Dans `settings.py` du backend Django :

```python
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
]
```

---

## Pipeline de Traitement

```
1. Upload image (JPG/PNG)
        |
2. Redimensionnement -> 256x256 px
        |
3. Segmentation feuille (masque HSV vert)
        |
4. Extraction features (couleur, texture, forme)
        |
5. Prédiction Random Forest (best_model.pkl)
        |
6. Détection zones affectées
        |
7. Réponse API -> Visualisation + Recommandations
```

**Features extraites (166 au total) :**
| Famille | Contribution | Exemples |
|---------|-------------|---------|
| Couleur | 51% | Canal LAB-a, Variance HSV |
| Texture | 32% | LBP uniformité, GLCM contraste |
| Forme | 17% | Ratio zone affectée |

---

## Performances

| Métrique | Valeur |
|----------|--------|
| Précision globale | **91.7%** |
| Temps de traitement | **< 1 seconde** |
| Confiance feuille saine | 99.7% |
| Confiance tache bactérienne | 99.9% |
| Segmentation IoU | 0.85 |

**Performances par type de smartphone :**
| Gamme | Sans correction | Avec correction |
|-------|----------------|----------------|
| Haut gamme | 89% | 92% |
| Milieu gamme | 78% | 88% |
| Entrée gamme | 61% | 81% |

---

## Structure du Projet

```
plant_disease_api/
├── plant_disease_api/       # Config Django
│   ├── settings.py
│   └── urls.py
├── api/                     # Application principale
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── utils/
│       ├── preprocessing.py      # Segmentation
│       ├── feature_extraction.py # Features couleur/texture/forme
│       └── model_loader.py       # Chargement modèle (Singleton)
├── models/
│   └── best_model.pkl       # Modèle ML entraîné
├── media/uploads/           # Images temporaires
└── requirements.txt
```

```
frontend-angular/
├── src/app/
│   ├── components/
│   │   ├── upload/          # Page upload drag & drop
│   │   ├── result/          # Page résultats diagnostic
│   │   └── history/         # Page historique
│   └── services/
│       └── diagnosis.ts     # Communication HTTP API
└── package.json
```

---

## Conseils de Capture (Meilleures Performances)

Pour des résultats optimaux :
- **Eclairage** : Temps nuageux ou lumière naturelle diffuse (éviter le flash)
- **Fond** : Papier blanc ou noir uni
- **Distance** : 20 à 30 cm de la feuille
- **Cadrage** : La feuille doit occuper 60–80% du cadre
- **Objectif** : Nettoyer l'objectif avant la prise de vue

---

## Dataset

Le modèle a été entraîné sur le dataset [PlantVillage](https://github.com/spMohanty/PlantVillage-Dataset).

---

## Auteur

**AMEKOUDJI Arvin** — Projet M2 IA Big Data & Data Science  
*Computer Vision — Détection de Maladies des Plantes de Tomates*
