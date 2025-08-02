"""
Modèle de données pour les joueurs
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import date

@dataclass
class Player:
    """Modèle représentant un joueur de football"""
    
    # Informations de base
    id: str
    name: str
    age: int
    nationality: str
    club: str
    position: str
    
    # Statistiques physiques
    height: Optional[float] = None  # en cm
    weight: Optional[float] = None  # en kg
    
    # Statistiques de performance
    goals: Optional[int] = None
    assists: Optional[int] = None
    matches_played: Optional[int] = None
    minutes_played: Optional[int] = None
    
    # Attributs techniques
    pace: Optional[int] = None  # 1-100
    shooting: Optional[int] = None
    passing: Optional[int] = None
    dribbling: Optional[int] = None
    defending: Optional[int] = None
    physical: Optional[int] = None
    
    # Informations supplémentaires
    market_value: Optional[float] = None  # en millions d'euros
    contract_until: Optional[date] = None
    preferred_foot: Optional[str] = None  # "Right", "Left", "Both"
    
    # Métadonnées
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir le joueur en dictionnaire"""
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "nationality": self.nationality,
            "club": self.club,
            "position": self.position,
            "height": self.height,
            "weight": self.weight,
            "goals": self.goals,
            "assists": self.assists,
            "matches_played": self.matches_played,
            "minutes_played": self.minutes_played,
            "pace": self.pace,
            "shooting": self.shooting,
            "passing": self.passing,
            "dribbling": self.dribbling,
            "defending": self.defending,
            "physical": self.physical,
            "market_value": self.market_value,
            "contract_until": self.contract_until.isoformat() if self.contract_until else None,
            "preferred_foot": self.preferred_foot,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        """Créer un joueur à partir d'un dictionnaire"""
        return cls(**data)
    
    def get_technical_attributes(self) -> Dict[str, int]:
        """Obtenir les attributs techniques du joueur"""
        return {
            "pace": self.pace,
            "shooting": self.shooting,
            "passing": self.passing,
            "dribbling": self.dribbling,
            "defending": self.defending,
            "physical": self.physical
        }
    
    def get_average_rating(self) -> Optional[float]:
        """Calculer la note moyenne du joueur"""
        attributes = self.get_technical_attributes()
        valid_attributes = [attr for attr in attributes.values() if attr is not None]
        
        if not valid_attributes:
            return None
            
        return sum(valid_attributes) / len(valid_attributes) 