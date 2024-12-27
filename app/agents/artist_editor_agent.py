from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from typing import List
from ..agents.artists_agent import ArtistNewsCollectorAgent
import os
from ..core.config import get_settings

settings = get_settings()

class ArtistEditorAgent:
    def __init__(self):
        model = AnthropicModel('claude-3-5-sonnet-latest', api_key=settings.ANTHROPIC_API_KEY)
        self.agent = Agent(model)
        self.artistAgent = ArtistNewsCollectorAgent()
        
     
    async def create_newsletter(self, artists: list) -> str:
        """Create a informative newsletter including the news of each artist."""
        
        collection = []
        for artist in artists:
            info = await self.artistAgent.collect_news(artist, 3, 1)
            collection.extend(info)  # Use extend instead of append to flatten the list

        # Create the joined string with better markdown formatting
        artists_news = "\n\n".join([
            f"## {item.title}\n\n"
            f"{item.summary}\n\n"
            f"[Read more]({item.url})"
            for item in collection
            if item.summary.strip()  # Skip items with empty summaries
        ])
        
        prompt = f"""
        Create an AI art newsletter using this content. Follow these requirements:
        
        - Use clean markdown formatting with proper spacing
        - Use level-1 heading (# ) for the newsletter title
        - Use level-2 headings (## ) for artist names
        - Include dates in italics when available
        - Make all links clickable
        - Organize content by artist, removing any duplicate information
        - Use proper paragraph spacing (double line breaks between sections)
        - Do not include any conclusions or final messages
        
        Content:
        {artists_news}
        """
        
        response = await self.agent.run(prompt)
        
        # Extract just the newsletter content from the response
        # If response.data is a string, use it directly. If it's an object, access its content
        newsletter_content = response.data if isinstance(response.data, str) else response.data.content
        
        # Add proper spacing and cleanup any formatting issues
        newsletter_content = (
            "# AI Artists News\n\n" +  # Ensure consistent title
            newsletter_content.split("# AI Artists News\n\n")[-1]  # Remove any duplicate titles
            .replace("\n\n\n", "\n\n")  # Fix excessive spacing
            .strip()  # Remove trailing whitespace
        )

        return newsletter_content
