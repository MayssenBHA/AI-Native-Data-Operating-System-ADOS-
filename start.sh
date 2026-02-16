#!/bin/bash
# Script de démarrage rapide ADOS pour Linux/Mac
# Ce script configure et lance le système

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   🚀 AI-Native Data Operating System (ADOS)              ║"
echo "║      Configuration et Démarrage Rapide                   ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    echo ""
    echo "Installation:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-venv python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

echo "✓ Python détecté: $(python3 --version)"
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "✓ Environnement virtuel créé"
    echo ""
fi

# Activer l'environnement virtuel
echo "🔄 Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier si les dépendances sont installées
if ! python -c "import pandas" &> /dev/null; then
    echo "📥 Installation des dépendances..."
    echo "   Cela peut prendre quelques minutes..."
    echo ""
    pip install -r requirements.txt
    echo "✓ Dépendances installées"
    echo ""
fi

# Vérifier si le fichier .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé"
    echo ""
    
    if [ -f ".env.example" ]; then
        echo "📝 Création du fichier .env depuis le template..."
        cp .env.example .env
        
        echo ""
        echo "⚠️  IMPORTANT: Configurez votre clé API OpenAI"
        echo "   Éditez le fichier .env et remplacez:"
        echo "   OPENAI_API_KEY=your_openai_api_key_here"
        echo "   par votre vraie clé API"
        echo ""
        echo "   Obtenez votre clé sur: https://platform.openai.com/api-keys"
        echo ""
        
        read -p "Appuyez sur Entrée après avoir configuré .env..."
    else
        echo "❌ .env.example non trouvé"
        exit 1
    fi
fi

# Fonction menu principal
show_menu() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "                     MENU PRINCIPAL"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "  1. 🧪 Exécuter les tests du système"
    echo "  2. 🖥️  Lancer l'interface CLI (ligne de commande)"
    echo "  3. 🌐 Lancer l'interface Web (Chainlit)"
    echo "  4. 🎯 Mode Démo (exemples automatiques)"
    echo "  5. 📊 Voir le statut du système"
    echo "  6. ❌ Quitter"
    echo ""
}

# Boucle principale
while true; do
    show_menu
    read -p "Choisissez une option (1-6): " choice
    
    case $choice in
        1)
            echo ""
            echo "🧪 Exécution des tests..."
            echo "═══════════════════════════════════════════════════════════"
            python test_ados.py
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        2)
            echo ""
            echo "🖥️  Lancement de l'interface CLI..."
            echo "═══════════════════════════════════════════════════════════"
            echo ""
            python ados_main.py
            ;;
        3)
            echo ""
            echo "🌐 Lancement de l'interface Web Chainlit..."
            echo "═══════════════════════════════════════════════════════════"
            echo ""
            echo "   L'interface s'ouvrira automatiquement dans votre navigateur"
            echo "   URL: http://localhost:8000"
            echo ""
            echo "   Appuyez sur Ctrl+C pour arrêter le serveur"
            echo ""
            chainlit run ados_interface.py
            ;;
        4)
            echo ""
            echo "🎯 Lancement du mode démo..."
            echo "═══════════════════════════════════════════════════════════"
            echo ""
            python ados_main.py --demo
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        5)
            echo ""
            echo "📊 Statut du système..."
            echo "═══════════════════════════════════════════════════════════"
            echo ""
            python -c "from ados_main import ADOS; ados = ADOS(); ados.show_system_status()"
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        6)
            echo ""
            echo "👋 Au revoir !"
            echo ""
            deactivate
            exit 0
            ;;
        *)
            echo ""
            echo "⚠️  Option invalide"
            ;;
    esac
done
