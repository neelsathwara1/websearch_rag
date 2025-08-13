from serpapi import GoogleSearch
from config import SERPAPI_API_KEY, PRIORITY_LINKS
import logging

# Configure logging
logger = logging.getLogger(__name__)

def serpapi_search(query, priority_links=[]):
    logger.info(f"Starting SerpAPI search for query: '{query}'")
    logger.info(f"Priority links: {priority_links}")
    
    results = []
    
    try:
        # Search priority sites first
        for i, site in enumerate(priority_links):
            logger.debug(f"Searching priority site {i+1}/{len(priority_links)}: {site}")
            
            try:
                search = GoogleSearch({
                    "q": f"site:{site} {query}",
                    "api_key": SERPAPI_API_KEY
                })
                data = search.get_dict()
                
                organic_results = data.get("organic_results", [])
                logger.debug(f"Found {len(organic_results)} results from {site}")
                
                snippets = [item.get("snippet", "") for item in organic_results if item.get("snippet")]
                results.extend(snippets)
                logger.debug(f"Added {len(snippets)} snippets from {site}")
                
            except Exception as site_error:
                logger.warning(f"Error searching site {site}: {site_error}")
                continue
        
        logger.info(f"Priority search completed. Found {len(results)} results from priority sites")
        
        # Fallback to generic search if nothing found
        if not results:
            logger.info("No results from priority sites, performing generic search...")
            
            try:
                search = GoogleSearch({
                    "q": query, 
                    "api_key": SERPAPI_API_KEY,
                    "num": 5  # Limit results
                })
                data = search.get_dict()
                
                organic_results = data.get("organic_results", [])
                logger.info(f"Generic search found {len(organic_results)} results")
                
                snippets = [item.get("snippet", "") for item in organic_results if item.get("snippet")]
                results.extend(snippets)
                logger.info(f"Added {len(snippets)} snippets from generic search")
                
            except Exception as generic_error:
                logger.error(f"Error in generic search: {generic_error}")
        
        # Filter and clean results
        cleaned_results = []
        for result in results:
            if result and len(result.strip()) > 10:  # Filter out very short snippets
                cleaned_results.append(result.strip())
        
        logger.info(f"SerpAPI search completed. Returning {len(cleaned_results)} cleaned results")
        return cleaned_results
        
    except Exception as e:
        logger.error(f"Error in serpapi_search: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        # Return empty list instead of raising to prevent complete failure
        return []
