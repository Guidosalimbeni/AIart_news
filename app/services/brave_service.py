from typing import List
import httpx
from datetime import datetime, timedelta
from ..core.config import get_settings
from ..core.models import NewsItem, ArtistContest

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
            print(f"Debug: News API response status: {response.status_code}")
            
            return [
                NewsItem(
                    title=item["title"],
                    url=item["url"],
                    snippet=item.get("description", "")
                )
                for item in data.get("results", [])[:limit]
            ]
    except Exception as e:
        print(f"Error searching news: {str(e)}")
        return []

async def search_content(query: str = "AI art exhibitions and contests", limit: int = 5) -> List[ArtistContest]:
    """
    Search for AI art contests and exhibitions using Brave API
    Returns: List of ArtistContest objects
    """
    base_url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": settings.BRAVE_API_KEY
    }
    
    print(f"Debug: Searching content with query: {query}")
    
    params = {
        "q": f"{query} current exhibition contest call for artists deadline",
        "text_format": "raw",
        "search_lang": "en",
        "count": limit * 2,  # Request more results to filter
        "freshness": "p90d"  # Look back 90 days
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
            print(f"Debug: Content API response status: {response.status_code}")
            print(f"Debug: Raw results count: {len(data.get('results', []))}")
            
            # Filter and convert results directly to ArtistContest objects
            results = []
            keywords = ["exhibition", "contest", "competition", "call for", "submission", "deadline", "artists"]
            
            for item in data.get("results", []):
                title = item["title"].lower()
                description = item.get("description", "").lower()
                
                # Check if the result contains relevant keywords
                if any(keyword in title or keyword in description for keyword in keywords):
                    # Create ArtistContest object directly
                    contest = ArtistContest(
                        title=item["title"],
                        insight=item.get("description", "") or title,  # Use description or fallback to title
                        relevance=1.0 if any(k in title for k in keywords) else 0.7,  # Higher relevance if keyword in title
                        source_url=item["url"]
                    )
                    results.append(contest)
                    print(f"Debug: Found relevant contest: {item['title']}")
                
                if len(results) >= limit:
                    break
            
            print(f"Debug: Filtered contests count: {len(results)}")
            return results[:limit]
            
    except Exception as e:
        print(f"Error searching content: {str(e)}\nHeaders: {headers}\nParams: {params}")
        return []
