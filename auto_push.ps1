# Auto-Push Script for Swedish Transcription App
# Checks for changes every 10 seconds and pushes to GitHub

$projectPath = "c:\Users\FredrikBeckman\OneDrive - Skyddsprodukter i Sverige AB\Tor Finans\Skyddsprodukter\Antigravity projects\Svensk transkribering"
Set-Location -Path $projectPath

Write-Host "Starting Auto-Push Monitor for: $projectPath"
Write-Host "Press Ctrl+C to stop."

while ($true) {
    $status = git status --porcelain
    if ($status) {
        Write-Host "[$(Get-Date)] Changes detected. Committing and pushing..."
        git add .
        git commit -m "Auto-save: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        
        # Capture push output to check for errors (optional, but good for debugging)
        $pushOutput = git push origin main 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[$(Get-Date)] Push successful." -ForegroundColor Green
        } else {
            Write-Host "[$(Get-Date)] Push failed." -ForegroundColor Red
            Write-Host $pushOutput
        }
    } else {
        Write-Host "[$(Get-Date)] No changes detected." -ForegroundColor Gray
    }
    Start-Sleep -Seconds 10
}
