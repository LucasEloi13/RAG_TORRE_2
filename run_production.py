#!/usr/bin/env python3
"""
Script para executar a aplicação RAG em modo produção
"""
import os
import sys
from src.app import app

if __name__ == '__main__':
    # Configurações de produção
    app.config['DEBUG'] = False
    
    # Executar com Gunicorn
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Iniciando aplicação RAG em modo produção")
    print(f"📍 URL: http://{host}:{port}")
    print(f"🔧 Para parar: Ctrl+C")
    
    app.run(host=host, port=port, debug=False)
