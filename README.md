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

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📞 Support

Pour toute question ou suggestion :
- Ouvrir une [issue](https://github.com/votre-username/ScoutRAG/issues)
- Consulter la documentation : `APP_README.md`
- Contacter l'équipe de développement

---

<div align="center">
  <p>Développé avec ❤️ pour la communauté football</p>
  <p><em>ScoutRAG - L'IA au service du scouting football</em></p>
</div> 