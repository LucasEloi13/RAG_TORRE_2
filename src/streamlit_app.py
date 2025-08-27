#!/usr/bin/env python3
"""
Sistema RAG com Streamlit para Torre de Investimento Elegível 2025

Este aplicativo permite consultar o documento Torre de Investimento Elegível 2025
usando um sistema RAG (Retrieval-Augmented Generation) com diferentes provedores de IA.

Autor: Sistema RAG Torre
Data: 2025-08-27
"""

import streamlit as st
import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import tiktoken
import json
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da página Streamlit
st.set_page_config(
    page_title="RAG Torre de Investimentos 2025",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)


class AIProvider:
    """Classe base para provedores de IA."""
    
    def __init__(self, config: Dict[str, Any], api_key: str):
        self.config = config
        self.api_key = api_key
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Configura o cliente da API."""
        raise NotImplementedError
    
    def generate_embedding(self, text: str) -> List[float]:
        """Gera embedding para um texto."""
        raise NotImplementedError
    
    def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Gera resposta para um prompt."""
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """Provedor OpenAI."""
    
    def _setup_client(self):
        """Configura o cliente da OpenAI."""
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.config.get('base_url', 'https://api.openai.com/v1')
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """Gera embedding usando OpenAI."""
        try:
            response = self.client.embeddings.create(
                model=self.config['models']['embedding'],
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding OpenAI: {e}")
            raise
    
    def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Gera resposta usando OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.config['models']['chat'],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens or self.config.get('max_tokens', 4096),
                temperature=self.config.get('temperature', 0.5)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao gerar resposta OpenAI: {e}")
            raise


class DeepSeekProvider(AIProvider):
    """Provedor DeepSeek."""
    
    def _setup_client(self):
        """Configura o cliente da DeepSeek."""
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.config.get('base_url', 'https://api.deepseek.com/v1')
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """DeepSeek não tem embedding próprio, usa OpenAI como fallback."""
        # Para embedding, vamos usar OpenAI como fallback
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("API key da OpenAI necessária para embeddings")
        
        openai_client = OpenAI(api_key=openai_key)
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Gera resposta usando DeepSeek."""
        try:
            response = self.client.chat.completions.create(
                model=self.config['models']['chat'],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens or self.config.get('max_tokens', 4096),
                temperature=self.config.get('temperature', 0.5)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao gerar resposta DeepSeek: {e}")
            raise


class RAGSystem:
    """Sistema RAG para consulta de documentos."""
    
    def __init__(self, config_path: str = None, env_path: str = None):
        """
        Inicializa o sistema RAG.
        
        Args:
            config_path: Caminho para o arquivo config.yaml
            env_path: Caminho para o arquivo .env
        """
        # Configurar caminhos
        self.project_root = Path(__file__).parent.parent
        self.config_path = config_path or self.project_root / "config.yaml"
        self.env_path = env_path or self.project_root / ".env"
        
        # Carregar configurações
        self._load_config()
        self._setup_ai_provider()
        self._setup_chromadb()
    
    def _load_config(self):
        """Carrega as configurações do arquivo config.yaml e .env"""
        # Carregar variáveis de ambiente
        load_dotenv(self.env_path)
        
        # Carregar config.yaml
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Obter provedor ativo
        self.active_provider = self.config.get('active_provider', 'openai')
        
        # Configurações do ChromaDB
        self.vector_db_path = os.getenv('VECTOR_DB_PATH', './data/embeddings')
        self.collection_name = os.getenv('COLLECTION_NAME', 'documents')
        
        logger.info(f"Provedor ativo: {self.active_provider}")
    
    def _setup_ai_provider(self):
        """Configura o provedor de IA."""
        provider_config = self.config['ai_providers'][self.active_provider]
        api_key_env = provider_config['api_key_env']
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            raise ValueError(f"API key não encontrada na variável de ambiente: {api_key_env}")
        
        if self.active_provider == 'openai':
            self.ai_provider = OpenAIProvider(provider_config, api_key)
        elif self.active_provider == 'deepseek':
            self.ai_provider = DeepSeekProvider(provider_config, api_key)
        else:
            raise ValueError(f"Provedor não suportado: {self.active_provider}")
        
        logger.info(f"Provedor {self.active_provider} configurado com sucesso")
    
    def _setup_chromadb(self):
        """Configura o cliente ChromaDB."""
        db_path = Path(self.vector_db_path)
        
        if not db_path.exists():
            raise FileNotFoundError(f"Banco vetorial não encontrado em: {db_path}")
        
        self.chroma_client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            logger.info(f"Coleção '{self.collection_name}' carregada")
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar coleção: {e}")
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca documentos similares à query.
        
        Args:
            query: Texto da consulta
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de documentos encontrados
        """
        try:
            # Gerar embedding da query
            query_embedding = self.ai_provider.generate_embedding(query)
            
            # Buscar no ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Formatar resultados
            documents = []
            if results and 'documents' in results:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if 'metadatas' in results else {}
                    distance = results['distances'][0][i] if 'distances' in results else 0.0
                    
                    documents.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity': 1 - distance  # Converter distância em similaridade
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    def generate_rag_response(self, question: str, max_context_tokens: int = 2000) -> Dict[str, Any]:
        """
        Gera resposta usando RAG.
        
        Args:
            question: Pergunta do usuário
            max_context_tokens: Número máximo de tokens para o contexto
            
        Returns:
            Dicionário com resposta e metadados
        """
        try:
            # Buscar documentos relevantes
            documents = self.search_documents(question, n_results=5)
            
            if not documents:
                return {
                    'answer': "Desculpe, não encontrei informações relevantes para responder sua pergunta.",
                    'sources': [],
                    'context_used': ""
                }
            
            # Construir contexto
            context_parts = []
            total_tokens = 0
            encoding = tiktoken.encoding_for_model("gpt-4")
            
            for doc in documents:
                content = doc['content']
                tokens = len(encoding.encode(content))
                
                if total_tokens + tokens <= max_context_tokens:
                    context_parts.append(content)
                    total_tokens += tokens
                else:
                    break
            
            context = "\n\n".join(context_parts)
            
            # Construir prompt usando configuração do config.yaml
            prompt_config = self.config['prompt_config']
            
            full_prompt = f"""
{prompt_config['persona']}

{prompt_config['contexto'].format(contexto=context)}

{prompt_config['pergunta'].format(pergunta=question)}

{prompt_config['instructions']}
"""
            
            # Gerar resposta
            answer = self.ai_provider.generate_response(full_prompt)
            
            # Extrair fontes
            sources = []
            for doc in documents[:3]:  # Máximo 3 fontes
                metadata = doc['metadata']
                source_info = {
                    'section': metadata.get('section', 'Seção não identificada'),
                    'similarity': doc['similarity'],
                    'chunk_index': metadata.get('chunk_index', 0)
                }
                sources.append(source_info)
            
            return {
                'answer': answer,
                'sources': sources,
                'context_used': context,
                'provider_used': self.active_provider,
                'documents_found': len(documents)
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta RAG: {e}")
            return {
                'answer': f"Erro ao processar sua pergunta: {str(e)}",
                'sources': [],
                'context_used': ""
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o sistema."""
        try:
            collection_count = self.collection.count()
            return {
                'provider': self.active_provider,
                'collection_name': self.collection_name,
                'documents_count': collection_count,
                'embedding_model': self.config['ai_providers'][self.active_provider]['models'].get('embedding', 'N/A'),
                'chat_model': self.config['ai_providers'][self.active_provider]['models']['chat']
            }
        except Exception as e:
            logger.error(f"Erro ao obter informações do sistema: {e}")
            return {}


# Cache do sistema RAG
@st.cache_resource
def get_rag_system():
    """Carrega o sistema RAG (cached)."""
    try:
        return RAGSystem()
    except Exception as e:
        st.error(f"Erro ao inicializar sistema RAG: {e}")
        st.exception(e)
        return None


def main():
    """Função principal do aplicativo Streamlit."""
    
    # Título principal
    st.title("🏗️ Sistema RAG - Torre de Investimentos 2025")
    st.markdown("Sistema de consulta inteligente para documentos da Torre de Investimento Elegível 2025")
    st.markdown("---")
    
    # Tentar carregar sistema RAG
    with st.spinner("🔄 Inicializando sistema RAG..."):
        rag_system = get_rag_system()
    
    if not rag_system:
        st.error("❌ Falha ao carregar o sistema RAG. Verifique as configurações.")
        st.info("💡 Certifique-se de que:")
        st.write("- O banco vetorial foi criado executando `generate_embeddings.py`")
        st.write("- As variáveis de ambiente estão configuradas no arquivo `.env`")
        st.write("- O arquivo `config.yaml` possui as configurações corretas")
        st.stop()
    
    # Sidebar com informações do sistema
    with st.sidebar:
        st.header("📊 Informações do Sistema")
        
        try:
            system_info = rag_system.get_system_info()
            
            if system_info:
                st.success("✅ Sistema RAG ativo")
                st.write(f"**Provedor:** {system_info.get('provider', 'N/A')}")
                st.write(f"**Modelo Chat:** {system_info.get('chat_model', 'N/A')}")
                st.write(f"**Modelo Embedding:** {system_info.get('embedding_model', 'N/A')}")
                st.write(f"**Documentos:** {system_info.get('documents_count', 0)}")
                st.write(f"**Coleção:** {system_info.get('collection_name', 'N/A')}")
            else:
                st.warning("⚠️ Informações do sistema indisponíveis")
        except Exception as e:
            st.error(f"Erro ao obter informações: {e}")
        
        st.markdown("---")
        st.markdown("### 💡 Dicas de Uso")
        st.markdown("""
        - Faça perguntas específicas sobre Torre de Investimentos
        - Use termos como AFFA, PM, IQO, VR_Distribuidora
        - Pergunte sobre fórmulas e cálculos
        - Solicite exemplos práticos
        """)
    
    # Interface principal
    st.header("💬 Faça sua Pergunta")
    
    # Input da pergunta
    question = st.text_area(
        "Digite sua pergunta sobre Torre de Investimentos 2025:",
        height=100,
        placeholder="Ex: Como é calculado o AFFA? Quais são os indicadores da Torre Elegível em 2025?",
        value=st.session_state.get('selected_question', ''),
        key="question_input"
    )
    
    # Configurações avançadas
    with st.expander("⚙️ Configurações Avançadas"):
        col1, col2 = st.columns(2)
        with col1:
            max_results = st.slider("Documentos para busca", 1, 10, 5)
        with col2:
            max_context_tokens = st.slider("Tokens para contexto", 500, 4000, 2000)
    
    # Botão de consulta
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Consultar", type="primary", use_container_width=True):
            if question.strip():
                with st.spinner("🔄 Processando sua pergunta..."):
                    try:
                        # Gerar resposta RAG
                        result = rag_system.generate_rag_response(
                            question, 
                            max_context_tokens=max_context_tokens
                        )
                        
                        # Exibir resposta
                        st.markdown("### 📝 Resposta")
                        st.markdown(result['answer'])
                        
                        # Informações adicionais
                        if result.get('sources'):
                            st.markdown("### 📚 Fontes Consultadas")
                            for i, source in enumerate(result['sources'], 1):
                                similarity_pct = source['similarity'] * 100
                                st.write(f"**{i}.** {source['section']} (Similaridade: {similarity_pct:.1f}%)")
                        
                        # Metadados
                        with st.expander("🔍 Detalhes da Consulta"):
                            st.write(f"**Provedor usado:** {result.get('provider_used', 'N/A')}")
                            st.write(f"**Documentos encontrados:** {result.get('documents_found', 0)}")
                            st.write(f"**Tokens do contexto:** {len(result.get('context_used', '').split())}")
                            
                            if result.get('context_used'):
                                st.markdown("**Contexto utilizado:**")
                                st.text_area("", result['context_used'], height=200, key="context_display")
                    
                    except Exception as e:
                        st.error(f"❌ Erro ao processar pergunta: {e}")
                        st.exception(e)
            else:
                st.warning("⚠️ Por favor, digite uma pergunta.")
    
    # Perguntas sugeridas
    st.markdown("---")
    st.header("📖 Perguntas Sugeridas")
    
    sample_questions = [
        "O que é AFFA e como é calculado?",
        "Quais são os três indicadores da Torre Elegível em 2025?",
        "Como funciona o Prazo Médio (PM)?",
        "O que é IQO - Índice de Qualidade de Obras?",
        "Como calcular o VR_Distribuidora?",
        "Quais as mudanças em relação a 2024?",
        "Como é feito o cálculo de Capitalização Ajustada?",
        "O que são obras AT?",
        "Como funciona o modelo de execução de obras?",
        "Qual é a fórmula do Avanço Físico?"
    ]
    
    cols = st.columns(2)
    for i, q in enumerate(sample_questions):
        col = cols[i % 2]
        with col:
            if st.button(q, key=f"sample_{i}", use_container_width=True):
                st.session_state.selected_question = q
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>🏗️ Sistema RAG - Torre de Investimentos Elegível 2025</p>
            <p>Desenvolvido com Streamlit • Powered by AI</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
