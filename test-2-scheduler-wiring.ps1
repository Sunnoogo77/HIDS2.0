# test-2-scheduler-wiring.ps1 — Vérifie l’intégration APScheduler + activité (minutely)

$ErrorActionPreference = "Stop"

$BASE = "http://localhost:8000"
$API  = "$BASE/api"
$LOG_FILE = Join-Path (Get-Location) "logs\hids.log"    # fallback si /api/activity absent

function Write-Title($t){ Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Write-Pass ($m){ Write-Host "✔ $m" -ForegroundColor Green }
function Write-Warn ($m){ Write-Host "! $m" -ForegroundColor Yellow }
function Write-Fail ($m){ Write-Host "✘ $m" -ForegroundColor Red }

function Invoke-Json {
  param([string]$Method,[string]$Url,[hashtable]$Headers=@{},$Body=$null,[int[]]$Expect=@(200,201,204),[string]$Name="")
  try {
    if ($null -ne $Body ) {
      if (-not $Headers.ContainsKey("Content-Type")) { $Headers["Content-Type"]="application/json" }
      $payload = if ($Headers["Content-Type"] -eq "application/json") { $Body | ConvertTo-Json -Depth 8 -Compress } else { $Body }
      $r = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers -Body $payload
    } else {
      $r = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers
    }
    $code=[int]$r.StatusCode; $content=$r.Content
  } catch {
    $ex=$_.Exception; $resp=$ex.Response
    if ($resp -and $resp.StatusCode) {
      $code=[int]$resp.StatusCode
      try { $sr=New-Object System.IO.StreamReader($resp.GetResponseStream()); $content=$sr.ReadToEnd() } catch { $content="" }
    } else { $code=-1; $content=$ex.Message }
  }
  $ok = $Expect -contains $code
  $label = if($Name){$Name}else{"$Method $Url"}
  if($ok){ Write-Pass "$label → $code" } else { Write-Fail "$label → $code (expected: $($Expect -join ','))" }
  $data=$null; try { $data = $content | ConvertFrom-Json } catch { }
  [pscustomobject]@{ Status=$code; Ok=$ok; Body=$data; Raw=$content }
}

# ---------------------------
# 0) Sanity + Auth admin
# ---------------------------
Write-Title "Sanity + Auth"
Invoke-Json -Method GET -Url "$API/status" -Name "GET /api/status" | Out-Null

# Login (FORM attendu)
$form = "username=admin_Hids&password=st21@g-p@ss!"
$login = Invoke-Json -Method POST -Url "$API/auth/login" -Body $form -Expect @(200) -Name "POST /api/auth/login (FORM)" -Headers @{ "Content-Type"="application/x-www-form-urlencoded" }
if(-not $login.Body -or -not $login.Body.access_token){ throw "Login failed" }
$TOKEN = $login.Body.access_token
$AUTH  = @{ Authorization = "Bearer $TOKEN" }

# Découverte de /api/activity (si présent)
Write-Title "Découverte de /api/activity"
$openapi = Invoke-Json -Method GET -Url "$BASE/openapi.json" -Name "GET /openapi.json"
$HAS_ACTIVITY = $false
if ($openapi.Body -and $openapi.Body.paths) {
  $HAS_ACTIVITY = $openapi.Body.paths.PSObject.Properties.Name -contains "/api/activity"
}
if ($HAS_ACTIVITY) { Write-Pass "/api/activity disponible" } else { Write-Warn "/api/activity absent → fallback: lecture de .\logs\hids.log" }

function Get-Activity([int]$limit=50){
  if ($HAS_ACTIVITY){
    $r = Invoke-Json -Method GET -Url "$API/activity?limit=$limit" -Headers $AUTH -Expect @(200) -Name "GET /api/activity"
    return $r.Body
  } else {
    if (Test-Path $LOG_FILE){
      $lines = Get-Content -Path $LOG_FILE -Tail $limit
      # retourne les lignes brutes (JSON dans la partie message si tu as gardé le format proposé)
      return $lines
    } else {
      return @()
    }
  }
}

function CountEventsMatching($events, [string]$needle){
  if (-not $events){ return 0 }
  $cnt = 0
  foreach($e in $events){
    $txt = if ($e -is [string]) { $e } else { ($e | ConvertTo-Json -Compress) }
    if ($txt -match [Regex]::Escape($needle)){ $cnt++ }
  }
  return $cnt
}

# ---------------------------
# 1) Créer des items minutely
# ---------------------------
Write-Title "Création items (minutely)"
$folderBody = @{ path="/var/log";  frequency="minutely" }
$fileBody   = @{ path="/etc/hosts"; frequency="minutely" }
$ipBody     = @{ ip="10.0.0.1"; hostname="lab"; frequency="minutely" }

$f1 = Invoke-Json -Method POST -Url "$API/monitoring/folders" -Headers $AUTH -Body $folderBody -Expect @(201,200,409) -Name "POST /monitoring/folders (minutely)"
$file = Invoke-Json -Method POST -Url "$API/monitoring/files"    -Headers $AUTH -Body $fileBody    -Expect @(201,200,409) -Name "POST /monitoring/files (minutely)"
$ip     = Invoke-Json -Method POST -Url "$API/monitoring/ips"      -Headers $AUTH -Body $ipBody      -Expect @(201,200,409) -Name "POST /monitoring/ips (minutely)"

$folderId = if($f1.Body){ [int]$f1.Body.id } else { 0 }
$fileId   = if($file.Body){ [int]$file.Body.id } else { 0 }
$ipId     = if($ip.Body){ [int]$ip.Body.id } else { 0 }

# Snapshot activité AVANT
$before = Get-Activity 200
Write-Host ("Activité avant: " + (($before | Measure-Object).Count))  

# ---------------------------
# 2) Attendre une minute et vérifier qu’on a des exécutions
# ---------------------------
Write-Title "Attente exécution jobs (~65s)"
Start-Sleep -Seconds 65

$after = Get-Activity 200
Write-Host ("Activité après: " + (($after | Measure-Object).Count))

# Vérif par motifs (id dans la ligne JSON)
$needles = @()
if($folderId -gt 0){ $needles += "folder_scan`",`"id`":$folderId" }
if($fileId   -gt 0){ $needles += "file_scan`",`"id`":$fileId" }
if($ipId     -gt 0){ $needles += "ip_scan`",`"id`":$ipId" }

$okRuns = 0
foreach($n in $needles){
  $cntBefore = CountEventsMatching $before $n
  $cntAfter  = CountEventsMatching $after  $n
  if ($cntAfter -gt $cntBefore){
    Write-Pass "Job exécuté pour motif [$n] (+$($cntAfter-$cntBefore))"
    $okRuns++
  } else {
    Write-Fail "Aucune nouvelle exécution détectée pour [$n]"
  }
}

# ---------------------------
# 3) Supprimer 1 item et vérifier arrêt du job
# ---------------------------
Write-Title "Suppression et vérif arrêt du job"

$deletedLabel = $null
if ($folderId -gt 0){
  Invoke-Json -Method DELETE -Url "$API/monitoring/folders/$folderId" -Headers $AUTH -Expect @(204,404) -Name "DELETE /monitoring/folders/{id}" | Out-Null
  $deletedLabel = "folder_scan`",`"id`":$folderId"
} elseif ($fileId -gt 0){
  Invoke-Json -Method DELETE -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Expect @(204,404) -Name "DELETE /monitoring/files/{id}" | Out-Null
  $deletedLabel = "file_scan`",`"id`":$fileId"
} elseif ($ipId -gt 0){
  Invoke-Json -Method DELETE -Url "$API/monitoring/ips/$ipId" -Headers $AUTH -Expect @(204,404) -Name "DELETE /monitoring/ips/{id}" | Out-Null
  $deletedLabel = "ip_scan`",`"id`":$ipId"
}

if ($deletedLabel){
  $base = Get-Activity 200
  $cntBase = CountEventsMatching $base $deletedLabel
  Start-Sleep -Seconds 65
  $again = Get-Activity 200
  $cntAgain = CountEventsMatching $again $deletedLabel
  if ($cntAgain -le $cntBase){
    Write-Pass "Aucune nouvelle exécution après suppression ($deletedLabel) → job arrêté"
  } else {
    Write-Fail "Encore des exécutions après suppression ($deletedLabel) → job NON retiré"
  }
} else {
  Write-Warn "Aucun ID supprimé (tous les POST ont renvoyé 409 sans body ?)"
}

Write-Title "Fin des tests scheduler"
