"""
Pipeline d'automatisation pour ScoutRAG
Récupère les données, les traite et les stocke dans Qdrant
"""

import sys
import os
import json
import pandas as pd
import soccerdata as sd
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, PayloadSchemaType
from tqdm import tqdm
import time
from openai import OpenAI

# Ajouter le répertoire parent au path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import config

class ScoutRAGPipeline:
    """Pipeline complet pour automatiser la récupération et le stockage des données"""
    
    def __init__(self):
        """Initialise le pipeline"""
        self.data_dir = Path("../data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialiser les clients
        self.openai_client = OpenAI(api_key=config.Config.OPENAI_API_KEY)
        self.qdrant_client = QdrantClient(url='localhost')
        self.embedding_model = SentenceTransformer("BAAI/bge-m3")
        
        # Configuration
        self.collection_name = 'ragscout_players'
        self.season = "2425"  # Saison 2024-2025
        
        print("🚀 Pipeline ScoutRAG initialisé")
    
    def step_1_scrape_data(self):
        """Étape 1: Récupération des données depuis FBref"""
        print("\n📊 Étape 1: Récupération des données FBref...")
        
        try:
            # Initialiser FBref
            fbref = sd.FBref(leagues="Big 5 European Leagues Combined", seasons=self.season)
            
            # Types de statistiques à récupérer
            stat_types = ['standard', 'shooting', 'passing', 'defense', 'possession', 'misc']
            dfs = []
            
            print("📈 Récupération des statistiques...")
            for stat in tqdm(stat_types, desc="Statistiques"):
                df = fbref.read_player_season_stats(stat_type=stat)
                
                # Flatten des colonnes MultiIndex
                df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
                
                # Définir les colonnes de jointure
                key_cols = [col for col in df.columns if any(k in col.lower() for k in ['player', 'season', 'team', 'comp'])]
                stat_cols = [col for col in df.columns if col not in key_cols]
                
                # Renommer les colonnes de stats
                df = df[key_cols + stat_cols]
                df = df.rename(columns={col: f"{col}_{stat}" for col in stat_cols})
                
                dfs.append(df)
            
            # Fusionner tous les DataFrames
            print("🔗 Fusion des données...")
            df_merged = pd.DataFrame()
            
            for df_temp in dfs:
                df_temp = df_temp.reset_index()
                if df_merged.empty:
                    df_merged = df_temp
                else:
                    df_merged = pd.merge(df_merged, df_temp, how='left', on=['league', 'season', 'team', 'player'])
            
            # Nettoyer et sauvegarder
            df_players = df_merged.reset_index()
            df_players = df_players.fillna(0)
            
            # Sauvegarder les données brutes
            output_path = self.data_dir / "players_stats.csv"
            df_players.to_csv(output_path, index=False)
            
            print(f"✅ Données sauvegardées: {output_path}")
            print(f"📊 {len(df_players)} joueurs récupérés")
            
            return df_players
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des données: {e}")
            raise
    
    def step_2_generate_summaries(self, df_players):
        """Étape 2: Génération des résumés de joueurs avec OpenAI"""
        print("\n🤖 Étape 2: Génération des résumés de joueurs...")
        
        # Charger les résumés existants s'ils existent
        summaries_path = self.data_dir / "player_summaries.json"
        if summaries_path.exists():
            print("📖 Chargement des résumés existants...")
            with open(summaries_path, "r", encoding="utf-8") as f:
                existing_summaries = json.load(f)
        else:
            existing_summaries = {}
           
        if len(existing_summaries) > 1:
            print("💡 Des données anterieures sont fournies voulez-vous vraiment mettre à jour ? (Durée: ~4h)")
        
            response = input("Rafraichir les données maintenant ? (o/N): ").strip().lower()
            if response not in ['o', 'oui', 'y', 'yes']:
                return existing_summaries
        
        # Préparer les données pour la génération
        players_to_process = []
        for _, row in df_players.iterrows():
            player_key = f"{row['player']} ({row['team']})"
            if player_key not in existing_summaries:
                print(player_key)
                players_to_process.append({
                    'player': row['player'],
                    'team': row['team'],
                    'position': row.get('pos__standard', 'Unknown'),
                    'stats': row.drop(exclude_columns).to_string()
                })
        
        
        exit()
        
        if not players_to_process:
            print("✅ Tous les résumés sont déjà générés")
            return existing_summaries
        
        print(f"🔄 Génération de {len(players_to_process)} nouveaux résumés...")
        
        # Prompt pour la génération de résumés
        exclude_columns = ['season', 'team', 'player', 'nation__standard', 'age__standard', 'born__standard', 'nation__shooting', 'pos__shooting', 'age__shooting', 'born__shooting', 'nation__passing', 'pos__passing', 'age__passing', 'born__passing', 'nation__defense', 'pos__defense', 'age__defense', 'born__defense', 'nation__possession', 'pos__possession', 'age__possession', 'born__possession', 'nation__misc', 'pos__misc', 'age__misc', 'born__misc']
        
        summary_prompt = """
        Tu es un expert en scouting football, analyste football spécialisé en scouting basé sur les données.
        
        Tu vas recevoir les statistiques détaillées d’un joueur professionnel.  
        À partir de ces données, rédige une **fiche de scouting complète, claire et neutre**, destinée à alimenter une base de recherche intelligente.

        ---

        ### 🎯 Objectif du texte :
        Identifier avec précision :
        - le **rôle du joueur** (poste et sous-rôle)
        - son **style de jeu** (comportement avec et sans ballon)
        - ses **principales qualités**
        - ses **axes d'amélioration**
        - son **profil-type** en fin de texte

        Le résumé doit permettre à un recruteur ou analyste d’avoir une **vision rapide mais fiable** du profil du joueur.

        ---
        
        ### ✍️ Structure attendue (fluide, sans titres ni bullets) :

        1. **Style de jeu et rôle** :  
        Décris le poste principal (DF, MF, FW…) et si possible, deduis des stats disponibles, le sous-rôle (ex : latéral offensif, milieu récupérateur, attaquant mobile).  
        Mentionne comment il évolue : projections, appels, conservation, pressing, largeur, implication défensive…  
        Base-toi uniquement sur les statistiques fournies.

        2. **Qualités principales** :  
        Regroupe par catégories :
        - **Physique** : volume de jeu, duels gagnés, présence, mobilité…
        - **Technique** : types de passes, créativité, conduite, finition, dribbles…
        - **Mental/tactique** : implication, pressing, discipline, concentration…

        3. **Axes d'amélioration** :  
        Exprime de manière neutre les domaines où il est moins à l’aise ou peut progresser.  
        Utilise des tournures comme “gagnerait à améliorer…”, “peut encore progresser sur…”, “montre quelques limites dans…”

        4. **Profil-type** :  
        Termine toujours par une ligne :  
        **Profil-type :** suivi d’une expression courte (3 à 6 mots) qui résume son profil.  
        (ex : “Milieu défensif intense”, “Défenseur axial sobre et solide”, “Ailier percutant et créatif”)

        ---

        ### ⚠️ Contraintes essentielles :

        - **Ne fais aucune déduction** à partir de données absentes (taille, puissance, nationalité, âge, etc.)
        - **N'invente jamais** une information
        - Ne donne aucun chiffre, pourcentage ou ratio
        - Texte fluide, sans bullet points, environ 6 à 8 phrases
        - Ne mentionne jamais le nom, le club, la ligue ou la nationalité du joueur

        ---
        
        IMPORTANT :
        - Ne déduis ni n’invente aucune donnée.
        - Si une information n’est pas présente dans les statistiques (comme la taille, la vitesse, la puissance, etc.), **n’en parle pas**.
        - Reste strictement fidèle aux données fournies.

        Voici les données du joueur :
        {stats}

        Résumé:
        """
        
        new_summaries = {}
        for player_data in tqdm(players_to_process, desc="Génération résumés"):
            try:
                # Préparer les statistiques pour le prompt
                stats_text = "\n".join([f"{k}: {v}" for k, v in player_data['stats'].items() 
                                       if k not in ['player', 'team', 'league', 'season'] and v != 0])
                
                prompt = summary_prompt.format(stats=stats_text)
                
                # Générer le résumé
                response = self.openai_client.chat.completions.create(
                    model=config.Config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "Tu es un expert en analyse footballistique."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                summary = response.choices[0].message.content.strip()
                player_key = f"{player_data['player']} ({player_data['team']})"
                new_summaries[player_key] = summary
                
                # Pause pour éviter de dépasser les limites API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️ Erreur pour {player_data['player']}: {e}")
                continue
        
        # Fusionner avec les résumés existants
        all_summaries = {**existing_summaries, **new_summaries}
        
        # Sauvegarder
        with open(summaries_path, "w", encoding="utf-8") as f:
            json.dump(all_summaries, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {len(new_summaries)} nouveaux résumés générés")
        print(f"📝 Total: {len(all_summaries)} résumés")
        
        return all_summaries
    
    def step_3_prepare_data(self, df_players, summaries):
        """Étape 3: Préparation des données pour Qdrant"""
        print("\n🔧 Étape 3: Préparation des données...")
        
        # Créer DataFrame des résumés
        df_summaries = pd.DataFrame([
            {
                'player': player.split('(')[0].strip(), 
                'team': player.split('(')[1].replace(')', '').strip(), 
                'summary': summary
            } 
            for player, summary in summaries.items()
        ])
        
        # Fusionner avec les statistiques
        df_merged = df_summaries.merge(df_players, how='left', on=['player', 'team'])
        
        # Sélectionner les colonnes importantes
        df_final = df_merged[[
            'league', 'season', 'player', 'team', 'pos__standard', 'summary'
        ]].copy()
        
        df_final.rename(columns={'pos__standard': 'position'}, inplace=True)
        df_final = df_final.dropna(subset=['summary'])  # Supprimer les lignes sans résumé
        
        print(f"✅ {len(df_final)} joueurs préparés pour Qdrant")
        
        return df_final
    
    def step_4_setup_qdrant(self):
        """Étape 4: Configuration de Qdrant"""
        print("\n🗄️ Étape 4: Configuration de Qdrant...")
        
        # Vérifier si la collection existe
        if self.qdrant_client.collection_exists(self.collection_name):
            print(f"🗑️ Suppression de la collection existante: {self.collection_name}")
            self.qdrant_client.delete_collection(self.collection_name)
        
        # Créer la nouvelle collection
        print(f"📦 Création de la collection: {self.collection_name}")
        self.qdrant_client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=1024,  # Taille des embeddings BAAI/bge-m3
                distance=Distance.COSINE
            )
        )
        
        print("✅ Collection Qdrant configurée")
        
        
    FBREF_TO_STD = {
        "GK": "GK",
        "DF": "DF",
        "DF,MF": "DM",
        "MF,DF": "DM",
        "MF": "CM",
        "MF,FW": "AM",
        'FW,MF': 'AM',
        "FW": "ST",
        'DF,FW': 'DF',
        'FW,DF': 'DF'
    }

    def normalize_position(self, raw_pos: str) -> str:
        if not raw_pos:
            return "UNK"
        raw = raw_pos.strip().upper()
        return self.FBREF_TO_STD.get(raw, raw[:2])

    def age_bucket(self, age: int) -> str:
        if age is None:
            return "unknown"
        if age <= 21: return "U21"
        if age <= 23: return "U23"
        if age <= 25: return "U25"
        if age <= 28: return "U28"
        if age <= 32: return "U32"
        return "32+"
    
    def step_5_store_embeddings(self, df_final):
        """Étape 5: Stockage des embeddings dans Qdrant"""
        print("\n💾 Étape 5: Stockage des embeddings...")
        
        points = []
        print("🔄 Génération des embeddings...")
        
        for idx, row in tqdm(df_final.iterrows(), total=len(df_final), desc="Embeddings"):
            try:
                # Générer l'embedding
                embedding = self.embedding_model.encode(
                    row['summary'],
                    normalize_embeddings=True
                ).tolist()
                
                pos_std = self.normalize_position(getattr(row, "position", ""))
                nat = getattr(row, "nationality", "")
                age = getattr(row, "age", None)
                try:
                    age = int(age) if age is not None and str(age).isdigit() else None
                except:
                    age = None
                
                metadata = {
                    'season': row['season'],
                    'player': row['player'],
                    'position_std': pos_std,
                    'age': age,
                    'age_bucket': self.age_bucket(age),
                    'nationality': nat,
                    'league': row['league'],
                    'team': row['team'],
                    'position': row['position'],
                    'summary': row['summary'],
                }
                
                # Créer le point
                point = PointStruct(
                    id=idx,
                    vector=embedding,
                    payload=metadata
                )
                
                points.append(point)
                
            except Exception as e:
                print(f"⚠️ Erreur pour {row['player']}: {e}")
                continue
        
        # Insérer par batch
        BATCH_SIZE = 100
        print("📤 Insertion dans Qdrant...")
        
        for i in tqdm(range(0, len(points), BATCH_SIZE), desc="Insertion"):
            batch = points[i:i + BATCH_SIZE]
            self.qdrant_client.upsert(
                collection_name=self.collection_name, 
                points=batch
            )
            
        self.qdrant_client.create_payload_index(
            collection_name="ragscout_players",
            field_name="position_std",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        self.qdrant_client.create_payload_index(
            collection_name="ragscout_players",
            field_name="league",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        self.qdrant_client.create_payload_index(
            collection_name="ragscout_players",
            field_name="season",
            field_schema=PayloadSchemaType.INTEGER,
        )
        self.qdrant_client.create_payload_index(
            collection_name="ragscout_players",
            field_name="age",
            field_schema=PayloadSchemaType.INTEGER,
        )
        self.qdrant_client.create_payload_index(
            collection_name="ragscout_players",
            field_name="age_bucket",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        
        print(f"✅ {len(points)} joueurs insérés dans Qdrant")
    
    def run_full_pipeline(self):
        """Exécute le pipeline complet"""
        print("🎯 Démarrage du pipeline ScoutRAG complet")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            # Étape 1: Récupération des données
            df_players = self.step_1_scrape_data()
            
            # Étape 2: Génération des résumés
            summaries = self.step_2_generate_summaries(df_players)
            
            # Étape 3: Préparation des données
            df_final = self.step_3_prepare_data(df_players, summaries)
            
            # Étape 4: Configuration de Qdrant
            self.step_4_setup_qdrant()
            
            # Étape 5: Stockage des embeddings
            self.step_5_store_embeddings(df_final)
            
            # Résumé final
            end_time = time.time()
            duration = end_time - start_time
            
            print("\n" + "=" * 50)
            print("🎉 Pipeline terminé avec succès !")
            print(f"⏱️ Durée totale: {duration:.2f} secondes")
            print(f"📊 {len(df_final)} joueurs traités")
            print(f"🗄️ Collection Qdrant: {self.collection_name}")
            print("🚀 L'application Gradio est prête à être utilisée !")
            
        except Exception as e:
            print(f"\n❌ Erreur dans le pipeline: {e}")
            raise

def main():
    """Fonction principale"""
    try:
        # Valider la configuration
        config.Config.validate()
        
        # Créer et exécuter le pipeline
        pipeline = ScoutRAGPipeline()
        pipeline.run_full_pipeline()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
