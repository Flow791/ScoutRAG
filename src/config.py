"""
Configuration du projet ScoutRAG
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Chemins du projet
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Créer les dossiers nécessaires
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

class Config:
    """Configuration principale de l'application"""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Application
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Sources de données
    PLAYERS_DATA_PATH = os.getenv("PLAYERS_DATA_PATH", str(DATA_DIR / "players_data.csv"))
    SCOUTING_REPORTS_PATH = os.getenv("SCOUTING_REPORTS_PATH", str(DATA_DIR / "scouting_reports"))
    
    @classmethod
    def validate(cls):
        """Valider la configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY est requis dans les variables d'environnement")
        
        return True 