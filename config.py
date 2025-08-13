import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env file

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
PRIORITY_LINKS = [
    "https://en-gb.facebook.com/business/help/621956575422138?id=649869995454285",
    "https://www.eachspy.com/facebook-ads-interests/",
    "https://www.clickguard.com/blog/meta-ads-campaign-types/",
    "https://twowheelsmarketing.com/blog/facebook-ads-targeting-options-list/",
    "https://transparency.meta.com/policies/ad-standards/",
    "https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group"
    # Add prioritized site(s)
]
