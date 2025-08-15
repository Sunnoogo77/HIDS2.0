# # tests.ps1 — E2E smoke tests HIDS-Web 2.0 (PowerShell)

# $ErrorActionPreference = "Stop"

# $BASE = "http://localhost:8000"
# $API  = "$BASE/api"

# function Write-Title($t){ Write-Host "`n=== $t ===" -ForegroundColor Cyan }
# function Write-Pass ($m){ Write-Host "✔ $m" -ForegroundColor Green }
# function Write-Warn ($m){ Write-Host "! $m" -ForegroundColor Yellow }
# function Write-Fail ($m){ Write-Host "✘ $m" -ForegroundColor Red }
# function Trim-Json($s){ if(-not $s){return ""}; if($s.Length -gt 800){$s.Substring(0,800)+"...(truncated)"}else{$s} }

# function Invoke-Test {
#   param(
#     [string]$Method,[string]$Url,[hashtable]$Headers=@{},$Body=$null,
#     [int[]]$Expect=@(200,201,204),[string]$Name=""
#   )
#   if ($Body -ne $null -and -not ($Headers.ContainsKey("Content-Type"))) {
#     $Headers["Content-Type"]="application/json"
#   }
#   try{
#     if($Body -ne $null -and $Headers["Content-Type"] -eq "application/json"){
#       $json = ($Body | ConvertTo-Json -Depth 6 -Compress)
#       $resp = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers -Body $json
#     } elseif ($Body -ne $null){
#       $resp = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers -Body $Body
#     } else {
#       $resp = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers
#     }
#     $code = [int]$resp.StatusCode; $content=$resp.Content
#   } catch {
#     $ex=$_.Exception; $resp2=$ex.Response
#     if($resp2 -and $resp2.StatusCode){
#       $code=[int]$resp2.StatusCode
#       try{ $sr=New-Object System.IO.StreamReader($resp2.GetResponseStream()); $content=$sr.ReadToEnd() }catch{ $content="" }
#     } else { $code=-1; $content=$ex.Message }
#   }
#   $label = if($Name){$Name}else{"$Method $Url"}
#   if($Expect -contains $code){ Write-Pass "$label → $code" } else { Write-Fail "$label → $code (expected: $($Expect -join ','))" }
#   if($content){ Write-Host (Trim-Json $content) }
#   $data=$null; try{ $data=$content | ConvertFrom-Json }catch{}
#   [pscustomobject]@{ Status=$code; Ok=($Expect -contains $code); Body=$data; Raw=$content }
# }

# # 0) Sanity
# Write-Title "Sanity check"
# Invoke-Test -Method GET -Url "$API/status" -Name "GET /api/status" | Out-Null

# # 1) Login admin (JSON→422 attendu, puis FORM→200)
# Write-Title "Auth: login admin"
# $LOGIN_JSON=@{ username="admin_Hids"; password="st21@g-p@ss!" }
# $r = Invoke-Test -Method POST -Url "$API/auth/login" -Body $LOGIN_JSON -Name "POST /api/auth/login (JSON)" -Expect @(422,200,401)
# $TOKEN=$null
# if(-not $TOKEN){
#   $form="username=admin_Hids&password=st21@g-p@ss!"
#   $r2=Invoke-Test -Method POST -Url "$API/auth/login" -Body $form -Headers @{ "Content-Type"="application/x-www-form-urlencoded" } -Name "POST /api/auth/login (FORM)" -Expect @(200)
#   if($r2.Status -eq 200 -and $r2.Body){ $TOKEN=$r2.Body.access_token }
# }
# if(-not $TOKEN){ throw "Login admin failed." }
# $AUTH=@{ Authorization="Bearer $TOKEN" }
# Write-Host ("Token: " + $TOKEN.Substring(0,20) + "...")

# # 2) Découvrir la vraie base des routes Users via OpenAPI
# Write-Title "Route discovery (Users)"
# $paths = (Invoke-Test -Method GET -Url "$BASE/openapi.json" -Name "GET /openapi.json").Body.paths.PSObject.Properties.Name
# $USERS_BASE = $null
# if($paths -contains "/api/users"){ $USERS_BASE="$API/users" }
# elseif($paths -contains "/users"){ $USERS_BASE="$BASE/users" }
# if(-not $USERS_BASE){
#   Write-Fail "Aucune route Users trouvée dans l'OpenAPI. Les tests Users seront ignorés."
# }else{
#   Write-Pass "Users base = $USERS_BASE"
# }

