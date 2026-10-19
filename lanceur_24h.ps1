$executions = 48
$intervalMinutes = 30

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " Demarrage de la collecte Google Flights" -ForegroundColor Cyan
Write-Host " Frequence : Toutes les $intervalMinutes minutes" -ForegroundColor Cyan
Write-Host " Duree : 24 heures ($executions executions)" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

for ($i = 1; $i -le$executions; $i++) {$currentTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "`n[$currentTime] Lancement de l'execution $i sur $executions..." -ForegroundColor Yellow
    
    # Appel direct de Docker (beaucoup plus stable sous Windows)
    docker run --rm -v "C:\Users\Casey\Desktop\SCRAPPER:/app" flight-scraper
    
    # Si ce n'est pas la derniere execution, on attend
    if ($i -lt $executions) {
        $prochaine = (Get-Date).AddMinutes($intervalMinutes).ToString("HH:mm:ss")
        Write-Host "✅ Termine. Prochain scan a $prochaine. En attente..." -ForegroundColor Green
        Start-Sleep -Seconds ($intervalMinutes * 60)
    }
}

Write-Host "`n🎉 Collecte de 24h terminee avec succes !" -ForegroundColor Cyan