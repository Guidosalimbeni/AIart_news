from datetime import datetime
from typing import List
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from ..core.models import AIArtNews, NewsItem
from ..core.config import get_settings
from ..services.brave_service import search_news

settings = get_settings()

class NewsCollectorAgent:
    def __init__(self):
        model = AnthropicModel('claude-3-5-sonnet-latest', api_key=settings.ANTHROPIC_API_KEY)
        self.agent = Agent(model)
    
    async def collect_news(self, days: int = 1, limit: int = 5) -> List[AIArtNews]:
        """Collect a limited number of news items and process AI art news from the past given days."""
        # Search for news using Brave API
        raw_news = await search_news("AI art", days=days, limit=limit)
        
        if not raw_news:
            return []
        
        processed_news = []
        for news in raw_news:
            prompt = f"""
            Analyze this AI art news:
            Title: {news.title}
            URL: {news.url}
            Content: {news.snippet}

            Analyze the news focusing on, if available, on
            - Specific AI artworks created and their concepts
            - Artist names and their approaches to using AI
            - the news content itself
            

            Create a concise summary highlighting the artistic and curatorial developments.
            
            Format response as:
            Summary: [your summary]
            
            """
            
            result = await self.agent.run(prompt)
            
            # Parse the response
            lines = result.data.split('\n')
            summary = ""
            relevance = 1.0
            
            for line in lines:
                if line.startswith("Summary:"):
                    summary = line.replace("Summary:", "").strip()
                elif line.startswith("Relevance:"):
                    try:
                        relevance = float(line.replace("Relevance:", "").strip())
                    except ValueError:
                        relevance = 1.0
            
            processed_news.append(
                AIArtNews(
                    title=news.title,
                    url=news.url,
                    snippet=news.snippet,
                    summary=summary,
                    relevance=relevance,
                    date=datetime.now()
                )
            )
        
        # Sort by relevance and return
        return sorted(
            processed_news,
            key=lambda x: x.relevance,
            reverse=True
        )