# # 3) Users CRUD (admin-only)
# if($USERS_BASE){
#   Write-Title "Users CRUD (admin-only)"
#   Invoke-Test -Method GET -Url "$USERS_BASE" -Headers $AUTH -Name "GET users" | Out-Null

#   $ts=[int][double]::Parse((Get-Date -UFormat %s))
#   $NewUser=@{ username="user_$ts"; email="user_$ts@example.com"; password="User@123"; is_admin=$false }
#   $rCreate=Invoke-Test -Method POST -Url "$USERS_BASE" -Headers $AUTH -Body $NewUser -Name "POST users" -Expect @(201,400)
#   $userId = if($rCreate.Body){ [int]$rCreate.Body.id } else { $null }

#   if($userId){
#     Invoke-Test -Method GET -Url "$USERS_BASE/$userId" -Headers $AUTH -Name "GET users/{id}" | Out-Null
#     $Upd=$NewUser.Clone(); $Upd.email="user_$ts+upd@example.com"
#     Invoke-Test -Method PUT -Url "$USERS_BASE/$userId" -Headers $AUTH -Body $Upd -Name "PUT users/{id}" | Out-Null

#     # Change password (204 attendu si endpoint corrigé; 422/500 sinon)
#     Invoke-Test -Method PUT -Url "$USERS_BASE/$userId/password" -Headers $AUTH -Body @{ new_password="NewPass@123" } -Name "PUT users/{id}/password" -Expect @(204,404,422,500) | Out-Null

#     # Login du non‑admin et test 403 sur /users
#     $rUserLogin = Invoke-Test -Method POST -Url "$API/auth/login" -Body "username=$($NewUser.username)&password=$($NewUser.password)" -Headers @{ "Content-Type"="application/x-www-form-urlencoded" } -Name "login (non-admin)" -Expect @(200)
#     if($rUserLogin.Status -eq 200 -and $rUserLogin.Body){
#       $UAUTH=@{ Authorization="Bearer " + $rUserLogin.Body.access_token }
#       Invoke-Test -Method GET -Url "$USERS_BASE" -Headers $UAUTH -Name "GET users (non-admin → 403)" -Expect @(403) | Out-Null
#     }
#   }
# }

# # 4) Monitoring — FILES
# Write-Title "Monitoring: FILES CRUD"
# $fileBody=@{ path="/etc/hosts"; frequency="daily" }
# $rF1=Invoke-Test -Method POST -Url "$API/monitoring/files" -Headers $AUTH -Body $fileBody -Name "POST /monitoring/files" -Expect @(201,200,409)
# if($rF1.Status -eq 409){ Write-Host "Duplicate policy: 409 (conflict)" }
# elseif($rF1.Status -in 200,201){ Write-Host "Duplicate policy: idempotent create (returns existing/created with 200/201)" }
# $fileId = if($rF1.Body){ [int]$rF1.Body.id } else { $null }
# Invoke-Test -Method POST -Url "$API/monitoring/files" -Headers $AUTH -Body $fileBody -Name "POST /files duplicate (201/200/409 accepted)" -Expect @(201,200,409) | Out-Null
# Invoke-Test -Method GET -Url "$API/monitoring/files" -Headers $AUTH -Name "GET /monitoring/files" | Out-Null
# if($fileId){
#   Invoke-Test -Method GET -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Name "GET /monitoring/files/{id}" | Out-Null
#   Invoke-Test -Method PUT -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Body @{ path="/etc/hosts"; frequency="hourly" } -Name "PUT /monitoring/files/{id}" | Out-Null
#   Invoke-Test -Method DELETE -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Name "DELETE /monitoring/files/{id}" -Expect @(204,404) | Out-Null
# }

