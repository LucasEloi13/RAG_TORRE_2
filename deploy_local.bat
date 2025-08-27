@echo off
REM Script para deploy local com Waitress
REM Torre de Investimentos - Sistema RAG

echo 🚀 Iniciando deploy local com Waitress...

REM Ativar ambiente virtual
call .venv\Scripts\activate.bat

REM Instalar/atualizar dependências
echo 📦 Instalando dependências...
pip install -r requirements.txt

REM Criar diretórios necessários
if not exist "logs" mkdir logs

REM Iniciar com Waitress
echo 🔧 Iniciando servidor Waitress...
echo 📍 Acesse: http://localhost:5000
echo 🛑 Para parar: Ctrl+C

python deploy_production.py

pause
