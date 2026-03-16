@echo off
echo.
echo ########################################################
echo #   Lancement de ONP PREMIUM - Mode Local (Docker)     #
echo ########################################################
echo.

set CONTAINER_NAME=onp_premium_app

:: Vérifier si Docker est installé
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Docker n'est pas installe ou n'est pas dans le PATH.
    echo Veuillez installer Docker Desktop pour Windows.
    pause
    exit /b
)

:: Reconstruire et lancer le container
echo [1/2] Preparation de l'Image Docker...
docker-compose build

echo [2/2] Demarrage de l'application...
docker-compose up -d

echo.
echo ########################################################
echo #  APPLICATION LANCEE : http://localhost:8501          #
echo ########################################################
echo.
pause
