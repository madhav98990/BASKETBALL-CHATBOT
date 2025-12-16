"""
Vector Embeddings and Pinecone Integration
Generates embeddings using sentence-transformers and stores in Pinecone
"""
import os
import sys
# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Windows workaround for readline module
try:
    import readline
except ImportError:
    # readline is not available on Windows, create a dummy module
    import sys
    class DummyReadline:
        pass
    sys.modules['readline'] = DummyReadline()

import pinecone
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import logging
from typing import List, Dict
import re

from config import (
    PINECONE_API_KEY, 
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX_NAME,
    PINECONE_DIMENSION,
    ARTICLES_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector embeddings and Pinecone storage"""
    
    def __init__(self):
        self.model = None
        self.pinecone_index = None
        self.embedding_model_name = "all-MiniLM-L6-v2"
        
    def initialize_model(self):
        """Initialize sentence transformer model"""
        logger.info(f"Loading embedding model: {self.embedding_model_name}")
        self.model = SentenceTransformer(self.embedding_model_name)
        logger.info("Embedding model loaded")
    
    def initialize_pinecone(self):
        """Initialize Pinecone connection and index"""
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not set in environment variables")
        
        logger.info("Initializing Pinecone...")
        
        # New Pinecone API (v3+)
        try:
            from pinecone import Pinecone
            pc = Pinecone(api_key=PINECONE_API_KEY)
            
            # Check if index exists
            existing_indexes = [idx.name for idx in pc.list_indexes()]
            
            if PINECONE_INDEX_NAME not in existing_indexes:
                logger.info(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
                from pinecone import ServerlessSpec
                pc.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=PINECONE_DIMENSION,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT)
                )
                logger.info("Index created. Waiting for it to be ready...")
                import time
                time.sleep(5)  # Wait for index to be ready
            else:
                logger.info(f"Index {PINECONE_INDEX_NAME} already exists")
            
            self.pinecone_index = pc.Index(PINECONE_INDEX_NAME)
            logger.info("Pinecone initialized")
            
        except ImportError:
            # Fallback to old API
            logger.warning("New Pinecone API not available, trying legacy API...")
            pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
            existing_indexes = pinecone.list_indexes()
            if PINECONE_INDEX_NAME not in existing_indexes:
                pinecone.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=PINECONE_DIMENSION,
                    metric="cosine"
                )
            self.pinecone_index = pinecone.Index(PINECONE_INDEX_NAME)
            logger.info("Pinecone initialized (legacy API)")
    
    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Split text into chunks with overlap"""
        words = text.split()
        chunks = []
        
        if len(words) <= chunk_size:
            return [text]
        
        i = 0
        while i < len(words):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += chunk_size - overlap
        
        return chunks
    
    def load_articles(self) -> List[Dict]:
        """Load all articles from directory"""
        articles = []
        
        if not os.path.exists(ARTICLES_DIR):
            logger.error(f"Articles directory not found: {ARTICLES_DIR}")
            return articles
        
        article_files = sorted([f for f in os.listdir(ARTICLES_DIR) if f.endswith('.txt')])
        
        logger.info(f"Found {len(article_files)} article files")
        
        for filename in article_files:
            filepath = os.path.join(ARTICLES_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        articles.append({
                            'filename': filename,
                            'content': content
                        })
            except Exception as e:
                logger.error(f"Error reading {filename}: {e}")
        
        return articles
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if not self.model:
            self.initialize_model()
        
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()
    
    def upload_to_pinecone(self, vectors: List[Dict]):
        """Upload vectors to Pinecone in batches"""
        if not self.pinecone_index:
            self.initialize_pinecone()
        
        batch_size = 100
        total_batches = (len(vectors) + batch_size - 1) // batch_size
        
        logger.info(f"Uploading {len(vectors)} vectors to Pinecone in {total_batches} batches...")
        
        for i in tqdm(range(0, len(vectors), batch_size), desc="Uploading to Pinecone"):
            batch = vectors[i:i + batch_size]
            self.pinecone_index.upsert(vectors=batch)
        
        logger.info("Upload complete")
    
    def build_vector_store(self):
        """Main function to build vector store from articles"""
        logger.info("Building vector store...")
        
        # Initialize components
        self.initialize_model()
        self.initialize_pinecone()
        
        # Load articles
        articles = self.load_articles()
        
        if not articles:
            logger.warning("No articles found. Please run the scraper first.")
            return
        
        # Process articles into chunks
        all_chunks = []
        chunk_metadata = []
        
        for article in tqdm(articles, desc="Chunking articles"):
            chunks = self.chunk_text(article['content'])
            
            for chunk_idx, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                chunk_metadata.append({
                    'filename': article['filename'],
                    'chunk_index': chunk_idx,
                    'text': chunk
                })
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(articles)} articles")
        
        # Generate embeddings
        embeddings = self.generate_embeddings(all_chunks)
        
        # Prepare vectors for Pinecone
        vectors = []
        for idx, (embedding, metadata) in enumerate(zip(embeddings, chunk_metadata)):
            vectors.append({
                'id': f"{metadata['filename']}_{metadata['chunk_index']}",
                'values': embedding,
                'metadata': {
                    'filename': metadata['filename'],
                    'chunk_index': metadata['chunk_index'],
                    'text': metadata['text'][:1000]  # Limit metadata text length
                }
            })
        
        # Upload to Pinecone
        self.upload_to_pinecone(vectors)
        
        logger.info("Vector store build complete!")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar articles in Pinecone"""
        if not self.model:
            self.initialize_model()
        
        if not self.pinecone_index:
            self.initialize_pinecone()
        
        # Generate query embedding
        query_embedding = self.model.encode([query])[0].tolist()
        
        # Search Pinecone
        results = self.pinecone_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results
        formatted_results = []
        for match in results.matches:
            formatted_results.append({
                'score': match.score,
                'text': match.metadata.get('text', ''),
                'filename': match.metadata.get('filename', '')
            })
        
        return formatted_results


if __name__ == "__main__":
    import sys
    print("Starting vector store build...", file=sys.stderr)
    print("Starting vector store build...")
    sys.stdout.flush()
    sys.stderr.flush()
    
    vector_store = VectorStore()
    vector_store.build_vector_store()
    
    print("Vector store build completed!", file=sys.stderr)
    print("Vector store build completed!")
    sys.stdout.flush()
    sys.stderr.flush()

