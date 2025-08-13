from qdrant_client import QdrantClient
from qdrant_client.http import models
import openai
from config import QDRANT_URL, QDRANT_API_KEY, QDRANT_HOST, QDRANT_PORT, OPENAI_API_KEY
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

QDRANT_COLLECTION = "DM_docs_openai"

# Connect to Qdrant Cloud if URL and API key are provided, otherwise use localhost
if QDRANT_URL and QDRANT_API_KEY:
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    logger.info(f"Connected to Qdrant Cloud: {QDRANT_URL}")
else:
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    logger.info(f"Connected to local Qdrant: {QDRANT_HOST}:{QDRANT_PORT}")

def embed_text_with_openai(text: str) -> list:
    """Generate embeddings using OpenAI's text-embedding-3-small model"""
    logger.debug(f"Generating OpenAI embedding for text: {text[:100]}...")
    
    try:
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        embedding = response.data[0].embedding
        logger.debug(f"Generated OpenAI embedding with {len(embedding)} dimensions")
        return embedding
    except Exception as e:
        logger.error(f"Error generating OpenAI embedding: {e}")
        raise e

def retrieve_similar_docs(query: str, top_k: int = 3):
    logger.info(f"Retrieving similar documents for query: '{query}' (top_k={top_k})")
    
    try:
        # Generate embedding for query using OpenAI
        emb = embed_text_with_openai(query)
        logger.debug(f"Query embedding generated successfully")
        
        # Search in Qdrant
        logger.debug(f"Searching in collection: {QDRANT_COLLECTION}")
        search_result = client.search(
            collection_name=QDRANT_COLLECTION,
            query_vector=emb,
            limit=top_k
        )
        
        logger.info(f"Found {len(search_result)} similar documents")
        
        # Extract text from results
        results = []
        for i, hit in enumerate(search_result):
            score = hit.score
            text = hit.payload["text"]
            title = hit.payload.get("title", "Unknown")
            filename = hit.payload.get("filename", "Unknown")
            
            logger.debug(f"Result {i+1}: score={score:.4f}, title='{title}', file='{filename}'")
            results.append(text)
        
        logger.info(f"Returning {len(results)} document texts")
        return results
        
    except Exception as e:
        logger.error(f"Error in retrieve_similar_docs: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        # Return empty list instead of raising to prevent complete failure
        return []
