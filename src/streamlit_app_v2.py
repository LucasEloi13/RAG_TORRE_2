#!/usr/bin/env python3
"""
Sistema RAG com Streamlit para Torre de Investimento Elegível 2025
Interface moderna e limpa baseada em HTML/CSS customizado.

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
    initial_sidebar_state="collapsed"
)

# CSS customizado baseado no design fornecido
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --equatorial-blue: #002D72;
        --equatorial-yellow: #FFC700;
        --background-light: #F9FAFB;
        --text-dark: #1F2937;
        --text-light: #6B7280;
        --border-color: #E5E7EB;
    }
    
    .main > div {
        padding-top: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: var(--background-light);
    }
    
    /* Header personalizado */
    .custom-header {
        background: white;
        padding: 1rem 2rem;
        border-bottom: 1px solid var(--border-color);
        margin: -2rem -2rem 2rem -2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-dark);
        margin: 0;
    }
    
    .logo-placeholder {
        background: var(--equatorial-blue);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        font-weight: 600;
        font-size: 0.875rem;
    }
    
    /* Sidebar customizada */
    .sidebar-content {
        background: white;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .sidebar-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .status-badge {
        background: #dcfce7;
        color: #166534;
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
        font-size: 0.875rem;
    }
    
    .info-label {
        color: var(--text-light);
    }
    
    .info-value {
        font-weight: 600;
        color: var(--text-dark);
    }
    
    /* Formulário principal */
    .main-form {
        background: white;
        padding: 2rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .form-label {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 0.5rem;
        display: block;
    }
    
    /* Área de resposta */
    .response-card {
        background: white;
        padding: 2rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        animation: fadeIn 0.5s ease-out;
    }
    
    .response-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }
    
    .response-icon {
        width: 1.25rem;
        height: 1.25rem;
        margin-right: 0.5rem;
        color: var(--equatorial-blue);
    }
    
    .sources-card {
        background: white;
        padding: 2rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        animation: fadeIn 0.5s ease-out 0.1s;
        animation-fill-mode: both;
    }
    
    .source-item {
        background: #f9fafb;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: 1px solid var(--border-color);
        margin-bottom: 0.75rem;
        display: flex;
        align-items: flex-start;
    }
    
    .source-icon {
        width: 1rem;
        height: 1rem;
        color: var(--text-light);
        margin-right: 0.75rem;
        margin-top: 0.125rem;
        flex-shrink: 0;
    }
    
    .source-content {
        flex: 1;
    }
    
    .source-title {
        font-weight: 600;
        color: var(--text-dark);
        font-size: 0.875rem;
        margin-bottom: 0.25rem;
    }
    
    .source-similarity {
        color: var(--text-light);
        font-size: 0.75rem;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Botões customizados */
    .stButton > button {
        background: var(--equatorial-blue) !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        border-radius: 0.5rem !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }
    
    .stButton > button:hover {
        background: #001f5c !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* TextArea customizada */
    .stTextArea > div > div > textarea {
        border: 1px solid var(--border-color) !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        outline: none !important;
        border-color: var(--equatorial-yellow) !important;
        box-shadow: 0 0 0 2px rgba(255, 199, 0, 0.2) !important;
    }
    
    /* Ocultar elementos desnecessários */
    .stDeployButton {
        display: none;
    }
    
    footer {
        display: none;
    }
    
    .stMainBlockContainer {
        padding-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)


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
        """Inicializa o sistema RAG."""
        self.project_root = Path(__file__).parent.parent
        self.config_path = config_path or self.project_root / "config.yaml"
        self.env_path = env_path or self.project_root / ".env"
        
        self._load_config()
        self._setup_ai_provider()
        self._setup_chromadb()
    
    def _load_config(self):
        """Carrega as configurações do arquivo config.yaml e .env"""
        load_dotenv(self.env_path)
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.active_provider = self.config.get('active_provider', 'openai')
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
        """Busca documentos similares à query."""
        try:
            query_embedding = self.ai_provider.generate_embedding(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            documents = []
            if results and 'documents' in results:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if 'metadatas' in results else {}
                    distance = results['distances'][0][i] if 'distances' in results else 0.0
                    
                    documents.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity': 1 - distance
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    def generate_rag_response(self, question: str, max_context_tokens: int = 2000) -> Dict[str, Any]:
        """Gera resposta usando RAG."""
        try:
            documents = self.search_documents(question, n_results=5)
            
            if not documents:
                return {
                    'answer': "Desculpe, não encontrei informações relevantes para responder sua pergunta.",
                    'sources': [],
                    'context_used': ""
                }
            
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
            
            prompt_config = self.config['prompt_config']
            
            full_prompt = f"""
{prompt_config['persona']}

