"""
Scraper pour WhoScored - Récupération de données de joueurs
"""

import time
import random
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import json
import re

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from ..models import Player
from ..config import Config

logger = logging.getLogger(__name__)

class WhoScoredScraper:
    """Scraper pour récupérer les données de joueurs depuis WhoScored"""
    
    def __init__(self, headless: bool = True, delay_range: tuple = (1, 3)):
        """Initialiser le scraper WhoScored"""
        self.base_url = "https://www.whoscored.com"
        self.session = requests.Session()
        self.delay_range = delay_range
        
        # Configuration des headers pour éviter la détection
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Configuration Selenium pour le scraping dynamique
        self.driver = None
        self.headless = headless
        self._setup_driver()
        
        logger.info("WhoScored scraper initialisé")
    
    def _setup_driver(self):
        """Configurer le driver Selenium"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Désactiver les images pour accélérer le chargement
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Driver Selenium configuré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la configuration du driver: {e}")
            self.driver = None
    
    def _random_delay(self):
        """Attendre un délai aléatoire pour éviter la détection"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def search_player(self, player_name: str) -> List[Dict[str, Any]]:
        """Rechercher un joueur par nom"""
        try:
            # URL de recherche WhoScored
            search_url = f"{self.base_url}/Search/?t={player_name}"
            
            if self.driver:
                return self._search_with_selenium(search_url)
            else:
                return self._search_with_requests(search_url)
                
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de {player_name}: {e}")
            return []
    
    def _search_with_selenium(self, search_url: str) -> List[Dict[str, Any]]:
        """Rechercher avec Selenium pour le contenu dynamique"""
        try:
            self.driver.get(search_url)
            self._random_delay()
            
            # Attendre que les résultats se chargent
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-result"))
            )
            
            # Extraire les résultats
            results = []
            search_results = self.driver.find_elements(By.CLASS_NAME, "search-result")
            
            for result in search_results[:5]:  # Limiter à 5 résultats
                try:
                    player_data = self._extract_player_from_search_result(result)
                    if player_data:
                        results.append(player_data)
                except Exception as e:
                    logger.warning(f"Erreur lors de l'extraction d'un résultat: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche Selenium: {e}")
            return []
    
    def _search_with_requests(self, search_url: str) -> List[Dict[str, Any]]:
        """Rechercher avec requests (fallback)"""
        try:
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Chercher les liens vers les profils de joueurs
            player_links = soup.find_all('a', href=re.compile(r'/Players/'))
            
            for link in player_links[:5]:
                try:
                    player_url = urljoin(self.base_url, link['href'])
                    player_data = self.get_player_profile(player_url)
                    if player_data:
                        results.append(player_data)
                except Exception as e:
                    logger.warning(f"Erreur lors de l'extraction d'un profil: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche requests: {e}")
            return []
    
    def _extract_player_from_search_result(self, result_element) -> Optional[Dict[str, Any]]:
        """Extraire les données d'un joueur depuis un résultat de recherche"""
        try:
            # Extraire le nom
            name_element = result_element.find_element(By.CSS_SELECTOR, "h3 a")
            name = name_element.text.strip()
            player_url = name_element.get_attribute('href')
            
            # Extraire les informations de base
            info_elements = result_element.find_elements(By.CSS_SELECTOR, ".search-result-info span")
            
            position = "Inconnu"
            club = "Inconnu"
            age = None
            
            for info in info_elements:
                text = info.text.strip()
                if "ans" in text or "years" in text:
                    age_match = re.search(r'(\d+)', text)
                    if age_match:
                        age = int(age_match.group(1))
                elif any(pos in text.lower() for pos in ['attaquant', 'milieu', 'défenseur', 'gardien']):
                    position = text
                else:
                    club = text
            
            return {
                "name": name,
                "position": position,
                "club": club,
                "age": age,
                "url": player_url
            }
            
        except Exception as e:
            logger.warning(f"Erreur lors de l'extraction des données de recherche: {e}")
            return None
    
    def get_player_profile(self, player_url: str) -> Optional[Dict[str, Any]]:
        """Récupérer le profil complet d'un joueur"""
        try:
            # Essayer d'abord avec requests et JSON
            profile_data = self._get_profile_with_requests_json(player_url)
            
            if profile_data:
                return profile_data
            
            # Fallback: utiliser Selenium si disponible
            if self.driver:
                return self._get_profile_with_selenium(player_url)
            else:
                return self._get_profile_with_requests(player_url)
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du profil: {e}")
            return None
    
    def _get_profile_with_requests_json(self, player_url: str) -> Optional[Dict[str, Any]]:
        """Récupérer le profil avec requests et extraction JSON"""
        try:
            response = self.session.get(player_url)
            response.raise_for_status()
            
            # Extraire les données JSON
            json_data = self._extract_json_from_html(response.text)
            
            if json_data:
                profile_data = self._parse_json_data(json_data)
                
                # Extraire le nom depuis le titre de la page
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title')
                if title:
                    name = title.text.strip().split(' Football Statistics')[0]
                    profile_data['name'] = name
                
                profile_data['url'] = player_url
                logger.info(f"Profil récupéré (JSON): {profile_data.get('name', 'Inconnu')}")
                return profile_data
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du profil JSON: {e}")
            return None
    
    def _extract_json_from_html(self, html_content: str) -> Optional[Dict[str, Any]]:
        """Extraire les données JSON depuis le HTML"""
        try:
            import re
            import json
            
            # Chercher le pattern JSON
            pattern = r'require\.config\.params\[\'args\'\]\s*=\s*({.*?});'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                
                # Nettoyer le JSON
                cleaned_json = self._clean_json_string(json_str)
                
                if cleaned_json:
                    data = json.loads(cleaned_json)
                    return data
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction JSON: {e}")
            return None
    
    def _clean_json_string(self, json_str: str) -> str:
        """Nettoyer la chaîne JSON"""
        try:
            import re
            
            # Supprimer les commentaires
            json_str = re.sub(r'//.*?\n', '\n', json_str)
            json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
            
            # Supprimer les virgules trailing
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            # Ajouter des guillemets aux propriétés sans guillemets
            json_str = re.sub(r'(\w+):', r'"\1":', json_str)
            
            return json_str
            
        except Exception as e:
            logger.error(f"Erreur nettoyage JSON: {e}")
            return ""
    
    def _get_profile_with_selenium(self, player_url: str) -> Optional[Dict[str, Any]]:
        """Récupérer le profil avec Selenium"""
        try:
            self.driver.get(player_url)
            self._random_delay()
            
            # Attendre que la page se charge
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "player-header"))
            )
            
            return self._extract_player_profile_data()
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du profil Selenium: {e}")
            return None
    
    def _get_profile_with_requests(self, player_url: str) -> Optional[Dict[str, Any]]:
        """Récupérer le profil avec requests"""
        try:
            response = self.session.get(player_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._extract_profile_from_soup(soup, player_url)
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du profil requests: {e}")
            return None
    
    def _extract_player_profile_data(self) -> Optional[Dict[str, Any]]:
        """Extraire les données du profil depuis la page Selenium"""
        try:
            # Extraire les données JSON depuis les scripts
            json_data = self._extract_json_data()
            
            if json_data:
                return self._parse_json_data(json_data)
            
            # Fallback: extraction HTML classique
            return self._extract_html_data()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données de profil: {e}")
            return None
    
    def _extract_json_data(self) -> Optional[Dict[str, Any]]:
        """Extraire les données JSON depuis les scripts de la page"""
        try:
            # Chercher le script contenant les données du joueur
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            
            for script in scripts:
                script_content = script.get_attribute('innerHTML')
                if script_content and 'require.config.params' in script_content:
                    # Extraire les données JSON
                    import re
                    import json
                    
                    # Chercher le pattern JSON
                    pattern = r'require\.config\.params\[\'args\'\]\s*=\s*({.*?});'
                    match = re.search(pattern, script_content, re.DOTALL)
                    
                    if match:
                        json_str = match.group(1)
                        try:
                            data = json.loads(json_str)
                            return data
                        except json.JSONDecodeError:
                            continue
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction JSON: {e}")
            return None
    
    def _parse_json_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parser les données JSON extraites"""
        try:
            # Extraire les informations du joueur depuis le JSON
            tournaments = data.get('tournaments', [])
            player_data = {}
            
            if tournaments:
                player_info = tournaments[0]  # Premier tournoi contient les infos du joueur
                
                player_data = {
                    "id": str(player_info.get('PlayerId', '')),
                    "name": player_info.get('Name', '').strip() or f"{player_info.get('FirstName', '')} {player_info.get('LastName', '')}".strip(),
                    "position": player_info.get('PositionText', ''),
                    "club": player_info.get('TeamName', ''),
                    "nationality": player_info.get('TeamRegionName', ''),
                    "age": player_info.get('Age', None),
                    "height": player_info.get('Height', None),
                    "weight": player_info.get('Weight', None),
                    "goals": player_info.get('Goals', 0),
                    "assists": player_info.get('Assists', 0),
                    "matches_played": player_info.get('GameStarted', 0) + player_info.get('SubOn', 0),
                    "rating": player_info.get('Rating', 0),
                    "yellow_cards": player_info.get('Yellow', 0),
                    "red_cards": player_info.get('Red', 0),
                    "total_passes": player_info.get('TotalPasses', 0),
                    "accurate_passes": player_info.get('AccuratePasses', 0),
                    "total_shots": player_info.get('TotalShots', 0),
                    "shots_on_target": player_info.get('ShotsOnTarget', 0),
                    "key_passes": player_info.get('KeyPasses', 0),
                    "dribbles": player_info.get('Dribbles', 0),
                    "total_tackles": player_info.get('TotalTackles', 0),
                    "interceptions": player_info.get('Interceptions', 0),
                    "fouls": player_info.get('Fouls', 0),
                    "offsides": player_info.get('Offsides', 0),
                    "clearances": player_info.get('TotalClearances', 0),
                    "was_dribbled": player_info.get('WasDribbled', 0),
                    "was_fouled": player_info.get('WasFouled', 0),
                    "dispossessed": player_info.get('Dispossesed', 0),
                    "turnovers": player_info.get('Turnovers', 0),
                    "total_crosses": player_info.get('TotalCrosses', 0),
                    "accurate_crosses": player_info.get('AccurateCrosses', 0),
                    "total_long_balls": player_info.get('TotalLongBalls', 0),
                    "accurate_long_balls": player_info.get('AccurateLongBalls', 0),
                    "total_through_balls": player_info.get('TotalThroughBalls', 0),
                    "accurate_through_balls": player_info.get('AccurateThroughBalls', 0),
                    "aerial_won": player_info.get('AerialWon', 0),
                    "aerial_lost": player_info.get('AerialLost', 0),
                    "man_of_match": player_info.get('ManOfTheMatch', 0)
                }
            
            return player_data
            
        except Exception as e:
            logger.error(f"Erreur lors du parsing JSON: {e}")
            return {}
    
    def _extract_html_data(self) -> Dict[str, Any]:
        """Extraction HTML classique (fallback)"""
        try:
            # Informations de base
            name = self._safe_get_text("h1")
            position = self._safe_get_text("[class*='position']")
            club = self._safe_get_text("[class*='club']")
            
            # Statistiques physiques
            height = self._extract_number(self._safe_get_text("[class*='height']"))
            weight = self._extract_number(self._safe_get_text("[class*='weight']"))
            
            # Âge
            age_text = self._safe_get_text("[class*='age']")
            age = self._extract_number(age_text)
            
            # Nationalité
            nationality = self._safe_get_text("[class*='nationality']")
            
            # Statistiques de performance
            goals = self._extract_number(self._safe_get_text("[class*='goals']"))
            assists = self._extract_number(self._safe_get_text("[class*='assists']"))
            matches = self._extract_number(self._safe_get_text("[class*='matches']"))
            
            return {
                "name": name,
                "position": position,
                "club": club,
                "age": age,
                "nationality": nationality,
                "height": height,
                "weight": weight,
                "goals": goals,
                "assists": assists,
                "matches_played": matches
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction HTML: {e}")
            return {}
    
    def _extract_profile_from_soup(self, soup: BeautifulSoup, url: str) -> Optional[Dict[str, Any]]:
        """Extraire les données du profil depuis BeautifulSoup"""
        try:
            # Extraire l'ID du joueur depuis l'URL
            player_id = self._extract_player_id_from_url(url)
            
            # Informations de base
            name = self._safe_get_text_soup(soup, ".player-header h1")
            position = self._safe_get_text_soup(soup, ".player-position")
            club = self._safe_get_text_soup(soup, ".player-club")
            
            # Autres informations...
            # (Implémentation similaire à _extract_player_profile_data)
            
            return {
                "id": player_id,
                "name": name,
                "position": position,
                "club": club,
                "url": url
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction depuis BeautifulSoup: {e}")
            return None
    
    def _safe_get_text(self, selector: str) -> str:
        """Récupérer le texte d'un élément de manière sécurisée (Selenium)"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except:
            return ""
    
    def _safe_get_text_soup(self, soup: BeautifulSoup, selector: str) -> str:
        """Récupérer le texte d'un élément de manière sécurisée (BeautifulSoup)"""
        try:
            element = soup.select_one(selector)
            return element.text.strip() if element else ""
        except:
            return ""
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extraire un nombre d'un texte"""
        if not text:
            return None
        
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else None
    
    def _extract_player_id_from_url(self, url: str) -> str:
        """Extraire l'ID du joueur depuis l'URL"""
        match = re.search(r'/Players/(\d+)/', url)
        return match.group(1) if match else f"player_{hash(url)}"
    
    def _extract_technical_attributes(self) -> Dict[str, Any]:
        """Extraire les attributs techniques du joueur"""
        attributes = {}
        
        # Sélecteurs pour les attributs techniques (à adapter selon la structure de WhoScored)
        attr_selectors = {
            "pace": ".attr-pace",
            "shooting": ".attr-shooting", 
            "passing": ".attr-passing",
            "dribbling": ".attr-dribbling",
            "defending": ".attr-defending",
            "physical": ".attr-physical"
        }
        
        for attr_name, selector in attr_selectors.items():
            try:
                value = self._extract_number(self._safe_get_text(selector))
                if value:
                    attributes[attr_name] = value
            except:
                continue
        
        return attributes
    
    def scrape_league_players(self, league_url: str, max_players: int = 100) -> List[Dict[str, Any]]:
        """Scraper les joueurs d'une ligue"""
        players = []
        
        try:
            if self.driver:
                self.driver.get(league_url)
                self._random_delay()
                
                # Attendre que la page se charge
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "player-list"))
                )
                
                # Trouver les liens vers les profils de joueurs
                player_links = self.driver.find_elements(By.CSS_SELECTOR, ".player-list a[href*='/Players/']")
                
                for i, link in enumerate(player_links[:max_players]):
                    try:
                        player_url = link.get_attribute('href')
                        player_data = self.get_player_profile(player_url)
                        
                        if player_data:
                            players.append(player_data)
                            logger.info(f"Joueur {i+1}/{min(len(player_links), max_players)}: {player_data.get('name', 'Inconnu')}")
                        
                        self._random_delay()
                        
                    except Exception as e:
                        logger.warning(f"Erreur lors du scraping du joueur {i+1}: {e}")
                        continue
            
            return players
            
        except Exception as e:
            logger.error(f"Erreur lors du scraping de la ligue: {e}")
            return players
    
    def close(self):
        """Fermer le driver Selenium"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver Selenium fermé")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 