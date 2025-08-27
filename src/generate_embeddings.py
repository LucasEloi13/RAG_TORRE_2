#!/usr/bin/env python3
"""
Script para gerar embeddings do documento Torre de Investimento Elegível 2025
e armazenar no ChromaDB.

Autor: Sistema RAG Torre
Data: 2025-08-27
"""

import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any
import logging
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import tiktoken

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentEmbedder:
    """Classe para processar documentos e gerar embeddings."""
    
    def __init__(self, config_path: str = None, env_path: str = None):
        """
        Inicializa o DocumentEmbedder.
        
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
        self._setup_openai_client()
        self._setup_chromadb()
        
        # Configurar tokenizer para chunking
        self.encoding = tiktoken.encoding_for_model(self.embedding_model)
        
    def _load_config(self):
        """Carrega as configurações do arquivo config.yaml e .env"""
        # Carregar variáveis de ambiente
        load_dotenv(self.env_path)
        
        # Carregar config.yaml
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Extrair configurações da OpenAI
        openai_config = self.config['ai_providers']['openai']
        self.embedding_model = openai_config['models']['embedding']
        self.api_key = os.getenv(openai_config['api_key_env'])
        
        if not self.api_key:
            raise ValueError(f"API key não encontrada na variável de ambiente: {openai_config['api_key_env']}")
        
        # Configurações do ChromaDB
        self.vector_db_path = os.getenv('VECTOR_DB_PATH', './data/embeddings')
        self.collection_name = os.getenv('COLLECTION_NAME', 'documents')
        
        logger.info(f"Configurações carregadas:")
        logger.info(f"- Modelo de embedding: {self.embedding_model}")
        logger.info(f"- Caminho do banco vetorial: {self.vector_db_path}")
        logger.info(f"- Nome da coleção: {self.collection_name}")
    
    def _setup_openai_client(self):
        """Configura o cliente da OpenAI."""
        self.openai_client = OpenAI(api_key=self.api_key)
        logger.info("Cliente OpenAI configurado com sucesso")
    
    def _setup_chromadb(self):
        """Configura o cliente ChromaDB."""
        # Criar diretório se não existir
        db_path = Path(self.vector_db_path)
        db_path.mkdir(parents=True, exist_ok=True)
        
        # Configurar ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Criar ou obter coleção
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            logger.info(f"Coleção '{self.collection_name}' carregada")
        except Exception:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Torre de Investimento Elegível 2025 - Documentos"}
            )
            logger.info(f"Coleção '{self.collection_name}' criada")
    
    def _count_tokens(self, text: str) -> int:
        """Conta o número de tokens em um texto."""
        return len(self.encoding.encode(text))
    
    def _chunk_text(self, text: str, max_tokens: int = 1000, overlap_tokens: int = 100) -> List[str]:
        """
        Divide o texto em chunks menores.
        
        Args:
            text: Texto para dividir
            max_tokens: Número máximo de tokens por chunk
            overlap_tokens: Número de tokens de sobreposição entre chunks
            
        Returns:
            Lista de chunks de texto
        """
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for paragraph in paragraphs:
            paragraph_tokens = self._count_tokens(paragraph)
            
            # Se o parágrafo sozinho é muito grande, divida-o
            if paragraph_tokens > max_tokens:
                # Se já temos conteúdo no chunk atual, salve-o
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                    current_tokens = 0
                
                # Dividir parágrafo grande em sentenças
                sentences = paragraph.split('. ')
                for sentence in sentences:
                    sentence_tokens = self._count_tokens(sentence + '. ')
                    
                    if current_tokens + sentence_tokens > max_tokens:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            # Manter overlap
                            overlap_text = '. '.join(current_chunk.split('. ')[-2:])
                            current_chunk = overlap_text + '. ' + sentence + '. '
                            current_tokens = self._count_tokens(current_chunk)
                        else:
                            current_chunk = sentence + '. '
                            current_tokens = sentence_tokens
                    else:
                        current_chunk += sentence + '. '
                        current_tokens += sentence_tokens
            else:
                # Verificar se adicionar este parágrafo excederia o limite
                if current_tokens + paragraph_tokens > max_tokens:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        # Manter overlap
                        overlap_text = '\n\n'.join(current_chunk.split('\n\n')[-1:])
                        current_chunk = overlap_text + '\n\n' + paragraph
                        current_tokens = self._count_tokens(current_chunk)
                    else:
                        current_chunk = paragraph
                        current_tokens = paragraph_tokens
                else:
                    if current_chunk:
                        current_chunk += '\n\n' + paragraph
                    else:
                        current_chunk = paragraph
                    current_tokens += paragraph_tokens
        
        # Adicionar o último chunk se houver conteúdo
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para um texto usando a API da OpenAI.
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Lista de floats representando o embedding
        """
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            raise
    
    def _extract_metadata(self, chunk: str, chunk_index: int, total_chunks: int, file_path: str) -> Dict[str, Any]:
        """
        Extrai metadados de um chunk de texto.
        
        Args:
            chunk: Texto do chunk
            chunk_index: Índice do chunk
            total_chunks: Total de chunks do documento
            file_path: Caminho do arquivo original
            
        Returns:
            Dicionário com metadados
        """
        metadata = {
            "source": str(file_path),
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,
            "chunk_size": len(chunk),
            "token_count": self._count_tokens(chunk),
            "document_type": "markdown"
        }
        
        # Extrair informações específicas do conteúdo
        if "## " in chunk:
            # Encontrar o primeiro cabeçalho de seção
            lines = chunk.split('\n')
            for line in lines:
                if line.startswith('## '):
                    metadata["section"] = line.replace('## ', '').strip()
                    break
        
        if "### " in chunk:
            # Encontrar o primeiro subcabeçalho
            lines = chunk.split('\n')
            for line in lines:
                if line.startswith('### '):
                    metadata["subsection"] = line.replace('### ', '').strip()
                    break
        
        # Identificar se contém fórmulas ou exemplos
        if any(keyword in chunk.lower() for keyword in ['fórmula', 'cálculo', 'exemplo']):
            metadata["contains_formula"] = True
        
        if any(keyword in chunk.lower() for keyword in ['affa', 'pm', 'iqo', 'vr_distribuidora']):
            metadata["contains_indicators"] = True
        
        return metadata
    
    def process_document(self, file_path: str) -> bool:
        """
        Processa um documento markdown e gera embeddings.
        
        Args:
            file_path: Caminho para o arquivo markdown
            
        Returns:
            True se processado com sucesso, False caso contrário
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"Arquivo não encontrado: {file_path}")
                return False
            
            logger.info(f"Processando documento: {file_path}")
            
            # Ler o arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Documento carregado. Tamanho: {len(content)} caracteres")
            
            # Dividir em chunks
            chunks = self._chunk_text(content)
            logger.info(f"Documento dividido em {len(chunks)} chunks")
            
            # Processar cada chunk
            embeddings = []
            metadatas = []
            documents = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processando chunk {i+1}/{len(chunks)}")
                
                # Gerar embedding
                embedding = self._generate_embedding(chunk)
                
                # Extrair metadados
                metadata = self._extract_metadata(chunk, i, len(chunks), file_path)
                
                # Preparar dados para inserção
                embeddings.append(embedding)
                metadatas.append(metadata)
                documents.append(chunk)
                ids.append(f"{file_path.stem}_chunk_{i}")
            
            # Inserir no ChromaDB
            logger.info("Inserindo embeddings no ChromaDB...")
            self.collection.add(
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents,
                ids=ids
            )
            
            logger.info(f"✅ Documento processado com sucesso! {len(chunks)} chunks inseridos.")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar documento: {e}")
            return False
    
    def query_similar(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Busca documentos similares à query.
        
        Args:
            query: Texto da consulta
            n_results: Número de resultados a retornar
            
        Returns:
            Resultados da busca
        """
        try:
            # Gerar embedding da query
            query_embedding = self._generate_embedding(query)
            
            # Buscar no ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return {}
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Retorna informações sobre a coleção."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "embedding_model": self.embedding_model
            }
        except Exception as e:
            logger.error(f"Erro ao obter informações da coleção: {e}")
            return {}