# # 5) Monitoring — FOLDERS
# Write-Title "Monitoring: FOLDERS CRUD"
# $folderBody=@{ path="/var/log"; frequency="daily" }
# $rD1=Invoke-Test -Method POST -Url "$API/monitoring/folders" -Headers $AUTH -Body $folderBody -Name "POST /monitoring/folders" -Expect @(201,200,409)
# $folderId = if($rD1.Body){ [int]$rD1.Body.id } else { $null }
# Invoke-Test -Method POST -Url "$API/monitoring/folders" -Headers $AUTH -Body $folderBody -Name "POST /folders duplicate (201/200/409 accepted)" -Expect @(201,200,409) | Out-Null
# Invoke-Test -Method GET -Url "$API/monitoring/folders" -Headers $AUTH -Name "GET /monitoring/folders" | Out-Null
# if($folderId){
#   Invoke-Test -Method GET -Url "$API/monitoring/folders/$folderId" -Headers $AUTH -Name "GET /monitoring/folders/{id}" | Out-Null
#   Invoke-Test -Method PUT -Url "$API/monitoring/folders/$folderId" -Headers $AUTH -Body @{ path="/var/log"; frequency="hourly" } -Name "PUT /monitoring/folders/{id}" | Out-Null
#   Invoke-Test -Method DELETE -Url "$API/monitoring/folders/$folderId" -Headers $AUTH -Name "DELETE /monitoring/folders/{id}" -Expect @(204,404) | Out-Null
# }

# # 6) Monitoring — IPS
# Write-Title "Monitoring: IPS CRUD"
# $ipBody=@{ ip="10.0.0.1"; hostname="lab"; frequency="daily" }
# $rI1=Invoke-Test -Method POST -Url "$API/monitoring/ips" -Headers $AUTH -Body $ipBody -Name "POST /monitoring/ips" -Expect @(201,200,409)
# $ipId = if($rI1.Body){ [int]$rI1.Body.id } else { $null }
# Invoke-Test -Method POST -Url "$API/monitoring/ips" -Headers $AUTH -Body $ipBody -Name "POST /ips duplicate (201/200/409 accepted)" -Expect @(201,200,409) | Out-Null
# Invoke-Test -Method GET -Url "$API/monitoring/ips" -Headers $AUTH -Name "GET /monitoring/ips" | Out-Null
# if($ipId){
#   Invoke-Test -Method GET -Url "$API/monitoring/ips/$ipId" -Headers $AUTH -Name "GET /monitoring/ips/{id}" | Out-Null
#   Invoke-Test -Method PUT -Url "$API/monitoring/ips/$ipId" -Headers $AUTH -Body @{ ip="10.0.0.1"; hostname="lab"; frequency="hourly" } -Name "PUT /monitoring/ips/{id}" | Out-Null
#   Invoke-Test -Method DELETE -Url "$API/monitoring/ips/$ipId" -Headers $AUTH -Name "DELETE /monitoring/ips/{id}" -Expect @(204,404) | Out-Null
# }

# Write-Title "Tests terminés"

# tests.ps1 — E2E smoke tests HIDS-Web 2.0 (PowerShell)

$ErrorActionPreference = "Stop"

$BASE = "http://localhost:8000"
$API  = "$BASE/api"

