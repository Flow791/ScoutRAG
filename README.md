<div align="center">
  <img src="img/banner.png" alt="ScoutRAG Banner" width="100%">
  
  <br>
  
  <h1>ScoutRAG</h1>
  <p><strong>Assistant de scouting football basé sur l'IA générative avec interface web automatisée</strong></p>
  
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
  [![OpenAI](https://img.shields.io/badge/OpenAI-GPT-blue.svg)](https://openai.com)
  [![Gradio](https://img.shields.io/badge/Gradio-Interface-blue.svg)](https://gradio.app)
</div>

---

## 🇬🇧 Quick Overview (English)

### About ScoutRAG
ScoutRAG is an AI-powered football scouting assistant. Describe a player profile in natural language and retrieve the most relevant players via semantic search.

- Retrieval-Augmented approach: SentenceTransformer embeddings (BAAI/bge-m3) + vector DB (Qdrant)
- Gradio web UI for fast search in French or English
- Optional end-to-end data pipeline: fetch FBref stats → generate player summaries with OpenAI → index into Qdrant

### Key Features
- Natural-language search for player profiles
- Modern web UI (Gradio)
- Vector search with cosine similarity
- Automated pipeline to (re)build the index
- RAG evaluation notebooks (nDCG, LLM-as-judge)

### Tech Stack
- Embeddings: SentenceTransformer "BAAI/bge-m3" (1024 dims)
- Vector DB: Qdrant (`ragscout_players`, cosine)
- LLM: OpenAI (`OPENAI_MODEL`, default `gpt-4o-mini`) for summary generation
- UI: Gradio (`src/gradio_app.py`)
- Pipeline: `src/data_pipeline.py` (FBref → summaries → Qdrant)

### Prerequisites
- Python 3.8+
- Docker + Docker Compose
- OpenAI API key

## ⚡ Quick Start (EN)

```bash
# (optional) activate pyenv env if available
pyenv shell scout_rag_env

# 1) Install deps
pip install -r requirements.txt

# 2) Start Qdrant (vector DB)
cd docker && docker-compose up -d && cd ..

# 3) Launch Gradio app
python run_app.py
# if 7860 is taken:
GRADIO_SERVER_PORT=7861 python run_app.py

# 4) Open browser: http://localhost:7860

# 5) (optional) Rebuild data and index (long)
cd src && python data_pipeline.py
```

Useful commands:
- Check Qdrant: `docker ps | grep qdrant`
- List collections: `curl -s http://localhost:6333/collections`

## 🚀 Automated Setup (EN)

```bash
python setup_scoutrag.py
```
This script checks prerequisites, installs dependencies, starts Qdrant, optionally runs the data pipeline, and tests the app.

## 🚀 Manual Installation (EN)
```bash
git clone <repository-url>
cd ScoutRAG
pip install -r requirements.txt
cd docker && docker-compose up -d && cd ..
python run_app.py
```

## 🔄 Data Pipeline (EN) – Detailed

The end-to-end pipeline fetches stats, generates player summaries, computes embeddings, and stores everything into Qdrant.

### Overview
- Source: FBref via `soccerdata` (Big 5 European Leagues Combined)
- Season: 2024/25 (configurable in `src/data_pipeline.py`)
- Stat types: `standard`, `shooting`, `passing`, `defense`, `possession`, `misc`
- Embeddings: `SentenceTransformer("BAAI/bge-m3")` (1024 dimensions)
- Vector DB: Qdrant (`ragscout_players`, cosine distance)

### Steps
1) Fetch & merge stats → writes `data/players_stats.csv`
2) Generate player summaries with OpenAI (French), each ending with a line `Profil-type : …` → writes/updates `data/player_summaries.json`
3) Prepare dataset: merge stats + summaries, select columns `[league, season, player, team, position, summary]`
4) Qdrant setup: drop existing collection (if any), recreate `ragscout_players` with size 1024 + cosine
5) Encode summaries (BAAI/bge-m3) and upsert in batches (default 100) with payload:
   - `season, player, league, team, position, summary`

### Run
```bash
cd src
python data_pipeline.py
```
Requirements: `.env` with `OPENAI_API_KEY`. Note that generating thousands of summaries can take hours; consider running on a subset for quick tests.

## 📈 RAG Evaluation (EN)

Evaluation is provided in `src/notebooks/rag_evaluation.ipynb`:
- Generate realistic search queries from player summaries (OpenAI) and store them in `data/player_queries.json`
- Compute nDCG@k with graded gains:
  - 4 = exact expected player
  - 3 = equal profile (after normalization)
  - 2/1 = strong/weak token overlap on the extracted `Profil-type`
