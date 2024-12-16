from datetime import datetime
from typing import List
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from ..core.models import AIArtNews, NewsItem
from ..core.config import get_settings
from ..services.brave_service import search_news

settings = get_settings()

class NewsCollectorAgent:
    def __init__(self):
        model = OpenAIModel('gpt-4o', api_key=settings.OPENAI_API_KEY)
        self.agent = Agent(model)
    
    async def collect_news(self, days: int = 1, limit: int = 5) -> List[AIArtNews]:
        """Collect a limited number of news items and process AI art news from the past given days."""
        # Search for news using Brave API
        raw_news = await search_news("AI art", days=days, limit=limit)
        
        if not raw_news:
            return []
        
        processed_news = []
        for news in raw_news:
            # Use the agent to analyze and summarize each news item
            prompt = f"""
            Analyze this AI art news article:
            Title: {news.title}
            URL: {news.url}
            Content: {news.snippet}

            Analyze the article focusing on:
            - Specific AI artworks created and their concepts
            - Artist names and their approaches to using AI
            - Exhibition venues, residencies, or competitions
            - Creative applications of AI tools/techniques
            - Cultural impact and artistic significance

            Create a concise summary highlighting these artistic and curatorial developments.
            Rate the article's relevance for curators and AI artists on a scale of 0.0 to 1.0.

            Format response as:
            Artwork & Artists: [details of specific works and creators]
            Venue/Context: [exhibition/residency/competition details]
            AI Integration: [how AI was used creatively]
            Relevance Score: [score]
            """
            
            result = await self.agent.run(prompt)
            response_lines = result.data.split('\n')
            
            summary = ""
            relevance = 1.0
            
            for line in response_lines:
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
