# test-3-frequency-and-pause.ps1 — Vérifie update de fréquence + pause/reprise (APScheduler)

$ErrorActionPreference = "Stop"
$BASE = "http://localhost:8000"
$API  = "$BASE/api"

function Write-Title($t){ Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Write-Pass ($m){ Write-Host "✔ $m" -ForegroundColor Green }
function Write-Warn ($m){ Write-Host "! $m" -ForegroundColor Yellow }
function Write-Fail ($m){ Write-Host "✘ $m" -ForegroundColor Red }

function Invoke-Json {
  param([string]$Method,[string]$Url,[hashtable]$Headers=@{},$Body=$null,[int[]]$Expect=@(200,201,204),[string]$Name="")
  try {
    if ($Body -ne $null) {
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

# --- Auth admin ---
Write-Title "Auth"
$form = "username=admin_Hids&password=st21@g-p@ss!"
$login = Invoke-Json -Method POST -Url "$API/auth/login" -Body $form -Expect @(200) -Headers @{ "Content-Type"="application/x-www-form-urlencoded" } -Name "POST /api/auth/login"
if(-not $login.Body -or -not $login.Body.access_token){ throw "Login failed" }
$TOKEN = $login.Body.access_token
$AUTH  = @{ Authorization = "Bearer $TOKEN" }

# --- Détection /api/activity ---
Write-Title "Découverte /api/activity"
$openapi = Invoke-Json -Method GET -Url "$BASE/openapi.json" -Name "GET /openapi.json"
$HAS_ACTIVITY = $false
if ($openapi.Body -and $openapi.Body.paths) { $HAS_ACTIVITY = $openapi.Body.paths.PSObject.Properties.Name -contains "/api/activity" }
if ($HAS_ACTIVITY) { Write-Pass "/api/activity disponible" } else { Write-Warn "/api/activity absent — ce test suppose /api/activity" }

function Get-Activity([int]$limit=200){
  if ($HAS_ACTIVITY){
    (Invoke-Json -Method GET -Url "$API/activity?limit=$limit" -Headers $AUTH -Expect @(200) -Name "GET /api/activity").Body
  } else { @() }
}

function CountMatches($events,[string]$needle){
  if (-not $events){ return 0 }
  $cnt=0
  foreach($e in $events){
    $txt = ($e | ConvertTo-Json -Compress)
    if ($txt -match [Regex]::Escape($needle)){ $cnt++ }
  }
  $cnt
}

# --- 1) Create file (minutely) ---
Write-Title "Create file (minutely)"
$fileBody = @{ path="/etc/hosts"; frequency="minutely"; status="active" }
$r = Invoke-Json -Method POST -Url "$API/monitoring/files" -Headers $AUTH -Body $fileBody -Expect @(201,200,409) -Name "POST /monitoring/files"
$fileId = if($r.Body){ [int]$r.Body.id } else { 0 }
if($fileId -eq 0){ throw "No file id (maybe 409 without body?)" }
$needle = "file_scan`",`"id`":$fileId"

$before = Get-Activity 200
$cnt0 = CountMatches $before $needle
Start-Sleep -Seconds 65
$after = Get-Activity 200
$cnt1 = CountMatches $after $needle
if ($cnt1 -gt $cnt0){ Write-Pass "minutely: exécution détectée (+$($cnt1-$cnt0))" } else { Write-Fail "minutely: aucune exécution détectée" }

# --- 2) Update to hourly (should not run again within ~65s) ---
Write-Title "Update → hourly"
$upd1 = @{ path="/etc/hosts"; frequency="hourly"; status="active" }
Invoke-Json -Method PUT -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Body $upd1 -Expect @(200) -Name "PUT /monitoring/files/{id}" | Out-Null
$base = Get-Activity 200
$cntBase = CountMatches $base $needle
Start-Sleep -Seconds 65
$again = Get-Activity 200
$cntAgain = CountMatches $again $needle
if ($cntAgain -le $cntBase){ Write-Pass "hourly: pas de nouvelle exécution en ~65s (ok)" } else { Write-Fail "hourly: exécution survenue alors que non attendue (+$($cntAgain-$cntBase))" }

# --- 3) Pause (status=paused) ---
Write-Title "Pause (status=paused)"
$upd2 = @{ path="/etc/hosts"; frequency="hourly"; status="paused" }
Invoke-Json -Method PUT -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Body $upd2 -Expect @(200) -Name "PUT /monitoring/files/{id} (paused)" | Out-Null
$base2 = Get-Activity 200
$cntBase2 = CountMatches $base2 $needle
Start-Sleep -Seconds 65
$again2 = Get-Activity 200
$cntAgain2 = CountMatches $again2 $needle
if ($cntAgain2 -le $cntBase2){ Write-Pass "paused: aucune nouvelle exécution (ok)" } else { Write-Fail "paused: exécution non désirée (+$($cntAgain2-$cntBase2))" }

# --- 4) Resume to minutely ---
Write-Title "Resume (active + minutely)"
$upd3 = @{ path="/etc/hosts"; frequency="minutely"; status="active" }
Invoke-Json -Method PUT -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Body $upd3 -Expect @(200) -Name "PUT /monitoring/files/{id} (resume)" | Out-Null
$base3 = Get-Activity 200
$cntBase3 = CountMatches $base3 $needle
Start-Sleep -Seconds 65
$again3 = Get-Activity 200
$cntAgain3 = CountMatches $again3 $needle
if ($cntAgain3 -gt $cntBase3){ Write-Pass "resume: exécution détectée après reprise (+$($cntAgain3-$cntBase3))" } else { Write-Fail "resume: aucune exécution après reprise" }

# --- 5) Cleanup ---
Write-Title "Cleanup"
Invoke-Json -Method DELETE -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Expect @(204,404) -Name "DELETE /monitoring/files/{id}" | Out-Null
Write-Pass "Done"