- “LLM as judge”: retrieve top-K candidates, ask the LLM to score relevance in {0,1,2,3}, then compute nDCG

Observed results (indicative): nDCG@3 ≈ 0.93, LLM-judge nDCG@5 ≈ 0.918.

## 📁 Project Structure (EN)

```
ScoutRAG/
├── src/
│   ├── gradio_app.py          # Gradio web app (semantic search)
│   ├── data_pipeline.py       # End-to-end data pipeline
│   ├── config.py              # App configuration (.env)
│   └── notebooks/
│       ├── scrapping_fbref.ipynb
│       ├── player_embedding.ipynb
│       ├── player_description.ipynb
│       └── rag_evaluation.ipynb
├── docker/
│   └── docker-compose.yaml    # Qdrant service
├── data/                      # Generated data
├── run_app.py                 # Launch Gradio interface
├── setup_scoutrag.py          # Automated setup (optional)
└── requirements.txt           # Dependencies
```

## 🛠 Useful Commands (EN)

```bash
# Start Qdrant
cd docker && docker-compose up -d

# Launch app (change port if needed)
python run_app.py
GRADIO_SERVER_PORT=7861 python run_app.py

# Rebuild pipeline (long)
cd src && python data_pipeline.py

# Inspect Qdrant
curl -s http://localhost:6333/collections
```

---

## 🎯 À propos de ScoutRAG

ScoutRAG est un assistant intelligent de scouting football qui révolutionne la recherche de joueurs grâce à l'intelligence artificielle. En combinant les technologies de LLM (Large Language Models) d'OpenAI avec la recherche vectorielle, ScoutRAG permet d'identifier rapidement des profils de joueurs correspondant à vos critères spécifiques, exprimés en langage naturel.

### 🎯 Public cible
- **Passionnés de data football** : Analysez les performances avec précision
- **Analystes de clubs** : Optimisez vos processus de recrutement
- **Entraîneurs** : Identifiez rapidement les joueurs adaptés à votre style de jeu

## ✨ Fonctionnalités principales

- 🔍 **Recherche en langage naturel** : Décrivez le profil recherché avec vos propres mots
- 🤖 **IA générative avancée** : Utilisation de GPT pour comprendre les requêtes complexes
- 📊 **Recherche vectorielle** : Analyse sémantique des profils de joueurs
- ⚡ **Résultats rapides** : Pipeline RAG optimisé pour des réponses instantanées
- 🎯 **Précision élevée** : Combinaison LLM + recherche vectorielle pour des résultats pertinents
- 🌐 **Interface web moderne** : Application Gradio intuitive et responsive
- 🔄 **Pipeline automatisé** : Récupération et traitement des données en une seule commande

## 🛠️ Technologies utilisées

- **OpenAI GPT** : Modèle de langage pour la compréhension des requêtes
- **Gradio** : Interface web moderne et responsive
- **Qdrant** : Base de données vectorielle pour la recherche sémantique
- **Sentence Transformers** : Modèle BAAI/bge-m3 pour les embeddings
- **SoccerData** : Récupération de données depuis FBref
- **Pipeline RAG** : Retrieval-Augmented Generation pour des réponses précises
- **Python** : Langage de développement principal

## 📋 Prérequis

- Python 3.8 ou supérieur
- Docker et Docker Compose
- Clé API OpenAI
- Connexion internet pour la récupération des données


## ⚡ Quick Start

```bash
# (facultatif) activer l'env pyenv si disponible
pyenv shell scout_rag_env

# 1) Installer les dépendances
pip install -r requirements.txt

# 2) Démarrer Qdrant (base vectorielle)
cd docker && docker-compose up -d && cd ..

# 3) Lancer l'interface Gradio
python run_app.py
# si le port 7860 est pris :
GRADIO_SERVER_PORT=7861 python run_app.py

# 4) Ouvrir le navigateur
# http://localhost:7860

# 5) (optionnel) Recréer les données et index (long)
cd src && python data_pipeline.py
```

Commandes utiles:
- Vérifier Qdrant: `docker ps | grep qdrant`
- Voir la collection: `curl -s http://localhost:6333/collections`


## 🚀 Installation et Configuration Automatisées

### Option 1: Setup Complet Automatisé (Recommandé)

```bash
# Cloner le projet
git clone <repository-url>
cd ScoutRAG

# Lancer le setup automatisé
python setup_scoutrag.py
```

