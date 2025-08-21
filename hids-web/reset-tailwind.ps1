# reset-tailwind.ps1 — force Tailwind v3 & nettoie verrous OneDrive/Node

$ErrorActionPreference = "Stop"

function Kill-Procs {
  "→ Killing node / vite / browsers / code that may lock files..."
  Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
  # Get-Process Code -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
  Get-Process "msedge" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
  Get-Process "chrome" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

function Npm-Clean {
  "→ Removing node_modules/.bin/tailwindcss*"
  Remove-Item -Force .\node_modules\.bin\tailwindcss* -ErrorAction SilentlyContinue

  "→ Removing node_modules and caches"
  # PowerShell remove
  Remove-Item -Recurse -Force .\node_modules -ErrorAction SilentlyContinue
  Remove-Item -Recurse -Force .\.vite -ErrorAction SilentlyContinue
  # CMD remove (plus robuste sur OneDrive)
  cmd /c "rd /s /q node_modules" 2>$null
  cmd /c "rd /s /q .vite" 2>$null

  "→ Clearing npm cache"
  npm cache clean --force | Out-Null
}

function Npm-Ensure-V3 {
  "→ Removing any v4 Tailwind CLI packages"
  # Supprime les paquets qui réinstallent Tailwind v4
  npm uninstall @tailwindcss/cli @tailwindcss/node 2>$null | Out-Null

  "→ Installing Tailwind v3 + PostCSS + Autoprefixer"
  npm install -D tailwindcss@3 postcss autoprefixer

  "→ Recreate config files if missing"
  if (-not (Test-Path .\tailwind.config.js)) {
    .\node_modules\.bin\tailwindcss init -p
  }
}

function Fix-OneDrive-Locks {
  "→ Attempting to clear OneDrive locks on native module"
  $paths = @(
    ".\node_modules\@tailwindcss\oxide-win32-x64-msvc",
    ".\node_modules\@tailwindcss\.oxide-win32-x64-msvc-*"
  )
  foreach($p in $paths){
    if(Test-Path $p){
      attrib -r -s -h /s /d $p 2>$null
      cmd /c "rd /s /q $p" 2>$null
    }
  }
}

# --- Run
Kill-Procs
Fix-OneDrive-Locks
Npm-Clean
Npm-Ensure-V3

"→ Installed versions:"
npm list tailwindcss

"→ Tailwind bin version:"
try { & .\node_modules\.bin\tailwindcss -v } catch { "tailwind bin ok" }

"✅ Done. Now run:"
"   npm install"
"   npm run dev"
