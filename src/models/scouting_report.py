"""
Modèle de données pour les rapports de scouting
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class ScoutingReport:
    """Modèle représentant un rapport de scouting"""
    
    # Informations de base
    id: str
    player_id: str
    scout_name: str
    report_date: datetime
    
    # Évaluation générale
    overall_rating: int  # 1-100
    potential_rating: int  # 1-100
    
    # Forces et faiblesses
    strengths: List[str]
    weaknesses: List[str]
    
    # Évaluation technique
    technical_skills: Dict[str, int]  # {"dribbling": 85, "passing": 78, ...}
    
    # Évaluation physique
    physical_attributes: Dict[str, int]  # {"pace": 90, "stamina": 75, ...}
    
    # Évaluation mentale
    mental_attributes: Dict[str, int]  # {"vision": 80, "leadership": 70, ...}
    
    # Recommandations
    recommendation: str  # "Sign", "Monitor", "Avoid"
    transfer_value: Optional[float] = None  # en millions d'euros
    
    # Notes détaillées
    detailed_notes: Optional[str] = None
    match_observations: Optional[str] = None
    
    # Métadonnées
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir le rapport en dictionnaire"""
        return {
            "id": self.id,
            "player_id": self.player_id,
            "scout_name": self.scout_name,
            "report_date": self.report_date.isoformat(),
            "overall_rating": self.overall_rating,
            "potential_rating": self.potential_rating,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "technical_skills": self.technical_skills,
            "physical_attributes": self.physical_attributes,
            "mental_attributes": self.mental_attributes,
            "recommendation": self.recommendation,
            "transfer_value": self.transfer_value,
            "detailed_notes": self.detailed_notes,
            "match_observations": self.match_observations,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScoutingReport":
        """Créer un rapport à partir d'un dictionnaire"""
        return cls(**data)
    
    def get_all_attributes(self) -> Dict[str, int]:
        """Obtenir tous les attributs évalués"""
        all_attrs = {}
        all_attrs.update(self.technical_skills)
        all_attrs.update(self.physical_attributes)
        all_attrs.update(self.mental_attributes)
        return all_attrs
    
    def get_average_technical_rating(self) -> float:
        """Calculer la note moyenne technique"""
        if not self.technical_skills:
            return 0.0
        return sum(self.technical_skills.values()) / len(self.technical_skills)
    
    def get_average_physical_rating(self) -> float:
        """Calculer la note moyenne physique"""
        if not self.physical_attributes:
            return 0.0
        return sum(self.physical_attributes.values()) / len(self.physical_attributes)
    
    def get_average_mental_rating(self) -> float:
        """Calculer la note moyenne mentale"""
        if not self.mental_attributes:
            return 0.0
        return sum(self.mental_attributes.values()) / len(self.mental_attributes) 