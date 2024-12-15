from datetime import datetime
from typing import List
from pydantic_ai import Agent
from ..core.models import Newsletter, AIArtNews, ArtistContext
import os
from ..core.config import get_settings

settings = get_settings()

class EditorAgent:
    def __init__(self):
        self.agent = Agent(
            'anthropic:claude-3-opus-20240229',
            system_prompt="""You are an AI art newsletter editor. Your task is to:
            1. Create engaging headlines that capture the day's key developments
            2. Write clear, concise introductions that set the context
            3. Organize news and insights in a logical flow
            4. Conclude with meaningful takeaways
            Focus on creating a cohesive narrative that provides value to readers interested in AI art.
            """
        )
    
    async def create_newsletter(
        self,
        news_items: List[AIArtNews],
        artist_contexts: List[ArtistContext]
    ) -> Newsletter:
        """Create a well-structured newsletter from collected content."""
        # Generate headline and introduction
        content_summary = "\n".join([
            f"- {news.title}: {news.summary[:100]}..."
            for news in news_items[:3]
        ])
        
        intro_result = await self.agent.arun(
            f"""Based on these top news items:
            {content_summary}
            
            Create an engaging headline and brief introduction for today's AI art newsletter.
            Format as JSON with 'headline' and 'introduction' fields."""
        )
        
        # Generate conclusion
        conclusion_result = await self.agent.arun(
            """Based on the news and insights collected, provide a brief conclusion 
            that ties everything together and offers perspective on the current 
            state of AI art."""
        )
        
        # Create newsletter
        newsletter = Newsletter(
            date=datetime.now(),
            headline=intro_result.data["headline"],
            introduction=intro_result.data["introduction"],
            news_items=news_items,
            artist_insights=artist_contexts,
            conclusion=conclusion_result.data
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
