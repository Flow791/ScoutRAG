import sys
import os
import gradio as gr
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, MatchAny, FieldCondition
import re
import unicodedata
import numpy as np
from rank_bm25 import BM25Okapi

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
        
        self._WORD_RE = re.compile(r"\w+", re.UNICODE)

        # Patterns simples pour déduire l'intention (position/ligue/âge)
        self.POS_PATTERNS = [
            (r"\b(gardien|goalkeeper|keeper|gb)\b", "GK"),
            (r"\b(défenseur central|defenseur central|central defender|centre[- ]back|dc)\b", "DF"),
            (r"\b(lat[eé]ral|lateral|full[- ]?back|back)\b", "DF"),
            (r"\b(milieu d[eé]fensif|6\b|defensive midfielder|dm)\b", "DM"),
            (r"\b(milieu (central|relayeur)|8\b|central midfielder|cm)\b", "CM"),
            (r"\b(meneur|num[eé]ro 10|numero 10|playmaker|am)\b", "AM"),
            (r"\b(ailier|wing(er)?|wide)\b", "AM"),
            (r"\b(avant[- ]centre|but(e)ur|buteur|striker|9\b|st)\b", "ST"),
        ]
        self.LEAGUE_MAP = {
            "premier league": "Premier League",
            "ligue 1": "Ligue 1",
            "la liga": "La Liga",
            "bundesliga": "Bundesliga",
            "serie a": "Serie A",
        }
        
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
    
    def _bm25_scores(self, query: str, docs: list[str]) -> np.ndarray:
        corpus_tokens = [self._tok(d) for d in docs]
        bm25 = BM25Okapi(corpus_tokens)
        return np.array(bm25.get_scores(self._tok(query)))
    
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

    def _infer_intent_from_query(self, query: str) -> dict:
        """Déduit des contraintes légères à partir de la requête (position, ligue, âge max)."""
        q = (query or "").lower()

        # position
        pos = None
        for pat, code in self.POS_PATTERNS:
            if re.search(pat, q):
                pos = code
                break

        # âge max (U23, U21, "moins de 25", "<= 25")
        age_max = None
        m = re.search(r"u(\d{2})", q)
        if m:
            age_max = int(m.group(1))
        else:
            m = re.search(r"(?:moins de|under|<=)\s*(\d{2})", q)
            if m:
                age_max = int(m.group(1))

        # ligue
        league = None
        for k, v in self.LEAGUE_MAP.items():
            if k in q:
                league = v
                break

        return {
            "position_std": pos,
            "age_max": age_max,
            "league": league,
        }

    def _make_qdrant_filter(self, intent: dict) -> Filter | None:
        """Construit un filtre Qdrant léger (actuellement sur position_std si détectée)."""
        must = []
        if intent.get("position_std"):
            must.append(
                FieldCondition(
                    key="position_std",
                    match=MatchAny(any=[intent["position_std"]])
                )
            )
        if not must:
            return None
        return Filter(must=must)

    def _tok(self, s: str):
        return self._WORD_RE.findall((s or "").lower())

    def _normalize_0_1(self, arr):
        arr = np.asarray(arr, dtype=float)
        if arr.size == 0:
            return arr
        mn, mx = float(np.min(arr)), float(np.max(arr))
        if mx - mn < 1e-12:
            return np.zeros_like(arr)  # tous égaux => neutre
        return (arr - mn) / (mx - mn + 1e-9)

    def _bm25_scores(self, query: str, docs: list[str]) -> np.ndarray:
        corpus_tokens = [self._tok(d) for d in docs]
        bm25 = BM25Okapi(corpus_tokens)
        return np.array(bm25.get_scores(self._tok(query)))

    def extract_profil_type(self, summary: str) -> str | None:
        if not summary:
            return None
        
        m = re.search(r"Profil-type\s*:\s*(.+)", summary, flags=re.IGNORECASE)
        return m.group(1).strip() if m else None
    
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
            
            # Intention et filtre (optionnel)
            intent = self._infer_intent_from_query(query)
            qdrant_filter = self._make_qdrant_filter(intent)

            # Rechercher dans Qdrant (pool élargi pour reranking hybride)
            dense_top_n = max(top_k * 5, 50)
            results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=dense_top_n,
                query_filter=qdrant_filter,
                with_payload=True
            )
            
            candidates = []
            for point in results.points:
                payload = point.payload or {}
                name = payload.get('player', 'Nom inconnu')
                summary = payload.get('summary', 'Aucune description disponible')
                short_summary = summary[:300] + "..." if len(summary) > 300 else summary
                profil_type = self.extract_profil_type(summary) or ""
                candidates.append({
                    "name": name,
                    "profil_type": profil_type,
                    "short_summary": short_summary,
                    "summary": summary,
                    "similarity_score_raw": float(point.score),
                    "position_std": payload.get("position_std", "UNK"),
                    "league": payload.get("league"),
                    "age": payload.get("age"),
                    "age_bucket": payload.get("age_bucket")
                })

            if not candidates:
                return []

            # BM25 sur (profil_type + résumé)
            bm25_docs = [
                f"{c['profil_type']} {c['summary']}".strip() for c in candidates
            ]
            bm25_scores = self._bm25_scores(query, bm25_docs)

            # Normalisation des signaux
            dense_scores = np.array([c['similarity_score_raw'] for c in candidates], dtype=float)
            dense_norm = self._normalize_0_1(dense_scores)
            bm25_norm = self._normalize_0_1(bm25_scores)

            # Fusion (alpha réglable)
            alpha = 0.75
            fused = alpha * dense_norm + (1.0 - alpha) * bm25_norm

            # Boosts en fonction de l'intention
            boosts = np.zeros_like(fused)
            for i, c in enumerate(candidates):
                b = 0.0
                if intent.get('position_std') and c.get('position_std') == intent['position_std']:
                    b += 0.03
                if intent.get('league') and c.get('league') == intent['league']:
                    b += 0.02
                if intent.get('age_max') and c.get('age') is not None:
                    try:
                        if int(c['age']) <= int(intent['age_max']):
                            b += 0.02
                    except Exception:
                        pass
                boosts[i] = b

            fused = fused + boosts

            # Ordonnancement par score fusionné
            order = np.argsort(-fused)
            ranked = []
            for idx in order[:top_k]:
                c = candidates[idx]
                full_summary = c['summary']
                short_summary = full_summary[:300] + "..." if len(full_summary) > 300 else full_summary
                ranked.append({
                    'name': c['name'],
                    'profil_type': c['profil_type'] or 'Profil non spécifié',
                    'short_summary': short_summary,
                    'summary': full_summary,
                    'similarity_score': float(c['similarity_score_raw']),
                    'bm25_score': float(bm25_norm[idx]),
                    'fused_score': float(fused[idx]),
                    'dense_score': float(dense_norm[idx]),
                    'position_std': c.get('position_std', ''),
                    'league': c.get('league'),
                    'age': c.get('age'),
                })

            return ranked
            
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return []
    
    def format_player_result(self, player: dict, index: int) -> str:
        """Formate un résultat de joueur pour l'affichage"""
        s = player.get("fused_score", 0.0)
        score_emoji = "🟢" if s >= 0.66 else ("🟡" if s >= 0.33 else "🔴")
        
        return f"""
### {score_emoji} {index}. {player['name']} ({player['position_std']}) - {player['age']} ans

**Profil-type:** {player['profil_type']}

**Description:** {player['short_summary']}

**Similar score :** {player['similarity_score']:.3f}

**Tri hybride:** fused=**{player.get('fused_score', 0):.3f}** | dense={player.get('dense_score', 0):.3f} | bm25={player.get('bm25_score', 0):.3f}

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
