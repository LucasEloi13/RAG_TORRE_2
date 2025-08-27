#!/usr/bin/env python3
"""
Deploy para Render.com - Torre de Investimentos RAG
"""
import os
import sys

# Configurar ambiente
os.environ.setdefault('FLASK_ENV', 'production')

# Configurar path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def create_app():
    """Factory para criar a aplicação Flask."""
    try:
        from app import app
        app.config['DEBUG'] = False
        return app
    except Exception as e:
        print(f"❌ Erro ao importar app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    from waitress import serve
    
    # Obter porta do ambiente (Render usa PORT)
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print("🚀 Torre de Investimentos RAG - Render Deploy")
    print(f"📍 Host: {host}:{port}")
    print("🔧 Servidor: Waitress")
    
    # Criar aplicação
    app = create_app()
    
    # Servir com Waitress
    serve(
        app,
        host=host,
        port=port,
        threads=4,
        connection_limit=200,
        cleanup_interval=30
    )
