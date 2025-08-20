import sys
import os
import gradio as gr
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import re
import unicodedata

# Ajouter le répertoire parent au path pour importer config
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import config

class PlayerSearchApp:
    def __init__(self):
        """Initialise l'application de recherche de joueurs"""
        # Initialiser les clients et modèles
        self.qdrant_client = QdrantClient(url='localhost')
        self.embedding_model = SentenceTransformer("BAAI/bge-m3")
        self.collection_name = 'ragscout_players'
        
        # Valider la configuration
        config.Config.validate()
        
    def extract_profil_type(self, summary: str) -> str | None:
        """Extrait le profil-type d'un résumé de joueur"""
        if not summary:
            return None
        
        m = re.search(r"Profil-type\s*:\s*(.+)", summary, flags=re.IGNORECASE)
        return m.group(1).strip() if m else None
    
    def strip_accents(self, s: str) -> str:
        """Supprime les accents d'une chaîne"""
        return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    
    def normalize_text(self, s: str) -> str:
        """Normalise le texte pour la comparaison"""
        s = self.strip_accents(s.lower())
        s = s.replace(' et ', ' ').replace(' de ', ' ')
        s = re.sub(r"[^\w\s\-+]", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s
    
    def canonical_tokens(self, s: str) -> set:
        """Extrait les tokens canoniques d'un texte"""
        s = self.normalize_text(s)
        s = s.replace("duels aeriens", "aerien").replace("jeu entre les lignes", "entre-lignes")
        return set(s.split())
    
    def soft_label(self, ref_profil: str | None, cand_profil: str | None) -> int:
        """
        Calcule un score de similarité entre deux profils
        2 = égal, 1 = au moins 1 token canonique partagé, 0 sinon
        """
        if not ref_profil or not cand_profil:
            return 0
        if self.normalize_text(ref_profil) == self.normalize_text(cand_profil):
            return 3
        if len(self.canonical_tokens(ref_profil) & self.canonical_tokens(cand_profil)) >= 3:
            return 2
        return 1 if len(self.canonical_tokens(ref_profil) & self.canonical_tokens(cand_profil)) >= 2 else 0
    
    def search_players(self, query: str, top_k: int = 5) -> list:
        """
        Recherche des joueurs basée sur une requête textuelle
        
        Args:
            query: Description du joueur recherché
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste des joueurs trouvés avec leurs informations
        """
        if not query.strip():
            return []
        
        try:
            # Encoder la requête
            query_vector = self.embedding_model.encode(query).tolist()
            
            # Rechercher dans Qdrant
            results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k
            )
            
            players = []
            for point in results.points:
                payload = point.payload or {}
                player_name = payload.get('player', 'Nom inconnu')
                summary = payload.get('summary', 'Aucune description disponible')
                profil_type = self.extract_profil_type(summary)
                
                # Calculer un score de pertinence basé sur la similarité des profils
                relevance_score = self.soft_label(query, profil_type)
                
                # Tronquer le résumé pour l'affichage
                short_summary = summary #[:300] + "..." if len(summary) > 300 else summary
                
                players.append({
                    'name': player_name,
                    'profil_type': profil_type or 'Profil non spécifié',
                    'summary': short_summary,
                    'full_summary': summary,
                    'relevance_score': relevance_score,
                    'similarity_score': point.score
                })
            
            # Trier par score de pertinence puis par score de similarité
            players.sort(key=lambda x: (x['relevance_score'], x['similarity_score']), reverse=True)
            
            return players
            
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return []
    
    def format_player_result(self, player: dict, index: int) -> str:
        """Formate un résultat de joueur pour l'affichage"""
        score_emoji = "🟢" if player['relevance_score'] >= 2 else "🟡" if player['relevance_score'] >= 1 else "🔴"
        
        return f"""
### {score_emoji} {index}. {player['name']}

**Profil-type:** {player['profil_type']}

**Description:** {player['summary']}

**Score de pertinence:** {player['relevance_score']}/3 | **Score de similarité:** {player['similarity_score']:.3f}

---
"""
    
    def search_interface(self, query: str, top_k: int) -> str:
        """
        Interface de recherche pour Gradio
        
        Args:
            query: Description du joueur recherché
            top_k: Nombre de résultats
            
        Returns:
            Résultats formatés en markdown
        """
        if not query.strip():
            return "Veuillez entrer une description de joueur pour commencer la recherche."
        
        players = self.search_players(query, top_k)
        
        if not players:
            return "Aucun joueur trouvé pour cette requête. Essayez de reformuler votre description."
        
        result_text = f"## Résultats de recherche pour: *{query}*\n\n"
        result_text += f"**{len(players)} joueur(s) trouvé(s)**\n\n"
        
        for i, player in enumerate(players, 1):
            result_text += self.format_player_result(player, i)
        
        return result_text

def create_gradio_interface():
    """Crée et lance l'interface Gradio"""
    app = PlayerSearchApp()
    
    # Interface Gradio
    with gr.Blocks(
        title="ScoutRAG - Recherche de Joueurs",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        """
    ) as interface:
        
        gr.Markdown("""
        # ⚽ ScoutRAG - Recherche de Joueurs
        
        Recherchez des joueurs de football en décrivant leurs caractéristiques, style de jeu ou profil recherché.
        
        **Exemples de requêtes:**
        - "défenseur central solide avec pressing intense"
        - "milieu créatif avec jeu entre les lignes"
        - "attaquant rapide avec finition"
        - "latéral offensif avec centres de qualité"
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                query_input = gr.Textbox(
                    label="Description du joueur recherché",
                    placeholder="Ex: défenseur central solide avec pressing intense et relance propre...",
                    lines=3
                )
                
                with gr.Row():
                    top_k_slider = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=5,
                        step=1,
                        label="Nombre de résultats"
                    )
                    search_btn = gr.Button("🔍 Rechercher", variant="primary")
            
            with gr.Column(scale=1):
                gr.Markdown("""
                ### 💡 Conseils
                
                - Soyez spécifique dans votre description
                - Mentionnez le poste et 2-3 caractéristiques clés
                - Utilisez des termes techniques: "pressing", "relance", "entre les lignes", etc.
                - Évitez les termes vagues comme "bon techniquement"
                """)
        
        results_output = gr.Markdown(
            label="Résultats",
            value="Entrez une description de joueur pour commencer la recherche..."
        )
        
        # Exemples de requêtes
        gr.Markdown("### 📝 Exemples de requêtes")
        examples = gr.Examples(
            examples=[
                ["défenseur central solide avec pressing intense et relance propre"],
                ["milieu central polyvalent avec capacité à jouer entre les lignes"],
                ["attaquant rapide avec finition et jeu de pointe"],
                ["latéral droit offensif avec centres de qualité"],
                ["gardien avec sorties aériennes et relance au pied"]
            ],
            inputs=query_input
        )
        
        # Événements
        search_btn.click(
            fn=app.search_interface,
            inputs=[query_input, top_k_slider],
            outputs=results_output
        )
        
        query_input.submit(
            fn=app.search_interface,
            inputs=[query_input, top_k_slider],
            outputs=results_output
        )
    
    return interface

if __name__ == "__main__":
    # Créer et lancer l'interface
    interface = create_gradio_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
