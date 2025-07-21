# Script de déploiement DevOps pour Windows
param(
    [string]$Environment = "development",
    [switch]$Build = $false,
    [switch]$Clean = $false
)

Write-Host "🚀 Déploiement AI PACS - Environnement: $Environment" -ForegroundColor Green

# Nettoyage si demandé
if ($Clean) {
    Write-Host "🧹 Nettoyage des conteneurs et volumes..." -ForegroundColor Yellow
    docker-compose down -v --remove-orphans
    docker system prune -f
}

# Construction des images si demandé
if ($Build) {
    Write-Host "🔨 Construction des images Docker..." -ForegroundColor Blue
    docker-compose build --no-cache
}

# Vérification des dépendances
Write-Host "📋 Vérification des dépendances..." -ForegroundColor Cyan
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker n'est pas installé ou accessible"
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Error "Docker Compose n'est pas installé ou accessible"
    exit 1
}

# Vérification des fichiers de configuration
if (-not (Test-Path ".env")) {
    Write-Warning "Fichier .env manquant, copie depuis .env.example"
    Copy-Item ".env.example" ".env"
}

# Démarrage des services
Write-Host "🚀 Démarrage des services..." -ForegroundColor Green
$env:COMPOSE_PROJECT_NAME = "aipacs"

switch ($Environment) {
    "development" {
        $env:DEBUG = "true"
        $env:LOG_LEVEL = "DEBUG"
        docker-compose up --detach
    }
    "staging" {
        $env:DEBUG = "false"
        $env:LOG_LEVEL = "INFO"
        docker-compose -f docker-compose.yml -f docker-compose.staging.yml up --detach
    }
    "production" {
        $env:DEBUG = "false"
        $env:LOG_LEVEL = "WARNING"
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --detach
    }
    default {
        Write-Error "Environnement non reconnu: $Environment"
        exit 1
    }
}

# Attente du démarrage
Write-Host "⏳ Attente du démarrage des services..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test de santé
Write-Host "🏥 Test de santé de l'application..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    if ($response.status -eq "healthy") {
        Write-Host "✅ Application déployée avec succès!" -ForegroundColor Green
        Write-Host "🌐 API: http://localhost:8000/api/v1/docs" -ForegroundColor Blue
        Write-Host "📊 Dashboard: http://localhost:8000" -ForegroundColor Blue
    }
} catch {
    Write-Warning "❌ Échec du test de santé: $($_.Exception.Message)"
    Write-Host "📋 Vérifiez les logs avec: docker-compose logs"
}

Write-Host "🎉 Déploiement terminé!" -ForegroundColor Green