def main():
    """Função principal do script."""
    try:
        # Inicializar o embedder
        embedder = DocumentEmbedder()
        
        # Caminho do documento
        doc_path = embedder.project_root / "data" / "documents" / "torre_investimento_elegivel_2025.md"
        
        if not doc_path.exists():
            logger.error(f"Documento não encontrado: {doc_path}")
            sys.exit(1)
        
        # Processar o documento
        logger.info("Iniciando processamento do documento...")
        success = embedder.process_document(doc_path)
        
        if success:
            # Mostrar informações da coleção
            info = embedder.get_collection_info()
            logger.info(f"📊 Informações da coleção:")
            logger.info(f"   - Nome: {info.get('collection_name', 'N/A')}")
            logger.info(f"   - Documentos: {info.get('document_count', 'N/A')}")
            logger.info(f"   - Modelo: {info.get('embedding_model', 'N/A')}")
            
            # Teste rápido de busca
            logger.info("\n🔍 Teste de busca:")
            results = embedder.query_similar("AFFA avanço físico", n_results=3)
            
            if results and 'documents' in results:
                for i, doc in enumerate(results['documents'][0][:2]):
                    logger.info(f"   Resultado {i+1}: {doc[:100]}...")
            
            logger.info("\n✅ Script executado com sucesso!")
        else:
            logger.error("❌ Falha no processamento do documento")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Erro na execução: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