{prompt_config['contexto'].format(contexto=context)}

{prompt_config['pergunta'].format(pergunta=question)}

{prompt_config['instructions']}
"""
            
            answer = self.ai_provider.generate_response(full_prompt)
            
            sources = []
            for doc in documents[:3]:
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
                'provider_used': self.active_provider
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
            return {
                'provider': self.active_provider,
                'collection_name': self.collection_name,
                'embedding_model': self.config['ai_providers'][self.active_provider]['models'].get('embedding', 'N/A'),
                'chat_model': self.config['ai_providers'][self.active_provider]['models']['chat']
            }
        except Exception as e:
            logger.error(f"Erro ao obter informações do sistema: {e}")
            return {}


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
    
    # Header customizado
    st.markdown("""
    <div class="custom-header">
        <h1 class="header-title">Torre de Investimentos Elegível 2025</h1>
        <div class="logo-placeholder">Equatorial</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Layout com colunas
    col1, col2 = st.columns([3, 1])
    
    with col2:
        # Sidebar com informações do sistema
        with st.spinner("🔄 Carregando sistema..."):
            rag_system = get_rag_system()
        
        if not rag_system:
            st.error("❌ Falha ao carregar o sistema RAG")
            st.info("💡 Certifique-se de que:")
            st.write("- O banco vetorial foi criado")
            st.write("- As variáveis de ambiente estão configuradas")
            st.stop()
        
        # Informações do sistema
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">Informações do Sistema</div>', unsafe_allow_html=True)
        
        try:
            system_info = rag_system.get_system_info()
            
            st.markdown("""
            <div class="info-row">
                <span class="info-label">Status:</span>
                <span class="status-badge">Ativo</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="info-row">
                <span class="info-label">Provedor:</span>
                <span class="info-value">{system_info.get('provider', 'N/A').title()}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="info-row">
                <span class="info-label">Modelo Chat:</span>
                <span class="info-value">{system_info.get('chat_model', 'N/A')}</span>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Erro ao obter informações: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col1:
        # Formulário principal
        st.markdown('<div class="main-form">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">Faça sua pergunta:</label>', unsafe_allow_html=True)
        
        question = st.text_area(
            "",
            height=100,
            placeholder="Ex: Como é calculado o AFFA? Quais são os indicadores da Torre Elegível em 2025?",
            label_visibility="collapsed",
            key="question_input"
        )
        
        col_left, col_right = st.columns([1, 1])
        with col_right:
            submit = st.button("🔍 Consultar", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Processamento da pergunta
        if submit and question.strip():
            with st.spinner("🔄 Processando sua pergunta..."):
                result = rag_system.generate_rag_response(question)
                
                # Área de resposta
                st.markdown(f"""
                <div class="response-card">
                    <div class="response-title">
                        <svg class="response-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.959 8.959 0 01-4.906-1.452L3 21l2.548-5.094A8.959 8.959 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z"></path>
                        </svg>
                        Resposta
                    </div>
                    <div>{result['answer']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Fontes consultadas
                if result.get('sources'):
                    st.markdown("""
                    <div class="sources-card">
                        <div class="response-title">
                            <svg class="response-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                            </svg>
                            Fontes Consultadas
                        </div>
                    """, unsafe_allow_html=True)
                    
                    for source in result['sources']:
                        similarity_pct = source['similarity'] * 100
                        st.markdown(f"""
                        <div class="source-item">
                            <svg class="source-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                            <div class="source-content">
                                <div class="source-title">{source['section']}</div>
                                <div class="source-similarity">Similaridade: {similarity_pct:.1f}%</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        
        elif submit and not question.strip():
            st.warning("⚠️ Por favor, digite uma pergunta.")


if __name__ == "__main__":
    main()
