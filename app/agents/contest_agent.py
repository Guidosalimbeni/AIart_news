from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from typing import List
from ..core.models import ArtistContest
from ..services.brave_service import search_content
from ..core.config import get_settings

settings = get_settings()

class ContestAgent:
    def __init__(self):
        model = AnthropicModel('claude-3-5-sonnet-latest', api_key=settings.ANTHROPIC_API_KEY)
        self.agent = Agent(model)
    
    async def gather_context(self) -> List[ArtistContest]:
        """Gather information about current AI art contests and exhibitions."""
        print("\nDebug: Starting contest search...")
        
        # Search for contests and exhibitions
        contests = await search_content(
            query="AI art exhibition contest competition",
            limit=5
        )
        
        print(f"Debug: Found {len(contests)} contests")
        
        if not contests:
            print("Warning: No contest or exhibition information found")
            return []
        
        enhanced_contests = []
        for contest in contests:
            print(f"\nDebug: Processing contest: {contest.title}")
            
            prompt = f"""
            Analyze this AI art opportunity:
            Title: {contest.title}
            Content: {contest.insight}
            
            Extract and summarize the key information and format the information in a clear, concise way that can be helpful for AI artists and curators.
            """
            
            result = await self.agent.run(prompt)
            print(f"Debug: Got enhanced description")
            
            # Update the contest with enhanced insight
            contest.insight = result.data
            enhanced_contests.append(contest)
        
        # Sort by relevance
        sorted_contests = sorted(enhanced_contests, key=lambda x: x.relevance, reverse=True)
        print(f"\nDebug: Returning {len(sorted_contests)} enhanced contests")
        return sorted_contests
