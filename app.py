from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from orchestrator import answer_query
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI RAG + SerpApi + Gemini")

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
def ask_question(req: QueryRequest):
    logger.info(f"Received query: '{req.query}'")
    
    try:
        # Validate input
        if not req.query or len(req.query.strip()) == 0:
            logger.warning("Empty query received")
            return {"error": "Query cannot be empty"}
        
        if len(req.query) > 1000:
            logger.warning(f"Query too long: {len(req.query)} characters")
            return {"error": "Query is too long. Please limit to 1000 characters."}
        
        # Process query
        logger.info("Starting query processing...")
        answer = answer_query(req.query.strip())
        
        logger.info(f"Query processed successfully. Answer length: {len(answer) if answer else 0}")
        return {"answer": answer, "status": "success"}
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "error": f"An error occurred while processing your query: {str(e)}", 
            "status": "error",
            "query": req.query
        }

@app.get("/")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "message": "AI API is running"}

@app.get("/debug")
def debug_info():
    """Debug endpoint to check system status"""
    logger.info("Debug info requested")
    
    try:
        # Test imports
        import google.generativeai as genai
        import sentence_transformers
        from qdrant_client import QdrantClient
        from serpapi import GoogleSearch
        
        debug_data = {
            "status": "ok",
            "imports": {
                "google.generativeai": "✓",
                "sentence_transformers": "✓", 
                "qdrant_client": "✓",
                "serpapi": "✓"
            },
            "config": {
                "gemini_api_key_set": bool(getattr(__import__('config'), 'GEMINI_API_KEY', None)),
                "serpapi_key_set": bool(getattr(__import__('config'), 'SERPAPI_API_KEY', None)),
                "qdrant_url_set": bool(getattr(__import__('config'), 'QDRANT_URL', None)),
                "qdrant_api_key_set": bool(getattr(__import__('config'), 'QDRANT_API_KEY', None))
            }
        }
        
        return debug_data
        
    except Exception as e:
        logger.error(f"Debug check failed: {e}")
        return {"status": "error", "error": str(e)}
