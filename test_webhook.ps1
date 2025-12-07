$body = @{
    type = 'text'
    text = 'Teste de mensagem'
    from = '5511974764971'
    timestamp = 1732918000
} | ConvertTo-Json

$headers = @{
    'Authorization' = 'Bearer bws_finance_token_55653'
    'Content-Type' = 'application/json'
}

Write-Host "Enviando teste para webhook..."

try {
    $response = Invoke-RestMethod -Uri 'http://localhost:5000/api/whatsapp/webhook' -Method Post -Body $body -Headers $headers
    Write-Host "Sucesso!"
    Write-Host ($response | ConvertTo-Json -Depth 3)
} catch {
    Write-Host "Erro ao chamar webhook"
    Write-Host $_.Exception.Message
}
