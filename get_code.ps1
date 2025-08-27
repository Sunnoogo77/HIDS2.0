# Définir le nom du fichier de sortie
$outputFile = "hids_codes_snapshot.txt"

# Définir les chemins des fichiers à inclure
$filesToInclude = @(
    ".\backend\app\api\activity.py",
    ".\backend\app\api\alerts.py",
    ".\docker-compose.yml",
    ".\backend\Dockerfile",
    ".\hids-web\src\pages\AlertsLogs.jsx",
    ".\hids-web\src\lib\api.js"
)

# Écraser le fichier de sortie s'il existe déjà
Set-Content -Path $outputFile -Value ""

# Parcourir la liste des fichiers et ajouter leur contenu au fichier de sortie
foreach ($file in $filesToInclude) {
    # Vérifier si le fichier existe
    if (Test-Path $file) {
        Write-Output "--- Contenu de $file ---" | Out-File -Append -FilePath $outputFile
        Get-Content -Path $file | Out-File -Append -FilePath $outputFile
        Write-Output "`n" | Out-File -Append -FilePath $outputFile
    } else {
        Write-Output "--- Fichier non trouvé: $file ---" | Out-File -Append -FilePath $outputFile
        Write-Output "`n" | Out-File -Append -FilePath $outputFile
    }
}

Write-Host "Le contenu des fichiers a été sauvegardé dans $outputFile."
