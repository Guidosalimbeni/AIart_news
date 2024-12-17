from datetime import datetime
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from typing import List
from ..core.models import AIArtNews, Newsletter, ArtistContest
import os
from ..core.config import get_settings

settings = get_settings()

class EditorAgent:
    def __init__(self):
        model = OpenAIModel('gpt-4o', api_key=settings.OPENAI_API_KEY)
        self.agent = Agent(model)
        
        # Static newsletter information
        self.static_info = {
            "website": "https://www.guidosalimbeni.it",
            "subscribe_link": "https://newsletter.yourwebsite.com/subscribe",
            "social_links": {
                "twitter": "https://twitter.com/guidosalimbeni",
                "instagram": "https://instagram.com/guidosalimbeni"
            },
            "footer_text": "Thank you for reading! If you enjoyed this newsletter, please share it with your friends."
        }
     
    async def create_newsletter(
        self,
        news_items: List[AIArtNews],
        artist_contests: List[ArtistContest]
    ) -> Newsletter:
        """Create a well-structured newsletter combining news and contest information."""
        if not news_items:
            raise ValueError("No news items provided")
        
        current_date = datetime.now()
            
        # Format news items into markdown
        news_content = "\n\n".join([
            f"### {item.title}\n"
            f"{item.summary}\n"
            f"[Read more]({item.url})"
            for item in news_items
        ])
        
        # Format contest information into markdown
        contest_content = "\n\n".join([
            f"### {contest.title}\n"
            f"{contest.insight}\n"
            f"[Learn more]({contest.source_url})"
            for contest in artist_contests
        ])
        
        # Generate a one-sentence introduction
        prompt = f"""
        Based on these AI art news items and contests, write ONE engaging sentence 
        that captures the most exciting developments:
        
        News:
        {news_content}
        
        Contests & Exhibitions:
        {contest_content}
        """
        
        intro_result = await self.agent.run(prompt)
        
        # Assemble the newsletter in markdown format
        newsletter_content = f"""
# AI Art News - {current_date.strftime('%B %d, %Y')}

{intro_result.data}

## Latest in AI Art

{news_content}

## Contests & Exhibitions

{contest_content}

---

## Stay Connected
- Visit my website: [{self.static_info['website']}]({self.static_info['website']})
- Follow me on [Twitter]({self.static_info['social_links']['twitter']}) and [Instagram]({self.static_info['social_links']['instagram']})
- [Subscribe]({self.static_info['subscribe_link']}) to receive future newsletters

{self.static_info['footer_text']}
"""
        
        # Create and return the newsletter
        return Newsletter(
            date=current_date,  
            headline=f"AI Art News - {current_date.strftime('%B %d, %Y')}",
            introduction=intro_result.data,
            news_items=news_items,
            artist_insights=artist_contests,
            conclusion=self.static_info['footer_text'],
            content=newsletter_content
        )
