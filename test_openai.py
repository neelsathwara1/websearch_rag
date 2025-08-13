"""
Test OpenAI API functionality
"""

import openai
from config import OPENAI_API_KEY
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

def test_openai_embeddings():
    """Test OpenAI embeddings API"""
    logger.info("Testing OpenAI embeddings...")
    
    try:
        test_text = "Facebook advertising targeting options"
        
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=test_text
        )
        
        embedding = response.data[0].embedding
        logger.info(f"Successfully generated embedding with {len(embedding)} dimensions")
        return True
        
    except Exception as e:
        logger.error(f"Error testing OpenAI embeddings: {e}")
        return False

def test_openai_chat():
    """Test OpenAI chat completion API"""
    logger.info("Testing OpenAI chat completion...")
    
    try:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant specializing in digital marketing."
            },
            {
                "role": "user",
                "content": "What are the main Facebook ad targeting options? Keep it brief."
            }
        ]
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        logger.info(f"Successfully generated chat response: {answer[:100]}...")
        return True
        
    except Exception as e:
        logger.error(f"Error testing OpenAI chat: {e}")
        return False

if __name__ == "__main__":
    print("=== OpenAI API Test ===")
    
    # Test embeddings
    print("\n1. Testing OpenAI Embeddings API...")
    embeddings_ok = test_openai_embeddings()
    if embeddings_ok:
        print("✓ Embeddings API working")
    else:
        print("✗ Embeddings API failed")
    
    # Test chat completion
    print("\n2. Testing OpenAI Chat Completion API...")
    chat_ok = test_openai_chat()
    if chat_ok:
        print("✓ Chat Completion API working")
    else:
        print("✗ Chat Completion API failed")
    
    print(f"\n=== Results ===")
    if embeddings_ok and chat_ok:
        print("✓ All OpenAI APIs working correctly!")
    else:
        print("✗ Some OpenAI APIs failed. Check your API key and credits.")
