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

# Configure safety settings to be more permissive
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH", 
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]

model = genai.GenerativeModel("gemini-2.5-pro", safety_settings=safety_settings)

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
        logger.info("Step 3: Building context for Gemini...")
        all_context = serp_results + doc_context
        
        # Limit context length to avoid token limits
        context_parts = []
        total_length = 0
        max_context_length = 4000  # Conservative limit
        
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
        
        # Build a more structured prompt
        prompt = f"""You are a helpful AI assistant specializing in digital marketing and Facebook advertising.

Based on the following context information, provide a clear and helpful answer to the user's question.

CONTEXT:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
- Provide a comprehensive but concise answer
- Use information from the context when relevant
- If the context doesn't fully answer the question, acknowledge that
- Keep your response professional and helpful

ANSWER:"""
        
        logger.info(f"Prompt length: {len(prompt)} characters")
        
        # 4. Generate response with error handling
        logger.info("Step 4: Generating Gemini response...")
        
        try:
            response = model.generate_content(prompt)
            logger.info("Gemini response generated successfully")
            
            # Debug response
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                logger.info(f"Response finish_reason: {candidate.finish_reason}")
                
                # finish_reason values: 1=STOP, 2=MAX_TOKENS, 3=SAFETY, 4=RECITATION, 5=OTHER
                if candidate.finish_reason == 3:  # SAFETY
                    logger.warning("Response blocked by safety filters")
                    return "I apologize, but I cannot provide a response to this query due to safety considerations. Please try rephrasing your question."
                elif candidate.finish_reason == 2:  # MAX_TOKENS
                    logger.warning("Response truncated due to token limit")
                elif candidate.finish_reason != 1:  # Not STOP
                    logger.warning(f"Unexpected finish_reason: {candidate.finish_reason}")
            
            # Extract response text
            if hasattr(response, 'text') and response.text:
                logger.info(f"Response text length: {len(response.text)} characters")
                return response.text
            else:
                # Try to extract from candidates manually
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    logger.info("Extracted text from candidate parts")
                                    return part.text
                
                logger.error("No valid text found in response")
                return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
                
        except Exception as gemini_error:
            logger.error(f"Gemini API error: {str(gemini_error)}")
            
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
