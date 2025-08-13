"""
Test the OpenAI RAG API directly
"""

from orchestrator import answer_query
import logging

# Configure logging to see debug info
logging.basicConfig(level=logging.INFO)

def test_query(query):
    print(f"\n=== Testing Query: '{query}' ===")
    
    try:
        result = answer_query(query)
        print(f"SUCCESS!")
        print(f"Response length: {len(result)} characters")
        print(f"Response: {result}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=== OpenAI RAG System Test ===")
    
    # Test queries
    test_queries = [
        "What are Facebook ad targeting options?",
        "How does Meta Business Manager work?",
        "What are the different Facebook campaign objectives?"
    ]
    
    passed = 0
    for query in test_queries:
        if test_query(query):
            passed += 1
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{len(test_queries)} tests")
    
    if passed == len(test_queries):
        print("🎉 All tests passed! OpenAI RAG system is working perfectly!")
    else:
        print("⚠️ Some tests failed. Check the logs above.")
