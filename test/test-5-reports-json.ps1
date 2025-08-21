# test-5-reports-json.ps1 — Validate consolidated JSON report

$ErrorActionPreference = "Stop"
$BASE = "http://localhost:8000"
$API  = "$BASE/api"

function Write-Title($t){ Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Write-Pass ($m){ Write-Host "✔ $m" -ForegroundColor Green }
function Write-Fail ($m){ Write-Host "✘ $m" -ForegroundColor Red }
function Invoke-Json {
  param([string]$Method,[string]$Url,[hashtable]$Headers=@{},$Body=$null,[int[]]$Expect=@(200),[string]$Name="")
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

Write-Title "Auth"
$form="username=admin_Hids&password=st21@g-p@ss!"
$login = Invoke-Json -Method POST -Url "$API/auth/login" -Body $form -Headers @{ "Content-Type"="application/x-www-form-urlencoded" } -Name "POST /api/auth/login"
if(-not $login.Body -or -not $login.Body.access_token){ throw "Login failed" }
$AUTH = @{ Authorization = "Bearer " + $login.Body.access_token }

Write-Title "GET /api/metrics (baseline)"
$metrics = Invoke-Json -Method GET -Url "$API/metrics?limit_events=10" -Headers $AUTH -Name "GET /api/metrics"

Write-Title "GET /api/reports"
$rep = Invoke-Json -Method GET -Url "$API/reports?limit_events=20" -Headers $AUTH -Name "GET /api/reports"
$rep.Raw | Write-Host

# Checks structure
if($rep.Body -and $rep.Body.report -and $rep.Body.metrics -and $rep.Body.inventory -and $rep.Body.events -ne $null){
  Write-Pass "Structure report OK"
}else{
  Write-Fail "Structure report incomplète"
}

# Consistency checks with metrics
$invTotal = ($rep.Body.inventory.files.Count + $rep.Body.inventory.folders.Count + $rep.Body.inventory.ips.Count)
$monTotal = $rep.Body.metrics.monitored.total
if($invTotal -eq $monTotal){
  Write-Pass ("Inventaire vs monitored total cohérents ({0})" -f $invTotal)
}else{
  Write-Fail ("Incohérence inventaire/monitored ({0} vs {1})" -f $invTotal, $monTotal)
}

# Scheduler counts visible
$jobsTotal = $rep.Body.metrics.scheduler.total
Write-Host ("Jobs scheduled: {0}" -f $jobsTotal)

Write-Title "Done"
