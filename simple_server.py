#!/usr/bin/env python3
"""
Alternativa simples para Render - sem waitress
"""
import os
import sys

# Configurar path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

if __name__ == '__main__':
    from app import app
    
    # Configurações do Render
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"🚀 RAG Torre iniciando em {host}:{port}")
    
    # Executar Flask diretamente (para desenvolvimento/teste)
    app.run(
        host=host,
        port=port,
        debug=False,
        threaded=True
    )
