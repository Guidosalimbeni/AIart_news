from datetime import datetime
from typing import List
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from ..core.models import AIArtistNews
from ..core.config import get_settings
from ..services.brave_service import search_news

settings = get_settings()

class ArtistNewsCollectorAgent:
    def __init__(self):
        model = AnthropicModel('claude-3-5-sonnet-latest', api_key=settings.ANTHROPIC_API_KEY)
        self.agent = Agent(model)
    
    async def collect_news(self, artist: str, days: int = 3, limit: int = 5) -> List[AIArtistNews]:
        """Collect a limited number of news items of a specific artist and process AI art news from the past given days."""
        # Search for news using Brave API
        raw_news = await search_news(f"{artist} AI artist", days=days, limit=limit)
        
        if not raw_news:
            return []
        
        processed_news = []
        for news in raw_news:
            prompt = f"""
            Analyze this AI art news about the artist {artist}:
            Title: {news.title}
            URL: {news.url}
            Content: {news.snippet}

            Analyze the news focusing on, if available, on
            - only if available, any specific AI artworks created and their concepts
            - Artist name
            - the news content itself
            - the date of the news
            
            Create a summary highlighting the artistic and curatorial developments.
            
            Format response as:
            Summary: [your summary including the artist name {artist}]
            
            """
            
            result = await self.agent.run(prompt)
            
            # Parse the response
            lines = result.data.split('\n')
            summary = ""
            
            for line in lines:
                if line.startswith("Summary:"):
                    summary = line.replace("Summary:", "").strip()
                
            
            processed_news.append(
                AIArtistNews(
                    title=news.title,
                    url=news.url,
                    summary=summary,
                    
                )
            )
        
        
        return processed_news
