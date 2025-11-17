# deploy.ps1 - Script PowerShell para deploy no EasyPanel

Write-Host "🚀 Iniciando deploy do RAG Assistant..." -ForegroundColor Green

# Verificar se .env existe
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Arquivo .env não encontrado!" -ForegroundColor Yellow
    Write-Host "📋 Copie .env.example para .env e configure suas variáveis:" -ForegroundColor Yellow
    Write-Host "   Copy-Item .env.example .env" -ForegroundColor Cyan
    Write-Host "   # Edite .env com suas configurações" -ForegroundColor Cyan
    exit 1
}

# Verificar se OPENAI_API_KEY está configurada
$envContent = Get-Content .env | Where-Object { $_ -match "^OPENAI_API_KEY=" }
if (-not $envContent -or $envContent -match "^OPENAI_API_KEY=$|^OPENAI_API_KEY=\s*$") {
    Write-Host "❌ OPENAI_API_KEY não está configurada no arquivo .env" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Configurações validadas" -ForegroundColor Green

# Build e deploy com docker-compose
Write-Host "🔧 Fazendo build das imagens..." -ForegroundColor Blue
docker-compose build --no-cache

Write-Host "🐳 Iniciando serviços..." -ForegroundColor Blue
docker-compose down --remove-orphans
docker-compose up -d

# Aguardar serviços ficarem prontos
Write-Host "⏳ Aguardando serviços ficarem prontos..." -ForegroundColor Yellow
Start-Sleep 10

# Verificar health dos serviços
Write-Host "🏥 Verificando saúde dos serviços..." -ForegroundColor Blue

# Verificar Qdrant
$qdrantReady = $false
for ($i = 1; $i -le 12; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:6333/" -Method GET -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Qdrant está funcionando" -ForegroundColor Green
            $qdrantReady = $true
            break
        }
    }
    catch {
        Write-Host "⏳ Aguardando Qdrant... (tentativa $i/12)" -ForegroundColor Yellow
        Start-Sleep 5
    }
}

# Verificar Streamlit
$streamlitReady = $false
for ($i = 1; $i -le 12; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8501/_stcore/health" -Method GET -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Streamlit está funcionando" -ForegroundColor Green
            $streamlitReady = $true
            break
        }
    }
    catch {
        Write-Host "⏳ Aguardando Streamlit... (tentativa $i/12)" -ForegroundColor Yellow
        Start-Sleep 5
    }
}

Write-Host ""
Write-Host "🎉 Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Aplicação disponível em:" -ForegroundColor Cyan
Write-Host "   Local: http://localhost:8501" -ForegroundColor White
Write-Host "   Qdrant Admin: http://localhost:6333/dashboard" -ForegroundColor White
Write-Host ""
Write-Host "📊 Para ver logs:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f app" -ForegroundColor White
Write-Host "   docker-compose logs -f qdrant" -ForegroundColor White
Write-Host ""
Write-Host "🛑 Para parar:" -ForegroundColor Cyan
Write-Host "   docker-compose down" -ForegroundColor White

# Abrir automaticamente no navegador (opcional)
$openBrowser = Read-Host "🌐 Abrir aplicação no navegador? (y/N)"
if ($openBrowser -eq "y" -or $openBrowser -eq "Y") {
    Start-Process "http://localhost:8501"
}