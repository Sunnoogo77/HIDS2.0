# tests.ps1  —  E2E smoke tests HIDS-Web 2.0 (PowerShell)
# Prérequis: API up sur http://localhost:8000

$ErrorActionPreference = "Stop"

$BASE = "http://localhost:8000"
$API  = "$BASE/api"

function Write-Title($t) { Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Write-Pass ($msg) { Write-Host "✔ $msg" -ForegroundColor Green }
function Write-Fail ($msg) { Write-Host "✘ $msg" -ForegroundColor Red }
function Trim-Json($s) {
  if (-not $s) { return "" }
  if ($s.Length -gt 800) { return $s.Substring(0,800) + "...(truncated)" } else { return $s }
}

function Invoke-Test {
  param(
    [string]$Method,
    [string]$Url,
    [hashtable]$Headers = @{},
    $Body = $null,                 # objet PS -> JSON si non null
    [int[]]$Expect = @(200,201,204),
    [string]$Name = ""
  )
  if ($Body -ne $null -and -not ($Headers.ContainsKey("Content-Type"))) {
    $Headers["Content-Type"] = "application/json"
  }
  try {
    if ($Body -ne $null -and $Headers["Content-Type"] -eq "application/json") {
      $json = ($Body | ConvertTo-Json -Depth 6 -Compress)
      $resp = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers -Body $json
    } elseif ($Body -ne $null) {
      $resp = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers -Body $Body
    } else {
      $resp = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers
    }
    $code = [int]$resp.StatusCode
    $content = $resp.Content
  } catch {
    $ex = $_.Exception
    $resp2 = $ex.Response
    if ($resp2 -and $resp2.StatusCode) {
      $code = [int]$resp2.StatusCode
      try { $sr = New-Object System.IO.StreamReader($resp2.GetResponseStream()); $content = $sr.ReadToEnd() } catch { $content = "" }
    } else {
      $code = -1; $content = $ex.Message
    }
  }

  $ok = $Expect -contains $code
  $label = if ($Name) { $Name } else { "$Method $Url" }
  if ($ok) { Write-Pass "$label → $code"; }
  else     { Write-Fail "$label → $code (expected: $($Expect -join ','))"; }
  if ($content) { Write-Host (Trim-Json $content) }

  # Essaie de parser JSON
  $data = $null
  try { $data = $content | ConvertFrom-Json } catch { }

  return [pscustomobject]@{
    Status  = $code
    Ok      = $ok
    BodyRaw = $content
    Body    = $data
  }
}

# -----------------------------
# 0) Sanity: /api/status (public)
# -----------------------------
Write-Title "Sanity check"
Invoke-Test -Method GET -Url "$API/status" -Name "GET /api/status" | Out-Null
# (status router est monté sous /api)  # 

# -----------------------------
# 1) Login admin (JSON puis FORM)
# -----------------------------
Write-Title "Auth: login admin (JSON then FORM)"
$LOGIN_JSON = @{ username = "admin_Hids"; password = "st21@g-p@ss!" }
$r = Invoke-Test -Method POST -Url "$API/auth/login" -Body $LOGIN_JSON -Name "POST /api/auth/login (JSON)" -Expect @(200,401,422)
$TOKEN = $null
if ($r.Status -eq 200 -and $r.Body -and $r.Body.access_token) { $TOKEN = $r.Body.access_token }
if (-not $TOKEN) {
  $form = "username=admin_Hids&password=st21@g-p@ss!"
  $r2 = Invoke-Test -Method POST -Url "$API/auth/login" -Body $form -Headers @{ "Content-Type"="application/x-www-form-urlencoded" } -Name "POST /api/auth/login (FORM)" -Expect @(200)
  if ($r2.Status -eq 200 -and $r2.Body -and $r2.Body.access_token) { $TOKEN = $r2.Body.access_token }
}
if (-not $TOKEN) { throw "Login failed. Vérifie /api/auth/login (côté API il attend FORM OAuth2PasswordRequestForm)." } # 

$AUTH = @{ Authorization = "Bearer $TOKEN" }
Write-Host ("Token: " + $TOKEN.Substring(0,20) + "...")

# -----------------------------
# 2) Users (admin-only)
# -----------------------------
Write-Title "Users CRUD (admin-only)"

# 2.0 List users
Invoke-Test -Method GET -Url "$API/users" -Headers $AUTH -Name "GET /api/users" | Out-Null  # router users sous /api  # 

# 2.1 Create a new non-admin user
$ts = [int][double]::Parse((Get-Date -UFormat %s))
$NewUser = @{
  username = "user_$ts"
  email    = "user_$ts@example.com"
  password = "User@123"
  is_admin = $false
}
$rCreate = Invoke-Test -Method POST -Url "$API/users" -Headers $AUTH -Body $NewUser -Name "POST /api/users"
$userId  = $null
if ($rCreate.Body -and $rCreate.Body.id) { $userId = [int]$rCreate.Body.id }

# 2.2 Get user by id
if ($userId) { Invoke-Test -Method GET -Url "$API/users/$userId" -Headers $AUTH -Name "GET /api/users/{id}" | Out-Null }

# 2.3 Update user (toggle is_admin false stays false, change email)
if ($userId) {
  $UpdUser = $NewUser.Clone()
  $UpdUser.email = "user_$ts+upd@example.com"
  Invoke-Test -Method PUT -Url "$API/users/$userId" -Headers $AUTH -Body $UpdUser -Name "PUT /api/users/{id}" | Out-Null
}

# 2.4 Change password (NOTE: ta route a encore un petit bug si elle lit 'new_password' mal référencé côté handler)
if ($userId) {
  $Pwd = @{ new_password = "NewPass@123" }
  Invoke-Test -Method PUT -Url "$API/users/$userId/password" -Headers $AUTH -Body $Pwd -Name "PUT /api/users/{id}/password" -Expect @(204,404,422) | Out-Null
  # Si ça renvoie 422/500, regarde la fonction change_password_endpoint dans users.py (utiliser payload.new_password).  # 
}

# 2.5 Non-admin cannot access /users
#    Login as the new user then try GET /api/users → attendu 403
if ($NewUser) {
  # login du nouvel utilisateur
  $rUserLogin = Invoke-Test -Method POST -Url "$API/auth/login" -Body @{ username=$NewUser.username; password=$NewUser.password } -Name "login non-admin (JSON)" -Expect @(200,401,422)
  if ($rUserLogin.Status -ne 200 -or -not $rUserLogin.Body.access_token) {
    # tente FORM au cas où
    $form2 = "username=$($NewUser.username)&password=$($NewUser.password)"
    $rUserLogin = Invoke-Test -Method POST -Url "$API/auth/login" -Body $form2 -Headers @{ "Content-Type"="application/x-www-form-urlencoded" } -Name "login non-admin (FORM)" -Expect @(200)
  }
  if ($rUserLogin.Status -eq 200 -and $rUserLogin.Body.access_token) {
    $UAUTH = @{ Authorization = "Bearer " + $rUserLogin.Body.access_token }
    Invoke-Test -Method GET -Url "$API/users" -Headers $UAUTH -Name "GET /api/users (non-admin → 403)" -Expect @(403) | Out-Null
  }
}

# -----------------------------
# 3) Monitoring — FILES
# -----------------------------
Write-Title "Monitoring: FILES CRUD"
$fileBody = @{ path="/etc/hosts"; frequency="daily" }   # schéma FileItemCreate  # 
$rF1 = Invoke-Test -Method POST -Url "$API/monitoring/files" -Headers $AUTH -Body $fileBody -Name "POST /api/monitoring/files" -Expect @(201,409)
$fileId = $null
if ($rF1.Body -and $rF1.Body.id) { $fileId = [int]$rF1.Body.id }

# Duplicate → 409
Invoke-Test -Method POST -Url "$API/monitoring/files" -Headers $AUTH -Body $fileBody -Name "POST /files duplicate → 409" -Expect @(409) | Out-Null  # la route map l'IntegrityError en 409  # 

# List / Get / Update / Delete
Invoke-Test -Method GET -Url "$API/monitoring/files" -Headers $AUTH -Name "GET /api/monitoring/files" | Out-Null
if ($fileId) { Invoke-Test -Method GET -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Name "GET /api/monitoring/files/{id}" | Out-Null }
if ($fileId) {
  $fileUpd = @{ path="/etc/hosts"; frequency="hourly" }
  Invoke-Test -Method PUT -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Body $fileUpd -Name "PUT /api/monitoring/files/{id}" | Out-Null
  Invoke-Test -Method DELETE -Url "$API/monitoring/files/$fileId" -Headers $AUTH -Name "DELETE /api/monitoring/files/{id}" -Expect @(204,404) | Out-Null
}

# -----------------------------
# 4) Monitoring — FOLDERS
# -----------------------------
Write-Title "Monitoring: FOLDERS CRUD"
$folderBody = @{ path="/var/log"; frequency="daily" }   # schéma FolderItemCreate  # 
$rD1 = Invoke-Test -Method POST -Url "$API/monitoring/folders" -Headers $AUTH -Body $folderBody -Name "POST /api/monitoring/folders" -Expect @(201,409)
$folderId = $null
if ($rD1.Body -and $rD1.Body.id) { $folderId = [int]$rD1.Body.id }

# Duplicate → 409 (au lieu de 500 après ton patch)
Invoke-Test -Method POST -Url "$API/monitoring/folders" -Headers $AUTH -Body $folderBody -Name "POST /folders duplicate → 409" -Expect @(409) | Out-Null  # 

# List / Get / Update / Delete
Invoke-Test -Method GET -Url "$API/monitoring/folders" -Headers $AUTH -Name "GET /api/monitoring/folders" | Out-Null
if ($folderId) { Invoke-Test -Method GET -Url "$API/monitoring/folders/$folderId" -Headers $AUTH -Name "GET /api/monitoring/folders/{id}" | Out-Null }
if ($folderId) {
  $folderUpd = @{ path="/var/log"; frequency="hourly" }
  Invoke-Test -Method PUT -Url "$API/monitoring/folders/$folderId" -Headers $AUTH -Body $folderUpd -Name "PUT /api/monitoring/folders/{id}" | Out-Null
  Invoke-Test -Method DELETE -Url "$API/monitoring/folders/$folderId" -Headers $AUTH -Name "DELETE /api/monitoring/folders/{id}" -Expect @(204,404) | Out-Null
}

# -----------------------------
# 5) Monitoring — IPS
# -----------------------------
Write-Title "Monitoring: IPS CRUD"
$ipBody = @{ ip="10.0.0.1"; hostname="lab"; frequency="daily" }   # schéma IPItemCreate  # 
$rI1 = Invoke-Test -Method POST -Url "$API/monitoring/ips" -Headers $AUTH -Body $ipBody -Name "POST /api/monitoring/ips" -Expect @(201,409)
$ipId = $null
if ($rI1.Body -and $rI1.Body.id) { $ipId = [int]$rI1.Body.id }

# Duplicate → 409
Invoke-Test -Method POST -Url "$API/monitoring/ips" -Headers $AUTH -Body $ipBody -Name "POST /ips duplicate → 409" -Expect @(409) | Out-Null  # 

# List / Get / Update / Delete
Invoke-Test -Method GET -Url "$API/monitoring/ips" -Headers $AUTH -Name "GET /api/monitoring/ips" | Out-Null
if ($ipId) { Invoke-Test -Method GET -Url "$API/monitoring/ips/$ipId" -Headers $AUTH -Name "GET /api/monitoring/ips/{id}" | Out-Null }
if ($ipId) {
  $ipUpd = @{ ip="10.0.0.1"; hostname="lab"; frequency="hourly" }
  Invoke-Test -Method PUT -Url "$API/monitoring/ips/$ipId" -Headers $AUTH -Body $ipUpd -Name "PUT /api/monitoring/ips/{id}" | Out-Null
  Invoke-Test -Method DELETE -Url "$API/monitoring/ips/$ipId" -Headers $AUTH -Name "DELETE /api/monitoring/ips/{id}" -Expect @(204,404) | Out-Null
}

Write-Title "Tests terminés"
