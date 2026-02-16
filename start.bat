@echo off
REM Script de démarrage rapide ADOS pour Windows
REM Ce script configure et lance le système

echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║   🚀 AI-Native Data Operating System (ADOS)              ║
echo ║      Configuration et Démarrage Rapide                   ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou n'est pas dans le PATH
    echo.
    echo Téléchargez Python depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python détecté
echo.

REM Vérifier si l'environnement virtuel existe
if not exist "venv\" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Erreur lors de la création de l'environnement virtuel
        pause
        exit /b 1
    )
    echo ✓ Environnement virtuel créé
    echo.
)

REM Activer l'environnement virtuel
echo 🔄 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Vérifier si les dépendances sont installées
pip show pandas >nul 2>&1
if errorlevel 1 (
    echo 📥 Installation des dépendances...
    echo    Cela peut prendre quelques minutes...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Erreur lors de l'installation des dépendances
        pause
        exit /b 1
    )
    echo ✓ Dépendances installées
    echo.
)

REM Vérifier si le fichier .env existe
if not exist ".env" (
    echo ⚠️  Fichier .env non trouvé
    echo.
    
    if exist ".env.example" (
        echo 📝 Création du fichier .env depuis le template...
        copy .env.example .env >nul
        
        echo.
        echo ⚠️  IMPORTANT: Configurez votre clé API OpenAI
        echo    Ouvrez le fichier .env et remplacez:
        echo    OPENAI_API_KEY=your_openai_api_key_here
        echo    par votre vraie clé API
        echo.
        echo    Obtenez votre clé sur: https://platform.openai.com/api-keys
        echo.
        
        set /p continue="Appuyez sur Entrée après avoir configuré .env..."
    ) else (
        echo ❌ .env.example non trouvé
        pause
        exit /b 1
    )
)

REM Menu principal
:menu
echo.
echo ═══════════════════════════════════════════════════════════
echo                     MENU PRINCIPAL
echo ═══════════════════════════════════════════════════════════
echo.
echo  1. 🧪 Exécuter les tests du système
echo  2. 🖥️  Lancer l'interface CLI (ligne de commande)
echo  3. 🌐 Lancer l'interface Web (Chainlit)
echo  4. 🎯 Mode Démo (exemples automatiques)
echo  5. 📊 Voir le statut du système
echo  6. ❌ Quitter
echo.
set /p choice="Choisissez une option (1-6): "

if "%choice%"=="1" goto tests
if "%choice%"=="2" goto cli
if "%choice%"=="3" goto web
if "%choice%"=="4" goto demo
if "%choice%"=="5" goto status
if "%choice%"=="6" goto end

echo.
echo ⚠️  Option invalide
goto menu

:tests
echo.
echo 🧪 Exécution des tests...
echo ═══════════════════════════════════════════════════════════
python test_ados.py
pause
goto menu

:cli
echo.
echo 🖥️  Lancement de l'interface CLI...
echo ═══════════════════════════════════════════════════════════
echo.
python ados_main.py
goto menu

:web
echo.
echo 🌐 Lancement de l'interface Web Chainlit...
echo ═══════════════════════════════════════════════════════════
echo.
echo    L'interface s'ouvrira automatiquement dans votre navigateur
echo    URL: http://localhost:8000
echo.
echo    Appuyez sur Ctrl+C pour arrêter le serveur
echo.
chainlit run ados_interface.py
goto menu

:demo
echo.
echo 🎯 Lancement du mode démo...
echo ═══════════════════════════════════════════════════════════
echo.
python ados_main.py --demo
pause
goto menu

:status
echo.
echo 📊 Statut du système...
echo ═══════════════════════════════════════════════════════════
echo.
python -c "from ados_main import ADOS; ados = ADOS(); ados.show_system_status()"
pause
goto menu

:end
echo.
echo 👋 Au revoir !
echo.
deactivate
exit /b 0
