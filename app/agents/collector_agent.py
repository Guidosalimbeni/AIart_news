from datetime import datetime, timedelta
from typing import List
from pydantic_ai import Agent
from ..core.models import AIArtNews
from ..core.config import get_settings
from ..services.brave_service import search_news

settings = get_settings()

class NewsCollectorAgent:
    def __init__(self):
        self.agent = Agent(
            'anthropic:claude-3-opus-20240229',
            system_prompt="""You are an AI art news curator. Your task is to:
            1. Analyze news articles about AI art
            2. Extract key information and summarize it concisely
            3. Rate the relevance of each article
            4. Ensure summaries are informative and engaging
            Focus on significant developments, trends, and impactful stories in the AI art space.
            """
        )
    
    async def collect_news(self) -> List[AIArtNews]:
        """Collect and process AI art news from the past day."""
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=settings.DAYS_LOOKBACK)
        
        # Search for news using Brave API
        raw_news = await search_news(
            query="AI art artificial intelligence generative art",
            start_date=start_date,
            end_date=end_date,
            max_results=settings.MAX_SEARCH_RESULTS
        )
        
        processed_news = []
        for news in raw_news:
            # Use the agent to analyze and summarize each news item
            result = await self.agent.arun(
                f"""Analyze this AI art news article:
                Title: {news.title}
                URL: {news.url}
                Content: {news.snippet}
                
                Create a concise, informative summary focusing on the key developments 
                and implications for the AI art community."""
            )
            
            processed_news.append(
                AIArtNews(
                    title=news.title,
                    url=news.url,
                    date=news.published_date,
                    summary=result.data,
                    source=news.source,
                    relevance_score=news.score
                )
            )
        
        # Sort by relevance and return top results
        return sorted(
            processed_news,
            key=lambda x: x.relevance_score,
            reverse=True
        )
