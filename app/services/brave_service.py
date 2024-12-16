from typing import List
import httpx
from datetime import datetime, timedelta
from ..core.config import get_settings
from ..core.models import NewsItem

settings = get_settings()

async def search_news(query: str = "AI art", days: int = 1, limit: int = 5) -> List[NewsItem]:
    """
    Search for news using Brave API
    """
    base_url = "https://api.search.brave.com/res/v1/news/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": settings.BRAVE_API_KEY
    }
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    params = {
        "q": query,
        "freshness": "p1d" if days == 1 else f"p{days}d",
        "text_format": "raw",
        "search_lang": "en",
        "count": limit
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                base_url,
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            return [
                NewsItem(
                    title=item["title"],
                    url=item["url"],
                    snippet=item["description"]
                )
                for item in data.get("results", [])[:limit]  # Ensure we don't exceed the limit
            ]
    except Exception as e:
        print(f"Error searching news: {str(e)}")
        return []

async def search_content(query: str = "AI art tutorials and resources", limit: int = 5) -> List[NewsItem]:
    """
    Search for general content using Brave API
    """
    base_url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": settings.BRAVE_API_KEY
    }
    
    params = {
        "q": query,
        "text_format": "raw",
        "search_lang": "en",
        "count": limit
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                base_url,
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            return [
                NewsItem(
                    title=item["title"],
                    url=item["url"],
                    snippet=item["description"]
                )
                for item in data.get("results", [])[:limit]  # Ensure we don't exceed the limit
            ]
    except Exception as e:
        print(f"Error searching content: {str(e)}")
        return []
