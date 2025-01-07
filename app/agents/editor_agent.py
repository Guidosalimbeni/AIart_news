from datetime import datetime
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from typing import List
from ..core.models import AIArtNews, Newsletter, ArtistContest
import os
from ..core.config import get_settings

settings = get_settings()

class EditorAgent:
    def __init__(self):
        model = AnthropicModel('claude-3-5-sonnet-latest', api_key=settings.ANTHROPIC_API_KEY)
        self.agent = Agent(model)
        
        # Static newsletter information
        self.static_info = {
            "website": "https://www.guidosalimbeni.it",
            "subscribe_link": "https://www.guidosalimbeni.it/blog.html",
            "social_links": {
                "twitter": "https://twitter.com/guidosalimbeni",
                "instagram": "https://instagram.com/guidosalimbeni"
            },
            "footer_text": "Thank you for reading! If you enjoyed this newsletter, please share it with your friends."
        }
     
    async def create_newsletter(
        self,
        news_items: List[AIArtNews],
        artist_contests: List[ArtistContest],
        linkedin_posts: List[dict],
        sub_newsletter_artists:str,
        result_x_news:str,
        result_linkedin_news:str,
        subPreprints_newsletter: str
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

        # Format LinkedIn posts into markdown
        linkedin_content = "\n\n".join([
            f"### {post['title']}\n"
            f"{post['analysis']}\n"
            f"[Read more]({post['url']})"
            for post in linkedin_posts
        ])
        
        # Generate newsletter
        prompt = f"""
        Based on the following information, write an extensive AI art newsletter,
        avoid repeated information when there is duplicated content,
        include dates when available
        include link and make them cliccable
        avoid any conclusion or final massage in the generated newsletter
        use a markdown style
        :

        Newsletter Date: {current_date.strftime('%B %d, %Y')}
        
        News:
        {news_content}
        
        Contests & Exhibitions:
        {contest_content}

        LinkedIn Posts:
        {linkedin_content}
        """
        
        newsletter_prompted = await self.agent.run(prompt)
        
        # Assemble the newsletter in markdown format
        newsletter_content = f"""
# AI Art News - {current_date.strftime('%B %d, %Y')}


{newsletter_prompted.data}


{sub_newsletter_artists}

{result_x_news}

{result_linkedin_news}

{subPreprints_newsletter}

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
            
            news_items=news_items,
            artist_insights=artist_contests,
            conclusion=self.static_info['footer_text'],
            content=newsletter_content
        )
