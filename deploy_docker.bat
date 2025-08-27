@echo off
REM Script para deploy com Docker
REM Torre de Investimentos - Sistema RAG

echo 🐳 Iniciando deploy com Docker...

REM Verificar se Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não encontrado! Instale o Docker Desktop primeiro.
    pause
    exit /b 1
)

REM Criar arquivo .env se não existir
if not exist ".env" (
    echo Criando arquivo .env...
    echo OPENAI_API_KEY=your_openai_key_here > .env
    echo DEEPSEEK_API_KEY=your_deepseek_key_here >> .env
    echo ⚠️  Configure suas chaves de API no arquivo .env
)

REM Build da imagem
echo 🔨 Building imagem Docker...
docker-compose build

REM Iniciar serviços
echo 🚀 Iniciando serviços...
docker-compose up -d

echo ✅ Deploy concluído!
echo 📍 Acesse: http://localhost:5000
echo 🔍 Logs: docker-compose logs -f
echo 🛑 Para parar: docker-compose down

pause
