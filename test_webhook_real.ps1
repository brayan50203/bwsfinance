$body = @{
    type = 'text'
    text = 'Quanto gastei esse mes?'
    from = '5511974764971@c.us'
    timestamp = [DateTimeOffset]::Now.ToUnixTimeSeconds()
} | ConvertTo-Json

$headers = @{
    'Authorization' = 'Bearer bws_finance_token_55653'
    'Content-Type' = 'application/json'
}

Write-Host "Testando webhook com seu numero..."
Write-Host "From: 5511974764971@c.us"
Write-Host "Text: Quanto gastei esse mes?"
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri 'http://localhost:5000/api/whatsapp/webhook' -Method Post -Body $body -Headers $headers
    Write-Host "Resposta do servidor:"
    Write-Host ($response | ConvertTo-Json -Depth 3)
} catch {
    Write-Host "Erro:"
    Write-Host $_.Exception.Message
}
