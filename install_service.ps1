# Script PowerShell para criar serviço Windows
# Torre de Investimentos - Sistema RAG

$serviceName = "RAG-Torre-Investimentos"
$serviceDisplayName = "RAG Torre de Investimentos 2025"
$serviceDescription = "Sistema RAG para consultas sobre Torre de Investimentos Elegível"
$pythonPath = "C:\Users\u12283\Documents\LUCAS ELOI\RAG_TORRE_2\.venv\Scripts\python.exe"
$scriptPath = "C:\Users\u12283\Documents\LUCAS ELOI\RAG_TORRE_2\deploy_production.py"
$workingDirectory = "C:\Users\u12283\Documents\LUCAS ELOI\RAG_TORRE_2"

Write-Host "🚀 Configurando serviço Windows para RAG Sistema..."

# Verificar se executando como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Execute este script como Administrador!" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Instalar NSSM se não existir
$nssmPath = "C:\Windows\System32\nssm.exe"
if (-not (Test-Path $nssmPath)) {
    Write-Host "📦 Baixando NSSM (Non-Sucking Service Manager)..."
    # Instruções para baixar NSSM manualmente
    Write-Host "Por favor, baixe NSSM de: https://nssm.cc/download" -ForegroundColor Yellow
    Write-Host "Extraia nssm.exe para C:\Windows\System32\" -ForegroundColor Yellow
    Read-Host "Pressione Enter após instalar NSSM"
}

# Criar serviço
Write-Host "🔧 Criando serviço $serviceName..."
& nssm install $serviceName $pythonPath $scriptPath
& nssm set $serviceName AppDirectory $workingDirectory
& nssm set $serviceName DisplayName $serviceDisplayName
& nssm set $serviceName Description $serviceDescription
& nssm set $serviceName Start SERVICE_AUTO_START

Write-Host "✅ Serviço criado com sucesso!"
Write-Host "🔧 Para iniciar: net start $serviceName"
Write-Host "🛑 Para parar: net stop $serviceName"
Write-Host "🗑️ Para remover: nssm remove $serviceName confirm"

Read-Host "Pressione Enter para sair"
