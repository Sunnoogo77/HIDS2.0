# 1. Build the filtered list of project files (excluding venv and other common folders)
$ext = @(
  '.py','.js','.ts','.tsx','.jsx','.json','.yml','.yaml','.toml',
  '.ini','.cfg','.conf','.md','.txt','.html','.css','.sql','.ps1',
  '.bat','.sh','.dockerfile'
)

$files = Get-ChildItem -Recurse -File -Force |
  Where-Object {
    $_.FullName -notmatch '\\(\.venv|\.git|__pycache__|node_modules|dist|build|\.mypy_cache|\.pytest_cache|\.idea|\.vscode)(\\|$)' -and
    ( $ext -contains $_.Extension.ToLower() -or ($_.Extension -eq '' -and $_.Name -match '^(Dockerfile|Makefile)$') )
  } |
  Sort-Object FullName

Write-Host "Files selected: $($files.Count)"

# 2. Generate tree.txt (relative paths)
$files | ForEach-Object {
  $rel = Resolve-Path -Relative $_.FullName
  $rel
} | Set-Content -Encoding utf8 .\tree.txt
Write-Host "tree.txt regenerated."

# 3. Generate snapshot.txt (content + sha256), skipping files >2MB
$snapshot = ".\snapshot.txt"
"### SNAPSHOT - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -Encoding utf8 $snapshot

foreach ($f in $files) {
  if ($f.Length -gt 2MB) {
    "----- FILE: $(Resolve-Path -Relative $f.FullName) (size=$($f.Length) bytes) [SKIPPED >2MB] -----" | Out-File -Encoding utf8 -Append $snapshot
    "`n" | Out-File -Encoding utf8 -Append $snapshot
    continue
  }
  $rel = Resolve-Path -Relative $f.FullName
  $hash = (Get-FileHash -Algorithm SHA256 $f.FullName).Hash
  "----- FILE: $rel (size=$($f.Length) bytes, sha256=$hash) -----" | Out-File -Encoding utf8 -Append $snapshot
  Get-Content $f.FullName -Raw | Out-File -Encoding utf8 -Append $snapshot
  "`n" | Out-File -Encoding utf8 -Append $snapshot
}
Write-Host "snapshot.txt regenerated."
