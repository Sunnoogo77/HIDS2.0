# stop-all.ps1 — Arrête l'API & vérifie qu'il ne reste rien

$ErrorActionPreference = "SilentlyContinue"

function Title($t){ Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Ok($m){ Write-Host "✔ $m" -ForegroundColor Green }
function Warn($m){ Write-Host "! $m" -ForegroundColor Yellow }
function Fail($m){ Write-Host "✘ $m" -ForegroundColor Red }

Title "Docker: stop & down"
# Stop + Down (sans supprimer volumes)
docker-compose stop api | Out-Null
docker-compose down | Out-Null
Ok "docker-compose down exécuté"

Title "Docker: conteneurs restants"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Title "Vérification du port 8000"
$net = netstat -ano | findstr ":8000"
if ($net) {
  Warn "Le port 8000 a encore des listeners :"
  $net | Write-Host
  $pids = ($net -split "\s+") | Where-Object { $_ -match "^\d+$" } | Select-Object -Unique
  if ($pids.Count -gt 0) {
    Write-Host "Tentative d'arrêt des PIDs: $($pids -join ', ')"
    foreach($pid in $pids){ try { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } catch {} }
    Start-Sleep -Seconds 1
    $net2 = netstat -ano | findstr ":8000"
    if ($net2) { Fail "Le port 8000 est encore occupé."; $net2 | Write-Host } else { Ok "Port 8000 libéré." }
  }
} else {
  Ok "Port 8000 libre."
}

Title "Process locaux uvicorn/python (si lancés hors Docker)"
$procs = Get-Process python,uvicorn -ErrorAction SilentlyContinue
if ($procs) {
  Warn "Process locaux détectés :"
  $procs | Select-Object Id, ProcessName, CPU, StartTime | Format-Table
  Write-Host "→ Si c'est votre API locale, vous pouvez les stopper :"
  Write-Host "   Stop-Process -Id <PID> -Force"
} else {
  Ok "Aucun processus python/uvicorn local détecté."
}

Title "État final"
Write-Host "Containers actifs:" -NoNewline; Write-Host ""
docker ps --format "table {{.Names}}\t{{.Status}}"
Write-Host "Port 8000:" -NoNewline; Write-Host ""
netstat -ano | findstr ":8000"
Ok "Arrêt & vérifications terminés."
