from app.core.config import get_settings
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from typing import List
from ..core.models import AIArtNews, Newsletter, ArtistContext
import os
from datetime import datetime
from ..core.config import get_settings

settings = get_settings()

class EditorAgent:
    def __init__(self):
        
        model = OpenAIModel('gpt-4o', api_key=settings.OPENAI_API_KEY)
        self.agent = Agent(model)
    
    async def create_newsletter(
        self,
        news_items: List[AIArtNews],
        artist_contexts: List[ArtistContext]
    ) -> Newsletter:
        """Create a well-structured newsletter from collected content."""
        if not news_items:
            return Newsletter(
                date=datetime.now(),
                headline="No news items available for today's newsletter.",
                introduction="",
                news_items=[],
                artist_insights=[],
                conclusion=""
            )
            
        # Prepare news items for the newsletter
        news_content = "\n\n".join([
            f"Title: {item.title}\n"
            f"Summary: {item.summary}\n"
            f"Context: {item.context}\n"
            f"URL: {item.url}"
            for item in news_items
        ])
        
        prompt = f"""
        Create a professional newsletter about AI art using these news items:
        
        {news_content}
        
        Requirements:
        1. Write an engaging introduction highlighting key themes
        2. Organize news items logically with smooth transitions
        3. Add relevant commentary and insights
        4. Include a conclusion with future outlook
        5. Format in Markdown for easy reading
        
        Make it informative yet engaging for artists and AI enthusiasts.
        """
        
        result = await self.agent.run(prompt)
        
        # Create newsletter
        newsletter = Newsletter(
            date=datetime.now(),
            headline=result.data.splitlines()[0],
            introduction=result.data,
            news_items=news_items,
            artist_insights=artist_contexts,
            conclusion=""
        )
        
        # Save to file
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(
            settings.OUTPUT_DIR,
            f"newsletter_{newsletter.date.strftime('%Y%m%d')}.md"
        )
        
        with open(output_path, "w") as f:
            f.write(newsletter.to_markdown())
        
        return newsletter