function Write-Title($t){ Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Write-Pass ($m){ Write-Host "✔ $m" -ForegroundColor Green }
function Write-Warn ($m){ Write-Host "! $m" -ForegroundColor Yellow }
function Write-Fail ($m){ Write-Host "✘ $m" -ForegroundColor Red }
function Trim-Json($s){ if(-not $s){return ""}; if($s.Length -gt 800){$s.Substring(0,800)+"...(truncated)"}else{$s} }

function Invoke-Test {
  param(
    [string]$Method,[string]$Url,[hashtable]$Headers=@{},$Body=$null,
    [int[]]$Expect=@(200,201,204),[string]$Name=""
  )
  if ($Body -ne $null -and -not ($Headers.ContainsKey("Content-Type"))) {
    $Headers["Content-Type"]="application/json"
  }
  try{
    if($Body -ne $null -and $Headers["Content-Type"] -eq "application/json"){
      $json = ($Body | ConvertTo-Json -Depth 6 -Compress)
      $resp = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers -Body $json
    } elseif ($Body -ne $null){
      $resp = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers -Body $Body
    } else {
      $resp = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers
    }
    $code = [int]$resp.StatusCode; $content=$resp.Content
  } catch {
    $ex=$_.Exception; $resp2=$ex.Response
    if($resp2 -and $resp2.StatusCode){
      $code=[int]$resp2.StatusCode
      try{ $sr=New-Object System.IO.StreamReader($resp2.GetResponseStream()); $content=$sr.ReadToEnd() }catch{ $content="" }
    } else { $code=-1; $content=$ex.Message }
  }
  $label = if($Name){$Name}else{"$Method $Url"}
  if($Expect -contains $code){ Write-Pass "$label → $code" } else { Write-Fail "$label → $code (expected: $($Expect -join ','))" }
  if($content){ Write-Host (Trim-Json $content) }
  $data=$null; try{ $data=$content | ConvertFrom-Json }catch{}
  [pscustomobject]@{ Status=$code; Ok=($Expect -contains $code); Body=$data; Raw=$content }
}

# 0) Sanity
Write-Title "Sanity check"
Invoke-Test -Method GET -Url "$API/status" -Name "GET /api/status" | Out-Null

# 1) Login admin (JSON→422 attendu, puis FORM→200)
Write-Title "Auth: login admin"
$LOGIN_JSON=@{ username="admin_Hids"; password="st21@g-p@ss!" }
$r = Invoke-Test -Method POST -Url "$API/auth/login" -Body $LOGIN_JSON -Name "POST /api/auth/login (JSON)" -Expect @(422,200,401)
$TOKEN=$null
if(-not $TOKEN){
  $form="username=admin_Hids&password=st21@g-p@ss!"
  $r2=Invoke-Test -Method POST -Url "$API/auth/login" -Body $form -Headers @{ "Content-Type"="application/x-www-form-urlencoded" } -Name "POST /api/auth/login (FORM)" -Expect @(200)
  if($r2.Status -eq 200 -and $r2.Body){ $TOKEN=$r2.Body.access_token }
}
if(-not $TOKEN){ throw "Login admin failed." }
$AUTH=@{ Authorization="Bearer $TOKEN" }
Write-Host ("Token: " + $TOKEN.Substring(0,20) + "...")

# 2) Découvrir la vraie base des routes Users via OpenAPI
Write-Title "Route discovery (Users)"
$paths = (Invoke-Test -Method GET -Url "$BASE/openapi.json" -Name "GET /openapi.json").Body.paths.PSObject.Properties.Name
$USERS_BASE = $null
if($paths -contains "/api/users"){ $USERS_BASE="$API/users" }
elseif($paths -contains "/users"){ $USERS_BASE="$BASE/users" }
if(-not $USERS_BASE){
  Write-Fail "Aucune route Users trouvée dans l'OpenAPI. Les tests Users seront ignorés."
}else{
  Write-Pass "Users base = $USERS_BASE"
}

# 3) Users CRUD (admin-only)
if($USERS_BASE){
  Write-Title "Users CRUD (admin-only)"
  Invoke-Test -Method GET -Url "$USERS_BASE" -Headers $AUTH -Name "GET users" | Out-Null

  $ts=[int][double]::Parse((Get-Date -UFormat %s))
  $NewUser=@{ username="user_$ts"; email="user_$ts@example.com"; password="User@123"; is_admin=$false }
  $rCreate=Invoke-Test -Method POST -Url "$USERS_BASE" -Headers $AUTH -Body $NewUser -Name "POST users" -Expect @(201,400)
  $userId = if($rCreate.Body){ [int]$rCreate.Body.id } else { $null }

  if($userId){
    Invoke-Test -Method GET -Url "$USERS_BASE/$userId" -Headers $AUTH -Name "GET users/{id}" | Out-Null
    $Upd=$NewUser.Clone(); $Upd.email="user_$ts+upd@example.com"
    Invoke-Test -Method PUT -Url "$USERS_BASE/$userId" -Headers $AUTH -Body $Upd -Name "PUT users/{id}" | Out-Null

    # Change password + test nouveau mot de passe
    $NEWPASS = "NouveauP@ss123!"
    $ORIGPASS = $NewUser.password
    Invoke-Test -Method PUT -Url "$USERS_BASE/$userId/password" -Headers $AUTH `
        -Body @{ new_password=$NEWPASS } -Name "PUT users/{id}/password" `
        -Expect @(204,404,422,500) | Out-Null

    # -- Vérifier le login avec le NOUVEAU mot de passe --
    $resp = curl.exe -s -X POST "$API/auth/login" `
      -H "Content-Type: application/x-www-form-urlencoded" `
      -d "username=$($NewUser.username)&password=$NEWPASS"

    if ($LASTEXITCODE -eq 0 -and ($resp | ConvertFrom-Json).access_token) {
      Write-Pass "login (non-admin avec nouveau mot de passe) → 200"
    } else {
      Write-Fail "login (non-admin avec nouveau mot de passe) → KO"
      $resp
    }

    # -- (Optionnel) remettre l’ancien mot de passe pour cleanup --
    curl.exe -s -X PUT "$USERS_BASE/$userId/password" `
      -H "Authorization: Bearer $TOKEN" `
      -H "Content-Type: application/json" `
      -d (@{ new_password = "$ORIGPASS" } | ConvertTo-Json) > $null
  }
}

# 4) Monitoring — FILES
Write-Title "Monitoring: FILES CRUD"
$fileBody=@{ path="/etc/hosts"; frequency="daily" }
$rF1=Invoke-Test -Method POST -Url "$API/monitoring/files" -Headers $AUTH -Body $fileBody -Name "POST /monitoring/files" -Expect @(201,200,409)
if($rF1.Status -eq 409){ Write-Host "Duplicate policy: 409 (conflict)" }
elseif($rF1.Status -in 200,201){ Write-Host "Duplicate policy: idempotent create (returns existing/created with 200/201)" }
$fileId = if($rF1.Body){ [int]$rF1.Body.id } else { $null }
Invoke-Test -Method POST -Url "$API/monitoring/files" -Headers $AUTH -Body $fileBody -Name "POST /files duplicate (201/200/409 accepted)" -Expect @(201,200,409) | Out-Null
Invoke-Test -Method GET -Url "$API/monitoring/files" -Headers $AUTH -Name "GET /monitoring/files" | Out-Null
if($fileId){
  Invoke-Test -Method GET -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Name "GET /monitoring/files/{id}" | Out-Null
  Invoke-Test -Method PUT -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Body @{ path="/etc/hosts"; frequency="hourly" } -Name "PUT /monitoring/files/{id}" | Out-Null
  Invoke-Test -Method DELETE -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Name "DELETE /monitoring/files/{id}" -Expect @(204,404) | Out-Null
}

# 5) Monitoring — FOLDERS
Write-Title "Monitoring: FOLDERS CRUD"
$folderBody=@{ path="/var/log"; frequency="daily" }
$rD1=Invoke-Test -Method POST -Url "$API/monitoring/folders" -Headers $AUTH -Body $folderBody -Name "POST /monitoring/folders" -Expect @(201,200,409)
$folderId = if($rD1.Body){ [int]$rD1.Body.id } else { $null }
Invoke-Test -Method POST -Url "$API/monitoring/folders" -Headers $AUTH -Body $folderBody -Name "POST /folders duplicate (201/200/409 accepted)" -Expect @(201,200,409) | Out-Null
Invoke-Test -Method GET -Url "$API/monitoring/folders" -Headers $AUTH -Name "GET /monitoring/folders" | Out-Null
if($folderId){
  Invoke-Test -Method GET -Url "$API/monitoring/folders/$folderId" -Headers $AUTH -Name "GET /monitoring/folders/{id}" | Out-Null
  Invoke-Test -Method PUT -Url "$API/monitoring/folders/$folderId" -Headers $AUTH -Body @{ path="/var/log"; frequency="hourly" } -Name "PUT /monitoring/folders/{id}" | Out-Null
  Invoke-Test -Method DELETE -Url "$API/monitoring/folders/$folderId" -Headers $AUTH -Name "DELETE /monitoring/folders/{id}" -Expect @(204,404) | Out-Null
}

# 6) Monitoring — IPS
Write-Title "Monitoring: IPS CRUD"
$ipBody=@{ ip="10.0.0.1"; hostname="lab"; frequency="daily" }
$rI1=Invoke-Test -Method POST -Url "$API/monitoring/ips" -Headers $AUTH -Body $ipBody -Name "POST /monitoring/ips" -Expect @(201,200,409)
$ipId = if($rI1.Body){ [int]$rI1.Body.id } else { $null }
Invoke-Test -Method POST -Url "$API/monitoring/ips" -Headers $AUTH -Body $ipBody -Name "POST /ips duplicate (201/200/409 accepted)" -Expect @(201,200,409) | Out-Null
Invoke-Test -Method GET -Url "$API/monitoring/ips" -Headers $AUTH -Name "GET /monitoring/ips" | Out-Null
if($ipId){
  Invoke-Test -Method GET -Url "$API/monitoring/ips/$ipId" -Headers $AUTH -Name "GET /monitoring/ips/{id}" | Out-Null
  Invoke-Test -Method PUT -Url "$API/monitoring/ips/$ipId" -Headers $AUTH -Body @{ ip="10.0.0.1"; hostname="lab"; frequency="hourly" } -Name "PUT /monitoring/ips/{id}" | Out-Null
  Invoke-Test -Method DELETE -Url "$API/monitoring/ips/$ipId" -Headers $AUTH -Name "DELETE /monitoring/ips/{id}" -Expect @(204,404) | Out-Null
}

Write-Title "Tests terminés"
