# test-7-scan-now.ps1 — Scan-now endpoints

$ErrorActionPreference = "Stop"
$BASE = "http://localhost:8000"   # ou https://localhost:8443 si tu actives TLS
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
$AUTH = @{ Authorization = "Bearer " + $login.Body.access_token }

Write-Title "Prépare un file/ip (si pas déjà en DB)"
$f = Invoke-Json -Method POST -Url "$API/monitoring/files" -Headers $AUTH -Body @{ path="/etc/hosts"; frequency="hourly"; status="active" } -Expect @(201,200,409) -Name "POST /monitoring/files"
$i = Invoke-Json -Method POST -Url "$API/monitoring/ips"   -Headers $AUTH -Body @{ ip="10.0.0.9"; hostname="demo"; frequency="hourly"; status="active" } -Expect @(201,200,409) -Name "POST /monitoring/ips"
$fileId = if($f.Body){ [int]$f.Body.id } else { 0 }
$ipId   = if($i.Body){ [int]$i.Body.id } else { 0 }

Write-Title "Snapshot activité (avant)"
$act0 = (Invoke-Json -Method GET -Url "$API/activity?limit=200" -Headers $AUTH -Expect @(200) -Name "GET /api/activity").Body
function CountMatches($events,[string]$needle){
  if(-not $events){ return 0 }
  $cnt=0; foreach($e in $events){ if( ($e | ConvertTo-Json -Compress) -match [Regex]::Escape($needle) ){ $cnt++ } }
  $cnt
}
$needleF = "file_scan`",`"id`":$fileId"
$needleI = "ip_scan`",`"id`":$ipId"
$cF0 = CountMatches $act0 $needleF
$cI0 = CountMatches $act0 $needleI

Write-Title "SCAN-NOW (file + ip)"
Invoke-Json -Method POST -Url "$API/monitoring/files/$fileId/scan-now" -Headers $AUTH -Expect @(200) -Name "POST /monitoring/files/{id}/scan-now" | Out-Null
Invoke-Json -Method POST -Url "$API/monitoring/ips/$ipId/scan-now"   -Headers $AUTH -Expect @(200) -Name "POST /monitoring/ips/{id}/scan-now" | Out-Null

Start-Sleep -Seconds 1
$act1 = (Invoke-Json -Method GET -Url "$API/activity?limit=200" -Headers $AUTH -Expect @(200) -Name "GET /api/activity").Body
$cF1 = CountMatches $act1 $needleF
$cI1 = CountMatches $act1 $needleI

if($cF1 -gt $cF0){ Write-Pass "file scan-now → OK (+$($cF1-$cF0))" } else { Write-Fail "file scan-now → KO" }
if($cI1 -gt $cI0){ Write-Pass "ip scan-now → OK (+$($cI1-$cI0))" } else { Write-Fail "ip scan-now → KO" }

Write-Title "Done"
