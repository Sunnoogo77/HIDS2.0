# test-8-cors-preflight.ps1 — Preflight CORS
$ErrorActionPreference="Stop"
$BASE="https://localhost:8000"
$ORIGIN="http://localhost:5173"

try{
  $r = Invoke-WebRequest -Method OPTIONS -Uri "$BASE/api/status" -Headers @{
    "Origin"=$ORIGIN
    "Access-Control-Request-Method"="GET"
  }
  $h = $r.Headers
  if($h["Access-Control-Allow-Origin"] -eq $ORIGIN){
    Write-Host "✔ CORS OK pour $ORIGIN" -ForegroundColor Green
  } else {
    Write-Host "✘ CORS NOK. Header: $($h["Access-Control-Allow-Origin"])" -ForegroundColor Red
  }
}catch{
  Write-Host "✘ OPTIONS a échoué: $($_.Exception.Message)" -ForegroundColor Red
}
