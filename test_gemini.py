"""
Test script to debug Gemini API issues
"""

import google.generativeai as genai
from config import GEMINI_API_KEY
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def test_gemini_simple():
    """Test Gemini with a simple prompt"""
    logger.info("Testing Gemini with simple prompt...")
    
    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        
        # Simple test
        simple_prompt = "What is 2+2?"
        logger.info(f"Simple prompt: {simple_prompt}")
        
        response = model.generate_content(simple_prompt)
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Response dir: {[attr for attr in dir(response) if not attr.startswith('_')]}")
        
        if hasattr(response, 'candidates'):
            logger.info(f"Candidates count: {len(response.candidates)}")
            for i, candidate in enumerate(response.candidates):
                logger.info(f"Candidate {i} finish_reason: {candidate.finish_reason}")
                logger.info(f"Candidate {i} content: {candidate.content}")
                if hasattr(candidate.content, 'parts'):
                    logger.info(f"Candidate {i} parts count: {len(candidate.content.parts)}")
                    for j, part in enumerate(candidate.content.parts):
                        logger.info(f"Part {j}: {part}")
        
        try:
            text = response.text
            logger.info(f"Successfully got text: {text}")
            return text
        except Exception as text_error:
            logger.error(f"Error accessing response.text: {text_error}")
            return None
            
    except Exception as e:
        logger.error(f"Error in simple test: {e}")
        return None

def test_gemini_with_safety_settings():
    """Test Gemini with adjusted safety settings"""
    logger.info("Testing Gemini with safety settings...")
    
    try:
        # Try with more permissive safety settings
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
        
        model = genai.GenerativeModel(
            "gemini-2.5-pro",
            safety_settings=safety_settings
        )
        
        test_prompt = """Based on the following information about Facebook advertising, provide a helpful response:

Context: Facebook Ads targeting options include demographic targeting (age, gender, location, language), interest targeting based on user behavior and preferences, custom audiences from customer lists or website visitors, lookalike audiences based on existing customers, and behavioral targeting including purchase history and device usage patterns.

Question: What are the main targeting options in Facebook Ads?

Answer:"""
        
        logger.info("Sending test prompt with safety settings...")
        response = model.generate_content(test_prompt)
        
        try:
            text = response.text
            logger.info(f"Successfully got text with safety settings: {text}")
            return text
        except Exception as text_error:
            logger.error(f"Error accessing response.text with safety settings: {text_error}")
            
            # Try to extract text manually
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                logger.info(f"Manually extracted text: {part.text}")
                                return part.text
            
            return None
            
    except Exception as e:
        logger.error(f"Error in safety settings test: {e}")
        return None

def test_different_model():
    """Test with a different Gemini model"""
    logger.info("Testing different Gemini model...")
    
    try:
        # Try gemini-pro instead of gemini-2.5-pro
        model = genai.GenerativeModel("gemini-pro")
        
        simple_prompt = "Explain Facebook advertising targeting in one paragraph."
        logger.info(f"Testing with gemini-pro model...")
        
        response = model.generate_content(simple_prompt)
        
        try:
            text = response.text
            logger.info(f"Successfully got text from gemini-pro: {text}")
            return text
        except Exception as text_error:
            logger.error(f"Error accessing response.text from gemini-pro: {text_error}")
            return None
            
    except Exception as e:
        logger.error(f"Error testing gemini-pro: {e}")
        return None

def test_with_generation_config():
    """Test with specific generation configuration"""
    logger.info("Testing with generation config...")
    
    try:
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        model = genai.GenerativeModel(
            "gemini-pro",
            generation_config=generation_config
        )
        
        prompt = "What are Facebook ad targeting options? Keep response under 200 words."
        
        response = model.generate_content(prompt)
        
        try:
            text = response.text
            logger.info(f"Successfully got text with config: {text}")
            return text
        except Exception as text_error:
            logger.error(f"Error accessing response.text with config: {text_error}")
            return None
            
    except Exception as e:
        logger.error(f"Error testing with config: {e}")
        return None

if __name__ == "__main__":
    print("=== Gemini API Debug Test ===")
    
    # Test 1: Simple prompt
    print("\n1. Testing simple prompt...")
    result1 = test_gemini_simple()
    if result1:
        print("✓ Simple test passed")
    else:
        print("✗ Simple test failed")
    
    # Test 2: Safety settings
    print("\n2. Testing with safety settings...")
    result2 = test_gemini_with_safety_settings()
    if result2:
        print("✓ Safety settings test passed")
    else:
        print("✗ Safety settings test failed")
    
    # Test 3: Different model
    print("\n3. Testing different model...")
    result3 = test_different_model()
    if result3:
        print("✓ Different model test passed")
    else:
        print("✗ Different model test failed")
    
    # Test 4: Generation config
    print("\n4. Testing with generation config...")
    result4 = test_with_generation_config()
    if result4:
        print("✓ Generation config test passed")
    else:
        print("✗ Generation config test failed")
    
    print("\n=== Test Summary ===")
    tests = [result1, result2, result3, result4]
    passed = sum(1 for test in tests if test)
    print(f"Passed: {passed}/4 tests")
    
    if passed == 0:
        print("All tests failed - there may be an issue with your Gemini API key or the service")
    elif passed < 4:
        print("Some tests passed - we can use a working configuration")
    else:
        print("All tests passed - the issue may be with specific prompts or context length")
