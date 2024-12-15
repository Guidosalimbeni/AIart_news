from typing import List
from pydantic_ai import Agent
from ..core.models import ArtistContext
from ..services.brave_service import search_content
from ..core.config import get_settings

settings = get_settings()

class ContextAgent:
    def __init__(self):
        self.agent = Agent(
            'anthropic:claude-3-opus-20240229',
            system_prompt="""You are an AI art context analyst. Your task is to:
            1. Analyze discussions, tutorials, and resources about AI art
            2. Extract valuable insights for artists
            3. Identify emerging trends and opportunities
            4. Present information in a way that's actionable for artists
            Focus on practical insights that can help artists leverage AI tools effectively.
            """
        )
    
    async def gather_context(self) -> List[ArtistContext]:
        """Gather and analyze context about AI art for artists."""
        # Search for relevant content using Brave API
        raw_content = await search_content(
            query="AI art tools tutorials guides artists workflow",
            max_results=settings.MAX_SEARCH_RESULTS
        )
        
        contexts = []
        for content in raw_content:
            # Use the agent to analyze and extract insights
            result = await self.agent.arun(
                f"""Analyze this AI art resource:
                Title: {content.title}
                Content: {content.snippet}
                
                Extract key insights and practical advice that would be valuable 
                for artists working with AI tools. Focus on actionable information."""
            )
            
            contexts.append(
                ArtistContext(
                    topic=content.title,
                    insights=result.data,
                    relevance=content.score,
                    source=content.url
                )
            )
        
        # Sort by relevance and return top insights
        return sorted(
            contexts,
            key=lambda x: x.relevance,
            reverse=True
        )
