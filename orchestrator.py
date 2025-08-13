import google.generativeai as genai
from rag_module import retrieve_similar_docs
from search_module import serpapi_search
from config import GEMINI_API_KEY, PRIORITY_LINKS
import logging
import json

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

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro")

def answer_query(query: str, priority_links=PRIORITY_LINKS):
    logger.info(f"Starting query processing for: '{query}'")
    
    try:
        # 1. Web/Priority search
        logger.info("Step 1: Starting SerpAPI search...")
        serp_results = serpapi_search(query, priority_links)
        logger.info(f"SerpAPI search completed. Found {len(serp_results)} results")
        logger.debug(f"SerpAPI results: {serp_results[:2] if serp_results else 'No results'}")
        
        # 2. RAG search
        logger.info("Step 2: Starting RAG document retrieval...")
        doc_context = retrieve_similar_docs(query)
        logger.info(f"RAG search completed. Found {len(doc_context)} documents")
        logger.debug(f"RAG results: {doc_context[:1] if doc_context else 'No results'}")
        
        # 3. Build context
        logger.info("Step 3: Building context for Gemini...")
        all_context = serp_results + doc_context
        context = "\n".join(all_context)
        
        logger.info(f"Total context length: {len(context)} characters")
        logger.info(f"Total sources: {len(all_context)} (SerpAPI: {len(serp_results)}, RAG: {len(doc_context)})")
        
        # Build prompt with safety considerations
        prompt = (
            f"Based on the following information, provide a helpful and accurate answer to the user's question. "
            f"If the information is insufficient, acknowledge that and provide what you can.\n\n"
            f"Context:\n{context}\n\n"
            f"User question: {query}\n\n"
            f"Answer:"
        )
        
        logger.info(f"Prompt length: {len(prompt)} characters")
        logger.debug(f"Full prompt: {prompt[:500]}...")
        
        # 4. Generate response with error handling
        logger.info("Step 4: Generating Gemini response...")
        
        try:
            response = model.generate_content(prompt)
            logger.info("Gemini response generated successfully")
            
            # Debug response object
            logger.debug(f"Response object type: {type(response)}")
            logger.debug(f"Response candidates: {len(response.candidates) if hasattr(response, 'candidates') else 'No candidates attr'}")
            
            if hasattr(response, 'candidates') and response.candidates:
                for i, candidate in enumerate(response.candidates):
                    logger.debug(f"Candidate {i}: finish_reason={candidate.finish_reason}")
                    if hasattr(candidate, 'content') and candidate.content:
                        logger.debug(f"Candidate {i} has content with {len(candidate.content.parts)} parts")
            
            # Check if response has valid content
            if hasattr(response, 'text') and response.text:
                logger.info(f"Response text length: {len(response.text)} characters")
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                # Try to extract text from candidates
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                logger.info("Extracted text from candidate parts")
                                return part.text
                
                logger.error("No valid text found in response candidates")
                return "I apologize, but I couldn't generate a proper response. The AI model didn't return valid content. Please try rephrasing your question."
            else:
                logger.error("Response has no candidates or text attribute")
                return "I apologize, but I couldn't generate a response. Please try again with a different question."
                
        except Exception as gemini_error:
            logger.error(f"Gemini API error: {str(gemini_error)}")
            logger.error(f"Error type: {type(gemini_error)}")
            
            # Fallback response using context
            if all_context:
                logger.info("Generating fallback response from context")
                return f"Based on the available information:\n\n{context[:500]}...\n\nPlease note: The AI service encountered an issue, so this is a basic response from the retrieved information."
            else:
                return "I apologize, but I encountered an error and couldn't retrieve relevant information for your question. Please try again."
    
    except Exception as e:
        logger.error(f"Error in answer_query: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise e
