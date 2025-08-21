# test-6-jobstore-persistence.ps1 — Persistance APScheduler (SQLite job store)

$ErrorActionPreference = "Stop"
$BASE = "http://localhost:8000"
$API  = "$BASE/api"

function Write-Title($t){ Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Write-Pass ($m){ Write-Host "✔ $m" -ForegroundColor Green }
function Write-Fail ($m){ Write-Host "✘ $m" -ForegroundColor Red }

function Invoke-Json {
  param([string]$Method,[string]$Url,[hashtable]$Headers=@{},$Body=$null,[int[]]$Expect=@(200,201,204),[string]$Name="")
  try{
    if($Body -ne $null){
      if(-not $Headers.ContainsKey("Content-Type")){ $Headers["Content-Type"]="application/json" }
      $payload = if($Headers["Content-Type"] -eq "application/json"){ $Body | ConvertTo-Json -Depth 8 -Compress } else { $Body }
      $r = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers -Body $payload
    } else {
      $r = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers
    }
    $code=[int]$r.StatusCode; $content=$r.Content
  } catch {
    $ex=$_.Exception; $resp=$ex.Response
    if($resp -and $resp.StatusCode){
      $code=[int]$resp.StatusCode
      try{ $sr=New-Object System.IO.StreamReader($resp.GetResponseStream()); $content=$sr.ReadToEnd() }catch{ $content="" }
    } else { $code=-1; $content=$ex.Message }
  }
  $ok = $Expect -contains $code
  $label = if($Name){$Name}else{"$Method $Url"}
  if($ok){ Write-Pass "$label → $code" } else { Write-Fail "$label → $code (expected: $($Expect -join ','))" }
  $data=$null; try{ $data=$content | ConvertFrom-Json }catch{}
  [pscustomobject]@{ Status=$code; Ok=$ok; Body=$data; Raw=$content }
}

# --- Auth admin ---
Write-Title "Auth"
$form="username=admin_Hids&password=st21@g-p@ss!"
$login = Invoke-Json -Method POST -Url "$API/auth/login" -Body $form -Headers @{ "Content-Type"="application/x-www-form-urlencoded" } -Expect @(200) -Name "POST /api/auth/login"
if(-not $login.Body -or -not $login.Body.access_token){ throw "Login failed" }
$AUTH = @{ Authorization = "Bearer " + $login.Body.access_token }

# --- Create two minutely items ---
Write-Title "Create items (minutely)"
$fileBody = @{ path="/etc/hosts"; frequency="minutely"; status="active" }
$ipBody   = @{ ip="10.0.0.2"; hostname="lab2"; frequency="minutely"; status="active" }

$f = Invoke-Json -Method POST -Url "$API/monitoring/files" -Headers $AUTH -Body $fileBody -Expect @(201,200,409) -Name "POST /monitoring/files"
$i = Invoke-Json -Method POST -Url "$API/monitoring/ips"   -Headers $AUTH -Body $ipBody   -Expect @(201,200,409) -Name "POST /monitoring/ips"

$fileId = if($f.Body){ [int]$f.Body.id } else { 0 }
$ipId   = if($i.Body){ [int]$i.Body.id } else { 0 }
$needleFile = "file_scan`",`"id`":$fileId"
$needleIp   = "ip_scan`",`"id`":$ipId"

# --- Baseline metrics & activity ---
Write-Title "Baseline /api/metrics & /api/activity"
$met1 = Invoke-Json -Method GET -Url "$API/metrics?limit_events=10" -Headers $AUTH -Expect @(200) -Name "GET /api/metrics"
$jobsBefore = $met1.Body.scheduler.total

$actBefore = (Invoke-Json -Method GET -Url "$API/activity?limit=200" -Headers $AUTH -Expect @(200) -Name "GET /api/activity").Body
function CountMatches($events,[string]$needle){
  if(-not $events){ return 0 }
  $cnt=0
  foreach($e in $events){ if( ($e | ConvertTo-Json -Compress) -match [Regex]::Escape($needle) ){ $cnt++ } }
  $cnt
}
$cntF0 = CountMatches $actBefore $needleFile
$cntI0 = CountMatches $actBefore $needleIp

# --- Attendre 65s pour voir des exécutions ---
Write-Title "Wait ~65s (pre-restart)"
Start-Sleep -Seconds 65
$act1 = (Invoke-Json -Method GET -Url "$API/activity?limit=200" -Headers $AUTH -Expect @(200) -Name "GET /api/activity").Body
$cntF1 = CountMatches $act1 $needleFile
$cntI1 = CountMatches $act1 $needleIp
if($cntF1 -gt $cntF0 -or $cntI1 -gt $cntI0){ Write-Pass "Jobs executed pre-restart" } else { Write-Fail "No executions pre-restart" }

# --- Restart manual ---
Write-Title "MANUAL STEP"
Write-Host "➡ Ouvre un autre terminal et exécute:  docker-compose restart api"
Read-Host "Quand le conteneur est revenu UP (docs OK), appuie sur Entrée pour continuer"

# --- After restart: metrics & activity ---
Write-Title "Post-restart checks"
$met2 = Invoke-Json -Method GET -Url "$API/metrics?limit_events=10" -Headers $AUTH -Expect @(200) -Name "GET /api/metrics (post-restart)"
$jobsAfter = $met2.Body.scheduler.total
Write-Host ("Jobs before/after restart: {0}/{1}" -f $jobsBefore, $jobsAfter)

# On attend à nouveau 65s et on doit revoir des exécutions, sans recréer les items
Start-Sleep -Seconds 65
$act2 = (Invoke-Json -Method GET -Url "$API/activity?limit=200" -Headers $AUTH -Expect @(200) -Name "GET /api/activity (post-restart)").Body
$cntF2 = CountMatches $act2 $needleFile
$cntI2 = CountMatches $act2 $needleIp
if($cntF2 -gt $cntF1 -or $cntI2 -gt $cntI1){
  Write-Pass "Jobs persisted & executed post-restart"
} else {
  Write-Fail "No executions post-restart (persistence KO ?)"
}

Write-Title "Done"
