# Script de monitoring AI PACS
param(
    [switch]$Detailed = $false,
    [switch]$Services = $false,
    [switch]$Logs = $false
)

Write-Host "🔍 Monitoring AI PACS" -ForegroundColor Green

function Test-ServiceHealth {
    param([string]$ServiceName, [string]$Url)
    
    try {
        $response = Invoke-RestMethod -Uri $Url -TimeoutSec 5
        Write-Host "✅ $ServiceName : OK" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ $ServiceName : Erreur - $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Get-ContainerStats {
    Write-Host "`n📊 Statistiques des conteneurs:" -ForegroundColor Cyan
    $containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    Write-Host $containers
    
    if ($Detailed) {
        Write-Host "`n📈 Utilisation des ressources:" -ForegroundColor Yellow
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    }
}

function Get-ServiceLogs {
    Write-Host "`n📋 Logs récents des services:" -ForegroundColor Cyan
    Write-Host "--- API ---" -ForegroundColor Yellow
    docker-compose logs --tail=10 ai_pacs_app
    
    Write-Host "`n--- Base de données ---" -ForegroundColor Yellow  
    docker-compose logs --tail=10 postgres
    
    Write-Host "`n--- Worker IA ---" -ForegroundColor Yellow
    docker-compose logs --tail=10 ai_worker
}

# Tests de santé des services
Write-Host "`n🏥 Tests de santé:" -ForegroundColor Cyan
$apiHealth = Test-ServiceHealth "API REST" "http://localhost:8000/health"
$dicomHealth = Test-ServiceHealth "DICOM Status" "http://localhost:8000/api/v1/dicom/status"
$aiHealth = Test-ServiceHealth "IA Engine" "http://localhost:8000/api/v1/ai/status"

# Statistiques des conteneurs
if ($Services) {
    Get-ContainerStats
}

# Logs si demandés
if ($Logs) {
    Get-ServiceLogs
}

# Résumé global
Write-Host "`n📈 Résumé du monitoring:" -ForegroundColor Green
$totalServices = 3
$healthyServices = @($apiHealth, $dicomHealth, $aiHealth) | Where-Object { $_ -eq $true } | Measure-Object | Select-Object -ExpandProperty Count

Write-Host "Services opérationnels: $healthyServices/$totalServices" -ForegroundColor $(if($healthyServices -eq $totalServices) {"Green"} else {"Yellow"})

# Recommandations
if ($healthyServices -lt $totalServices) {
    Write-Host "`n⚠️  Recommandations:" -ForegroundColor Yellow
    Write-Host "- Vérifiez les logs avec: scripts\monitor.ps1 -Logs"
    Write-Host "- Redémarrez les services avec: scripts\deploy.ps1"
    Write-Host "- Vérifiez la configuration .env"
}

Write-Host "`n🎯 Monitoring terminé!" -ForegroundColor Green
