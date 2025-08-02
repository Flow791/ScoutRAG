<div align="center">
  <img src="img/banner.png" alt="ScoutRAG Banner" width="100%">
  
  <br>
  
  <h1>ScoutRAG</h1>
  <p><strong>Assistant de scouting football basé sur l'IA générative</strong></p>
  
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
  [![OpenAI](https://img.shields.io/badge/OpenAI-GPT-blue.svg)](https://openai.com)
</div>

---

## 🚀 À propos de ScoutRAG

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

## 🛠️ Technologies utilisées

- **OpenAI GPT** : Modèle de langage pour la compréhension des requêtes
- **Recherche vectorielle** : Analyse sémantique des données
- **Pipeline RAG** : Retrieval-Augmented Generation pour des réponses précises
- **Web Scraping** : Récupération de données depuis WhoScored
- **Selenium** : Automatisation du navigateur pour le scraping
- **Python** : Langage de développement principal

## 📋 Prérequis

- Python 3.8 ou supérieur
- Clé API OpenAI
- Base de données de joueurs (à configurer)

## 🚀 Installation

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
   cp .env.example .env
   # Éditer .env avec votre clé API OpenAI
   ```

4. **Lancer l'application**
   ```bash
   python main.py
   ```

## 💡 Utilisation

### Scraping de données depuis WhoScored

```python
# Scraper un joueur par nom
from src.scrapers import WhoScoredScraper

with WhoScoredScraper() as scraper:
    # Rechercher un joueur
    results = scraper.search_player("Kylian Mbappé")
    
    # Récupérer le profil complet
    if results:
        profile = scraper.get_player_profile(results[0]['url'])
        print(f"Profil récupéré: {profile['name']}")
```

### Recherche de joueurs avec RAG

```python
# Exemple de requête en langage naturel
requete = "Je cherche un attaquant rapide, bon dribbleur, âgé de 20-25 ans"
resultats = scoutrag.rechercher_joueurs(requete)
```

### Profils de recherche supportés

- **Attaquants** : Buteurs, ailier, attaquant de pointe
- **Milieux** : Récupérateur, relayeur, meneur de jeu
- **Défenseurs** : Central, latéral, libéro
- **Gardien** : Gardien de but

## 📊 Exemples de requêtes

- "Un milieu défensif robuste avec une bonne vision du jeu"
- "Attaquant rapide et technique, bon finisseur"
- "Défenseur central expérimenté, bon dans les duels aériens"
- "Gardien réactif avec de bons réflexes"

## 🕷️ Scraping WhoScored

### Script de scraping

```bash
# Lancer le script de scraping interactif
python scripts/scrape_whoscored.py
```

### Fonctionnalités du scraper

- **Recherche par nom** : Trouver des joueurs par leur nom
- **Profil complet** : Récupérer toutes les données d'un joueur
- **Scraping de ligue** : Récupérer les joueurs d'une ligue entière
- **Intégration ScoutRAG** : Ajouter automatiquement les données à la base
- **Sauvegarde JSON** : Exporter les données au format JSON

### Exemples d'utilisation

```python
# Scraper un joueur spécifique
scraper = WhoScoredScraper()
results = scraper.search_player("Erling Haaland")
profile = scraper.get_player_profile(results[0]['url'])

# Scraper une ligue
players = scraper.scrape_league_players("https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League", 50)
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
- Contacter l'équipe de développement

---

<div align="center">
  <p>Développé avec ❤️ pour la communauté football</p>
  <p><em>ScoutRAG - L'IA au service du scouting football</em></p>
</div> 