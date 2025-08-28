#!/usr/bin/env python3
"""
Aplicação Flask para o Sistema RAG - Torre de Investimentos 2025
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
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

# Adicionar o diretório src ao path
sys.path.append(str(Path(__file__).parent))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


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
        
        # Detectar ambiente e escolher configuração apropriada
        if config_path is None:
            config_file = os.environ.get('RAG_CONFIG_FILE', 'config.yaml')
            if os.environ.get('RENDER') and os.path.exists(self.project_root / 'config_production.yaml'):
                config_file = 'config_production.yaml'
            self.config_path = self.project_root / config_file
        else:
            self.config_path = config_path
            
        self.env_path = env_path or self.project_root / ".env"
        
        logger.info(f"📁 Usando configuração: {self.config_path}")
        
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
                    'context_used': "",
                    'provider_used': self.active_provider
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
            
            # Não incluir sources na resposta
            return {
                'answer': answer,
                'context_used': context,
                'provider_used': self.active_provider,
                'documents_found': len(documents)
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta RAG: {e}")
            return {
                'answer': f"Erro ao processar sua pergunta: {str(e)}",
                'context_used': "",
                'provider_used': self.active_provider
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


# Inicializar sistema RAG globalmente
try:
    rag_system = RAGSystem()
    logger.info("Sistema RAG inicializado com sucesso")
except Exception as e:
    logger.error(f"Erro ao inicializar sistema RAG: {e}")
    rag_system = None


@app.route('/imgs/<path:filename>')
def serve_images(filename):
    """Serve arquivos estáticos da pasta imgs."""
    import os
    from flask import send_from_directory
    imgs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'imgs')
    return send_from_directory(imgs_path, filename)


@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')


@app.route('/api/system-info')
def system_info():
    """API para obter informações do sistema."""
    if not rag_system:
        return jsonify({'error': 'Sistema RAG não inicializado'}), 500
    
    try:
        info = rag_system.get_system_info()
        return jsonify(info)
    except Exception as e:
        logger.error(f"Erro ao obter informações do sistema: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/query', methods=['POST'])
def query():
    """API para processar perguntas do usuário."""
    if not rag_system:
        return jsonify({'error': 'Sistema RAG não inicializado'}), 500
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        max_results = int(data.get('max_results', 5))
        max_context_tokens = int(data.get('max_context_tokens', 2000))
        
        if not question:
            return jsonify({'error': 'Pergunta não fornecida'}), 400
        
        logger.info(f"Processando pergunta: {question}")
        
        result = rag_system.generate_rag_response(question, max_context_tokens)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro ao processar pergunta: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Endpoint para verificação de saúde do serviço."""
    try:
        # Verificar se o sistema RAG está funcionando
        if not rag_system:
            return jsonify({
                'status': 'unhealthy',
                'message': 'Sistema RAG não inicializado'
            }), 503
            
        # Verificar se a coleção está acessível
        collection_count = rag_system.collection.count()
        
        return jsonify({
            'status': 'healthy',
            'message': 'Sistema operacional',
            'documents': collection_count,
            'provider': rag_system.active_provider,
            'timestamp': '2025-08-27T12:00:00Z'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'message': f'Erro interno: {str(e)}'
        }), 503


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
