# test-4-metrics.ps1 — metrics overview (counts + jobs + recent events)

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

Write-Title "Auth"
$form="username=admin_Hids&password=st21@g-p@ss!"
$login = Invoke-Json -Method POST -Url "$API/auth/login" -Body $form -Headers @{ "Content-Type"="application/x-www-form-urlencoded" } -Expect @(200) -Name "POST /api/auth/login"
if(-not $login.Body -or -not $login.Body.access_token){ throw "Login failed" }
$TOKEN = $login.Body.access_token
$AUTH = @{ Authorization = "Bearer $TOKEN" }

Write-Title "GET /api/metrics"
$r = Invoke-Json -Method GET -Url "$API/metrics?limit_events=20" -Headers $AUTH -Expect @(200) -Name "GET /api/metrics"
$r.Raw | Write-Host

# Quelques checks basiques
if($r.Body -and $r.Body.monitored -and $r.Body.scheduler){
  Write-Pass "Structure metrics OK (monitored + scheduler présents)"
} else {
  Write-Fail "Structure metrics incomplète"
}

# Affichage lisible de quelques compteurs
$filesTotal   = $r.Body.monitored.files.total
$filesActive  = $r.Body.monitored.files.active
$foldersTotal = $r.Body.monitored.folders.total
$ipsTotal     = $r.Body.monitored.ips.total
$jobsTotal    = $r.Body.scheduler.total

Write-Host ("Files total/active: {0}/{1}" -f $filesTotal, $filesActive)
Write-Host ("Folders total: {0}" -f $foldersTotal)
Write-Host ("IPs total: {0}" -f $ipsTotal)
Write-Host ("Jobs scheduled: {0}" -f $jobsTotal)

Write-Title "Done"
