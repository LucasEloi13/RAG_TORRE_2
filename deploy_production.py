#!/usr/bin/env python3
"""
Deploy de produção usando Waitress (compatível com Windows)
Torre de Investimentos - Sistema RAG
"""
from waitress import serve
from src.app import app
import os

if __name__ == '__main__':
    # Render usa a variável PORT
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print("🚀 Iniciando Sistema RAG - Torre de Investimentos 2025")
    print(f"📍 Servidor: http://{host}:{port}")
    print(f"🔧 Servidor: Waitress (Produção)")
    print(f"🛑 Para parar: Ctrl+C")
    print("=" * 50)
    
    serve(
        app, 
        host=host, 
        port=port,
        threads=8,
        connection_limit=1000,
        cleanup_interval=30,
        channel_timeout=120
    )
