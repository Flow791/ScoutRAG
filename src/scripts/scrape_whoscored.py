#!/usr/bin/env python3
"""
Script pour scraper des données de joueurs depuis WhoScored
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Ajouter le dossier src au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scrapers import WhoScoredScraper
# from src.rag import ScoutRAG  # Commenté pour l'instant

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def scrape_player_by_name(player_name: str, headless: bool = True) -> List[Dict[str, Any]]:
    """Scraper un joueur par son nom"""
    print(f"🔍 Recherche du joueur: {player_name}")
    
    with WhoScoredScraper(headless=headless) as scraper:
        results = scraper.search_player(player_name)
        
        if results:
            print(f"✅ {len(results)} résultat(s) trouvé(s)")
            for i, player in enumerate(results, 1):
                print(f"\n{i}. {player.get('name', 'N/A')}")
                print(f"   Position: {player.get('position', 'N/A')}")
                print(f"   Club: {player.get('club', 'N/A')}")
                print(f"   Âge: {player.get('age', 'N/A')} ans")
                if player.get('url'):
                    print(f"   URL: {player['url']}")
        else:
            print("❌ Aucun résultat trouvé")
        
        return results

def scrape_player_profile(player_url: str, headless: bool = True) -> Dict[str, Any]:
    """Scraper le profil complet d'un joueur"""
    print(f"📊 Récupération du profil: {player_url}")
    
    with WhoScoredScraper(headless=headless) as scraper:
        profile = scraper.get_player_profile(player_url)
        
        if profile:
            print("✅ Profil récupéré avec succès")
            print(f"Nom: {profile.get('name', 'N/A')}")
            print(f"Position: {profile.get('position', 'N/A')}")
            print(f"Club: {profile.get('club', 'N/A')}")
            print(f"Âge: {profile.get('age', 'N/A')} ans")
            print(f"Nationalité: {profile.get('nationality', 'N/A')}")
            print(f"Taille: {profile.get('height', 'N/A')} cm")
            print(f"Poids: {profile.get('weight', 'N/A')} kg")
            print(f"Buts: {profile.get('goals', 'N/A')}")
            print(f"Passes décisives: {profile.get('assists', 'N/A')}")
            print(f"Matches joués: {profile.get('matches_played', 'N/A')}")
            
            # Attributs techniques
            technical_attrs = ['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physical']
            print("\nAttributs techniques:")
            for attr in technical_attrs:
                value = profile.get(attr)
                if value:
                    print(f"  {attr.capitalize()}: {value}/100")
        else:
            print("❌ Impossible de récupérer le profil")
        
        return profile

def scrape_league_players(league_url: str, max_players: int = 50, headless: bool = True) -> List[Dict[str, Any]]:
    """Scraper les joueurs d'une ligue"""
    print(f"🏆 Scraping de la ligue: {league_url}")
    print(f"Nombre maximum de joueurs: {max_players}")
    
    with WhoScoredScraper(headless=headless) as scraper:
        players = scraper.scrape_league_players(league_url, max_players)
        
        print(f"✅ {len(players)} joueurs récupérés")
        
        # Sauvegarder les données
        output_file = Path("data") / "scraped_players.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(players, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Données sauvegardées dans: {output_file}")
        
        return players

def add_players_to_scoutrag(players: List[Dict[str, Any]]):
    """Ajouter les joueurs scrapés à ScoutRAG"""
    print(f"🤖 Ajout de {len(players)} joueurs à ScoutRAG")
    print("⚠️  Fonctionnalité ScoutRAG désactivée pour l'instant")
    
    # Sauvegarder les données en JSON à la place
    output_file = Path("data") / "scraped_players.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Données sauvegardées dans: {output_file}")
    
    # try:
    #     scout_rag = ScoutRAG()
    #     
    #     # Préparer les données pour ScoutRAG
    #     formatted_players = []
    #     for player in players:
    #         # Ajouter un ID unique si absent
    #         if 'id' not in player:
    #             player['id'] = f"whoscored_{hash(player.get('name', ''))}"
    #         
    #         formatted_players.append(player)
    #     
    #     # Ajouter à la base de données
    #     scout_rag.add_players_to_database(formatted_players)
    #     
    #     # Afficher les statistiques mises à jour
    #     stats = scout_rag.get_database_stats()
    #     print(f"✅ Base de données mise à jour: {stats['total_players']} joueurs")
    #     
    # except Exception as e:
    #     logger.error(f"Erreur lors de l'ajout à ScoutRAG: {e}")
    #     print(f"❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("🏈 ScoutRAG - Scraper WhoScored")
    print("=" * 40)
    
    while True:
        print("\nOptions disponibles:")
        print("1. Rechercher un joueur par nom")
        print("2. Récupérer le profil d'un joueur (URL)")
        print("3. Scraper les joueurs d'une ligue")
        print("4. Charger des données depuis un fichier JSON")
        print("5. Quitter")
        
        choice = input("\nVotre choix (1-5): ").strip()
        
        if choice == "1":
            player_name = input("Nom du joueur: ").strip()
            if player_name:
                results = scrape_player_by_name(player_name)
                
                # Demander si on veut récupérer le profil complet
                if results:
                    try:
                        choice_idx = int(input("\nEntrez le numéro du joueur pour récupérer son profil (0 pour passer): ")) - 1
                        if 0 <= choice_idx < len(results):
                            player_url = results[choice_idx].get('url')
                            if player_url:
                                profile = scrape_player_profile(player_url)
                                if profile:
                                    # Demander si on veut l'ajouter à ScoutRAG
                                    add_to_rag = input("\nAjouter ce joueur à ScoutRAG? (o/n): ").strip().lower()
                                    if add_to_rag == 'o':
                                        add_players_to_scoutrag([profile])
                    except ValueError:
                        print("Choix invalide")
        
        elif choice == "2":
            player_url = input("URL du profil du joueur: ").strip()
            if player_url:
                profile = scrape_player_profile(player_url)
                if profile:
                    add_to_rag = input("\nAjouter ce joueur à ScoutRAG? (o/n): ").strip().lower()
                    if add_to_rag == 'o':
                        add_players_to_scoutrag([profile])
        
        elif choice == "3":
            league_url = input("URL de la ligue: ").strip()
            if league_url:
                try:
                    max_players = int(input("Nombre maximum de joueurs (défaut: 50): ").strip() or "50")
                    players = scrape_league_players(league_url, max_players)
                    
                    if players:
                        add_to_rag = input("\nAjouter ces joueurs à ScoutRAG? (o/n): ").strip().lower()
                        if add_to_rag == 'o':
                            add_players_to_scoutrag(players)
                except ValueError:
                    print("Nombre invalide")
        
        elif choice == "4":
            file_path = input("Chemin vers le fichier JSON: ").strip()
            if file_path and Path(file_path).exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        players = json.load(f)
                    
                    print(f"📁 {len(players)} joueurs chargés depuis {file_path}")
                    add_to_rag = input("Ajouter ces joueurs à ScoutRAG? (o/n): ").strip().lower()
                    if add_to_rag == 'o':
                        add_players_to_scoutrag(players)
                        
                except Exception as e:
                    print(f"❌ Erreur lors du chargement: {e}")
            else:
                print("❌ Fichier non trouvé")
        
        elif choice == "5":
            print("Au revoir! 👋")
            break
        
        else:
            print("Choix invalide. Veuillez choisir 1-5.")

if __name__ == "__main__":
    main() 