Le script `setup_scoutrag.py` va automatiquement :
- ✅ Vérifier les prérequis (Docker, Python)
- ✅ Installer toutes les dépendances
- ✅ Configurer l'environnement
- ✅ Démarrer Qdrant
- ✅ Exécuter le pipeline de données (optionnel)
- ✅ Tester l'application

### Option 2: Installation Manuelle

Si vous préférez une installation manuelle, suivez les étapes ci-dessous.

## 🚀 Installation Manuelle

1. **Cloner le repository**
   ```bash
   git clone https://github.com/votre-username/ScoutRAG.git
   cd ScoutRAG
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer les variables d'environnement**
   ```bash
   # Le fichier .env sera créé automatiquement par setup_scoutrag.py
   # Ou créez-le manuellement avec votre clé API OpenAI
   ```

4. **Démarrer Qdrant**
   ```bash
   cd docker
   docker-compose up -d
   ```

5. **Exécuter le pipeline de données (optionnel)**
   ```bash
   cd src
   python data_pipeline.py
   ```

6. **Lancer l'application**
   ```bash
   python run_app.py
   ```

## 🌐 Utilisation de l'Interface Web

### Accès à l'application
L'application est accessible sur : **http://localhost:7860**

### Exemples de requêtes
- "défenseur central solide avec pressing intense et relance propre"
- "milieu central polyvalent avec capacité à jouer entre les lignes"
- "attaquant rapide avec finition et jeu de pointe"
- "latéral droit offensif avec centres de qualité"

### Fonctionnalités de l'interface
- **Recherche sémantique** : Trouvez des joueurs en décrivant leurs caractéristiques
- **Scores de pertinence** : Chaque résultat est évalué selon sa correspondance
- **Interface intuitive** : Saisie naturelle en français
- **Exemples intégrés** : Requêtes prêtes à utiliser

## 🔄 Pipeline de Données Automatisé

### Exécution complète
```bash
cd src
python data_pipeline.py
```

### Étapes du pipeline
1. **Récupération des données** : Scraping depuis FBref (Big 5 European Leagues)
2. **Génération des résumés** : Création de descriptions avec OpenAI GPT
3. **Préparation des données** : Fusion et nettoyage des données
4. **Configuration de Qdrant** : Création de la collection vectorielle
5. **Stockage des embeddings** : Insertion des vecteurs dans Qdrant

### Configuration du pipeline
- **Saison** : 2024-2025 (modifiable dans `data_pipeline.py`)
- **Ligues** : Big 5 European Leagues Combined
- **Types de stats** : standard, shooting, passing, defense, possession, misc
- **Modèle d'embedding** : BAAI/bge-m3 (1024 dimensions)

## 📊 Exemples de requêtes

- "Un milieu défensif robuste avec une bonne vision du jeu"
- "Attaquant rapide et technique, bon finisseur"
- "Défenseur central expérimenté, bon dans les duels aériens"
- "Gardien réactif avec de bons réflexes"

## 🕷️ Scraping de Données

### Sources de données
- **FBref** : Statistiques des joueurs des 5 grandes ligues européennes
- **SoccerData** : Bibliothèque Python pour la récupération de données football

### Fonctionnalités du scraper
- **Récupération automatique** : Toutes les statistiques en une fois
- **Fusion des données** : Combinaison de multiples types de statistiques
- **Nettoyage automatique** : Gestion des valeurs manquantes
- **Sauvegarde structurée** : Export au format CSV et JSON

## 🛠️ Commandes Utiles

```bash
# Setup complet automatisé
python setup_scoutrag.py

# Lancer l'application
python run_app.py

# Exécuter le pipeline de données
cd src && python data_pipeline.py

# Arrêter Qdrant
cd docker && docker-compose down

# Vérifier le statut de Qdrant
docker ps | grep qdrant
```

## 📁 Structure du Projet

```
ScoutRAG/
├── src/
│   ├── gradio_app.py          # Application Gradio
│   ├── data_pipeline.py       # Pipeline d'automatisation
│   ├── config.py              # Configuration
│   └── notebooks/             # Notebooks d'analyse
├── docker/
│   └── docker-compose.yaml    # Configuration Qdrant
├── data/                      # Données générées
├── setup_scoutrag.py          # Script de setup automatisé
├── run_app.py                 # Lancement de l'application
└── requirements.txt           # Dépendances Python
```


<div align="center">
  <p>Développé avec ❤️ pour la communauté football</p>
  <p><em>ScoutRAG - L'IA au service du scouting football</em></p>
</div> 