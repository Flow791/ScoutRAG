#!/usr/bin/env python3
"""
Script de setup complet pour ScoutRAG
Automatise l'installation, la configuration et le lancement de l'application
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def run_command(command, description, check=True):
    """Exécute une commande avec gestion d'erreur"""
    print(f"\n🔄 {description}...")
    print(f"💻 Commande: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ Succès: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        if e.stderr:
            print(f"📝 Détails: {e.stderr.strip()}")
        return False

def check_docker():
    """Vérifie que Docker est installé et fonctionnel"""
    print("🐳 Vérification de Docker...")
    
    if not run_command("docker --version", "Vérification de Docker", check=False):
        print("❌ Docker n'est pas installé ou accessible")
        print("💡 Installez Docker depuis: https://docs.docker.com/get-docker/")
        return False
    
    if not run_command("docker-compose --version", "Vérification de Docker Compose", check=False):
        print("❌ Docker Compose n'est pas installé ou accessible")
        print("💡 Installez Docker Compose depuis: https://docs.docker.com/compose/install/")
        return False
    
    return True

def check_python_env():
    """Vérifie l'environnement Python"""
    print("🐍 Vérification de l'environnement Python...")
    
    # Vérifier Python
    if not run_command("python --version", "Vérification de Python", check=False):
        print("❌ Python n'est pas installé ou accessible")
        return False
    
    # Vérifier pip
    if not run_command("pip --version", "Vérification de pip", check=False):
        print("❌ pip n'est pas installé ou accessible")
        return False
    
    return True

def setup_environment():
    """Configure l'environnement de développement"""
    print("\n🔧 Configuration de l'environnement...")
    
    # Vérifier si .env existe
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Création du fichier .env...")
        env_content = """# Configuration ScoutRAG
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
DEBUG=True
LOG_LEVEL=INFO
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Fichier .env créé")
        print("⚠️ N'oubliez pas de configurer votre clé API OpenAI dans le fichier .env")
    else:
        print("✅ Fichier .env existe déjà")
    
    # Créer les dossiers nécessaires
    folders = ["data", "logs", "img"]
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
        print(f"✅ Dossier {folder} créé/vérifié")

def install_dependencies():
    """Installe les dépendances Python"""
    print("\n📦 Installation des dépendances...")
    
    if not run_command("pip install -r requirements.txt", "Installation des dépendances"):
        print("❌ Échec de l'installation des dépendances")
        return False
    
    return True

def start_qdrant():
    """Démarre Qdrant avec Docker"""
    print("\n🗄️ Démarrage de Qdrant...")
    
    # Vérifier si Qdrant est déjà en cours d'exécution
    if run_command("docker ps | grep qdrant", "Vérification de Qdrant", check=False):
        print("✅ Qdrant est déjà en cours d'exécution")
        return True
    
    # Démarrer Qdrant
    if not run_command("cd docker && docker-compose up -d", "Démarrage de Qdrant"):
        print("❌ Échec du démarrage de Qdrant")
        return False
    
    # Attendre que Qdrant soit prêt
    print("⏳ Attente du démarrage de Qdrant...")
    time.sleep(10)
    
    # Vérifier que Qdrant répond
    for i in range(30):  # 30 tentatives de 2 secondes = 1 minute
        if run_command("curl -s http://localhost:6333/collections", "Test de connexion Qdrant", check=False):
            print("✅ Qdrant est prêt")
            return True
        time.sleep(2)
    
    print("❌ Qdrant ne répond pas après 1 minute")
    return False

def run_data_pipeline():
    """Exécute le pipeline de données"""
    print("\n📊 Exécution du pipeline de données...")
    
    # Vérifier que la clé API OpenAI est configurée
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
        print("❌ Clé API OpenAI non configurée")
        print("💡 Configurez votre clé API dans le fichier .env")
        return False
    
    # Exécuter le pipeline
    if not run_command("cd src && python data_pipeline.py", "Exécution du pipeline de données"):
        print("❌ Échec du pipeline de données")
        return False
    
    return True

def test_application():
    """Teste l'application Gradio"""
    print("\n🧪 Test de l'application...")
    
    # Test simple de l'import
    test_script = """
import sys
sys.path.append('src')
try:
    from gradio_app import PlayerSearchApp
    app = PlayerSearchApp()
    print("✅ Application Gradio importée avec succès")
except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)
"""
    
    with open("test_app.py", "w") as f:
        f.write(test_script)
    
    success = run_command("python test_app.py", "Test de l'application")
    
    # Nettoyer
    Path("test_app.py").unlink(missing_ok=True)
    
    return success

def main():
    """Fonction principale du setup"""
    print("🎯 Setup complet de ScoutRAG")
    print("=" * 50)
    
    # Vérifications préliminaires
    if not check_docker():
        print("\n❌ Docker requis pour continuer")
        sys.exit(1)
    
    if not check_python_env():
        print("\n❌ Environnement Python requis pour continuer")
        sys.exit(1)
    
    # Configuration
    setup_environment()
    
    # Installation
    if not install_dependencies():
        print("\n❌ Échec de l'installation des dépendances")
        sys.exit(1)
    
    # Démarrage de Qdrant
    if not start_qdrant():
        print("\n❌ Échec du démarrage de Qdrant")
        sys.exit(1)
    
    # Pipeline de données (optionnel)
    print("\n🤔 Voulez-vous exécuter le pipeline de données maintenant ?")
    print("⚠️ Cela peut prendre plusieurs minutes et nécessite une clé API OpenAI")
    print("💡 Vous pouvez l'exécuter plus tard avec: cd src && python data_pipeline.py")
    
    response = input("Exécuter le pipeline maintenant ? (o/N): ").strip().lower()
    if response in ['o', 'oui', 'y', 'yes']:
        if not run_data_pipeline():
            print("\n⚠️ Pipeline de données échoué, mais l'application peut fonctionner avec des données existantes")
    
    # Test de l'application
    if not test_application():
        print("\n❌ Échec du test de l'application")
        sys.exit(1)
    
    # Résumé final
    print("\n" + "=" * 50)
    print("🎉 Setup ScoutRAG terminé avec succès !")
    print("\n📋 Prochaines étapes:")
    print("1. Configurez votre clé API OpenAI dans le fichier .env")
    print("2. Lancez l'application: python run_app.py")
    print("3. Accédez à l'interface: http://localhost:7860")
    print("\n📚 Documentation:")
    print("- README.md: Documentation générale")
    print("- APP_README.md: Documentation de l'application")
    print("\n🛠️ Commandes utiles:")
    print("- python run_app.py: Lancer l'application")
    print("- cd src && python data_pipeline.py: Exécuter le pipeline de données")
    print("- cd docker && docker-compose down: Arrêter Qdrant")

if __name__ == "__main__":
    main()
