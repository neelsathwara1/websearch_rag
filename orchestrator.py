import openai
from rag_module import retrieve_similar_docs
from search_module import serpapi_search
from config import OPENAI_API_KEY, PRIORITY_LINKS
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

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

def answer_query(query: str, priority_links=PRIORITY_LINKS):
    logger.info(f"Starting query processing for: '{query}'")
    
    try:
        # 1. Web/Priority search
        logger.info("Step 1: Starting SerpAPI search...")
        serp_results = serpapi_search(query, priority_links)
        logger.info(f"SerpAPI search completed. Found {len(serp_results)} results")
        
        # 2. RAG search
        logger.info("Step 2: Starting RAG document retrieval...")
        doc_context = retrieve_similar_docs(query)
        logger.info(f"RAG search completed. Found {len(doc_context)} documents")
        
        # 3. Build context with length limits
        logger.info("Step 3: Building context for OpenAI...")
        all_context = serp_results + doc_context
        
        # Limit context length to avoid token limits (OpenAI has different limits than Gemini)
        context_parts = []
        total_length = 0
        max_context_length = 6000  # Conservative limit for OpenAI
        
        for item in all_context:
            if total_length + len(item) < max_context_length:
                context_parts.append(item)
                total_length += len(item)
            else:
                # Truncate the last item if needed
                remaining = max_context_length - total_length
                if remaining > 100:  # Only add if meaningful length remains
                    context_parts.append(item[:remaining] + "...")
                break
        
        context = "\n\n".join(context_parts)
        
        logger.info(f"Context length: {len(context)} characters from {len(context_parts)} sources")
        
        # 4. Generate response with OpenAI
        logger.info("Step 4: Generating OpenAI response...")
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant specializing in digital marketing and Facebook advertising. Provide clear, comprehensive, and helpful answers based on the context provided."
                },
                {
                    "role": "user",
                    "content": f"""Based on the following context information, provide a clear and helpful answer to my question.

CONTEXT:
{context}

QUESTION: {query}

Please provide a comprehensive but concise answer using the information from the context when relevant. If the context doesn't fully answer the question, acknowledge that and provide what you can."""
                }
            ]
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1500,
                temperature=0.7
            )
            
            logger.info("OpenAI response generated successfully")
            
            answer = response.choices[0].message.content
            logger.info(f"Response length: {len(answer)} characters")
            
            return answer
                
        except Exception as openai_error:
            logger.error(f"OpenAI API error: {str(openai_error)}")
            
            # Fallback response using context
            if context_parts:
                logger.info("Generating fallback response from context")
                fallback = f"Based on the available information:\n\n"
                
                # Include the most relevant context
                for i, part in enumerate(context_parts[:3]):  # Top 3 most relevant
                    fallback += f"{part[:200]}...\n\n"
                
                fallback += f"Please note: The AI service encountered an issue, so this is a basic response from the retrieved information."
                return fallback
            else:
                return "I apologize, but I encountered an error and couldn't retrieve relevant information for your question. Please try again."
    
    except Exception as e:
        logger.error(f"Error in answer_query: {str(e)}")
        raise e
