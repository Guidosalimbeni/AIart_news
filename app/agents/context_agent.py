from typing import List
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from ..core.models import ArtistContext, AIArtNews
from ..services.brave_service import search_content
from app.core.config import get_settings

settings = get_settings()

class ContextAgent:
    def __init__(self):
        model = OpenAIModel('gpt-4o', api_key=settings.OPENAI_API_KEY)
        self.agent = Agent(model)
    
    async def gather_context(self) -> List[ArtistContext]:
        """Gather and analyze context about AI art for artists."""
        # Search for relevant content
        raw_content = await search_content(
            query="AI art tools tutorials guides artists workflow",
            limit=settings.MAX_SEARCH_RESULTS
        )
        
        contexts = []
        for content in raw_content:
            # Use the agent to analyze and extract insights
            prompt = f"""
            Analyze this AI art resource:
            Title: {content.title}
            Content: {content.snippet}
            
            Extract key insights and practical tips for artists working with AI.
            Rate the relevance for AI artists on a scale of 0.0 to 1.0.
            
            Format your response as:
            Insight: [your insight]
            Relevance: [score]
            """
            
            result = await self.agent.run(prompt)
            response_lines = result.data.split('\n')
            
            insight = ""
            relevance = 1.0
            
            for line in response_lines:
                if line.startswith("Insight:"):
                    insight = line.replace("Insight:", "").strip()
                elif line.startswith("Relevance:"):
                    try:
                        relevance = float(line.replace("Relevance:", "").strip())
                    except ValueError:
                        relevance = 1.0
            
            contexts.append(
                ArtistContext(
                    topic=content.title,
                    insights=insight,
                    relevance=relevance,
                    source=content.url
                )
            )
        
        # Sort by relevance
        return sorted(
            contexts,
            key=lambda x: x.relevance,
            reverse=True
        )
    
    async def add_context(self, news_items: List[AIArtNews]) -> List[AIArtNews]:
        """Add broader context and connections between different news items."""
        if not news_items:
            return []
            
        # Create a summary of all news items for context
        news_summary = "\n".join([
            f"- {item.title}: {item.summary}"
            for item in news_items
        ])
        
        prompt = f"""
        Here are today's AI art news items:
        {news_summary}
        
        For each news item, provide:
        1. Historical context and background
        2. Connections to other news items
        3. Potential future implications
        4. Relevant industry trends
        
        Format each analysis separately.
        """
        
        result = await self.agent.run(prompt)
        
        # Parse and add context to each news item
        context_blocks = result.data.split("\n\n")
        for item, context in zip(news_items, context_blocks):
            item.context = context.strip()
        
        return news_items
