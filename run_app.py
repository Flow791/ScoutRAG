#!/usr/bin/env python3
"""
Script de lancement pour l'application ScoutRAG
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def main():
    """Lance l'application Gradio"""
    try:
        from gradio_app import create_gradio_interface
        
        print("🚀 Lancement de ScoutRAG...")
        print("📊 Connexion à la base de données vectorielle...")
        
        # Créer et lancer l'interface
        interface = create_gradio_interface()
        
        print("✅ Application prête !")
        print("🌐 Interface disponible sur: http://localhost:7860")
        print("⏹️  Appuyez sur Ctrl+C pour arrêter")
        
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("💡 Assurez-vous que toutes les dépendances sont installées:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        print("💡 Vérifiez que:")
        print("   - Qdrant est démarré (docker-compose up -d)")
        print("   - Les variables d'environnement sont configurées")
        sys.exit(1)

if __name__ == "__main__":
    main()
