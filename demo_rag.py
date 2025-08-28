#!/usr/bin/env python3
"""
Script de demonstração do Sistema RAG via linha de comando
para Torre de Investimento Elegível 2025

Autor: Sistema RAG Torre
Data: 2025-08-27
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path para importar o módulo
sys.path.append(str(Path(__file__).parent / "src"))

from streamlit_app import RAGSystem


def main():
    """Demonstração do sistema RAG via CLI."""
    print("Sistema RAG - Torre de Investimentos 2025")
    print("=" * 50)
    
    try:
        # Inicializar sistema RAG
        print("📡 Inicializando sistema RAG...")
        rag_system = RAGSystem()
        
        # Obter informações do sistema
        system_info = rag_system.get_system_info()
        print("\n📊 Informações do Sistema:")
        print(f"   • Provedor: {system_info.get('provider', 'N/A')}")
        print(f"   • Modelo Chat: {system_info.get('chat_model', 'N/A')}")
        print(f"   • Modelo Embedding: {system_info.get('embedding_model', 'N/A')}")
        print(f"   • Documentos: {system_info.get('documents_count', 0)}")
        print(f"   • Coleção: {system_info.get('collection_name', 'N/A')}")
        
        # Perguntas de demonstração
        demo_questions = [
            "O que é AFFA e como é calculado?",
            "Quais são os três indicadores da Torre Elegível em 2025?",
            "Como funciona o Prazo Médio (PM)?",
            "Quais as principais mudanças em relação a 2024?"
        ]
        
        print("\n🔍 Demonstração de Consultas:")
        print("-" * 50)
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n{i}. Pergunta: {question}")
            print("   Processando...")
            
            # Gerar resposta
            result = rag_system.generate_rag_response(question)
            
            print(f"   📝 Resposta ({result.get('provider_used', 'N/A')}):")
            # Exibir resposta completa, mas quebrar em linhas para melhor legibilidade
            answer_lines = result['answer'].split('\n')
            for line in answer_lines:
                if line.strip():  # Só imprime linhas não vazias
                    print(f"   {line}")
            
            if result.get('sources'):
                print(f"   📚 Fontes: {len(result['sources'])} documento(s)")
                for j, source in enumerate(result['sources'][:2], 1):
                    similarity = source['similarity'] * 100
                    print(f"      {j}. {source['section']} ({similarity:.1f}%)")
            
            print()
        
        # Modo interativo
        print("\n💬 Modo Interativo")
        print("Digite suas perguntas (ou 'sair' para terminar):")
        print("-" * 50)
        
        while True:
            try:
                question = input("\n❓ Sua pergunta: ").strip()
                
                if question.lower() in ['sair', 'exit', 'quit', '']:
                    break
                
                print("   🔄 Processando...")
                result = rag_system.generate_rag_response(question)
                
                print(f"\n   📝 Resposta:")
                # Exibir resposta completa com formatação melhorada
                answer_lines = result['answer'].split('\n')
                for line in answer_lines:
                    if line.strip():
                        print(f"   {line}")
                    else:
                        print()  # Linha vazia para preservar quebras de parágrafo
                
                if result.get('sources'):
                    print(f"\n   📚 Fontes consultadas:")
                    for j, source in enumerate(result['sources'], 1):
                        similarity = source['similarity'] * 100
                        print(f"      {j}. {source['section']} (Similaridade: {similarity:.1f}%)")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"   ❌ Erro: {e}")
        
        print("\n👋 Obrigado por usar o Sistema RAG!")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar sistema: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
