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

async def search_content(query: str = "AI art", limit: int = 5) -> List[ArtistContest]:
    """
    Search for AI art content using Brave API
    Returns: List of ArtistContest objects
    """
    base_url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": settings.BRAVE_API_KEY
    }
    
    print(f"\nDebug: Starting Brave API search")
    print(f"Debug: Query: {query}")
    
    params = {
        "q": query,
        "search_lang": "en",
        "count": 10  # Request more results initially
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print("Debug: Sending request to Brave API...")
            response = await client.get(
                base_url,
                headers=headers,
                params=params,
                timeout=100.0
            )
            
            print(f"Debug: Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Debug: Error response body: {response.text}")
                return []
                
            try:
                data = response.json()
                web_results = data.get('web', {}).get('results', [])
                print(f"Debug: Found {len(web_results)} web results")
                
                results = []
                for item in web_results[:limit]:
                    try:
                        contest = ArtistContest(
                            title=item.get('title', 'Untitled'),
                            insight=item.get('description', '') or item.get('title', ''),
                            relevance=0.8,  # Default relevance
                            source_url=item.get('url', '')
                        )
                        results.append(contest)
                        print(f"Debug: Added result: {contest.title}")
                    except Exception as e:
                        print(f"Debug: Error creating contest object: {str(e)}")
                        continue
                
                return results
                
            except json.JSONDecodeError as e:
                print(f"Debug: JSON decode error: {str(e)}")
                print(f"Debug: Raw response: {response.text[:500]}...")
                return []
                
    except Exception as e:
        print(f"Debug: Request error: {str(e)}")
        return []
