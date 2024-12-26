from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from typing import List, Dict
from ..services.brightdata_service import get_recent_posts, getsnapshot
from ..core.config import get_settings
import json
import time


    
    
    

class LinkedInCollector:
    def __init__(self, dataset_id):
        self.settings = get_settings()
        model = AnthropicModel('claude-3-5-sonnet-latest', api_key=self.settings.ANTHROPIC_API_KEY)
        self.agent = Agent(model)
        self.dataset_id = dataset_id

    async def get_linkedin_posts(self, company_urls: List[str], days: int = 2) -> List[Dict]:
        """Collect and analyze recent LinkedIn posts from specified companies."""
        response_data = get_recent_posts(self.dataset_id, company_urls, days)
        
        response_text = getsnapshot(response_data['snapshot_id'])
        

        posts = self._parse_posts(response_text)
        return await self._analyze_posts(posts)

    
    def _parse_posts(self, response_text: str) -> List[Dict]:
        """Parse raw response into structured post data."""
        data = json.loads(response_text)
        return [{
            'title': post['title'],
            'date': post['date_posted'],
            'url': post['url'],
            'content': post['post_text'],
            'images': post.get('images', []),
            'videos': post.get('videos', []),
            'company': post['use_url'].split('company/')[1].split('/')[0]
        } for post in data]

    async def _analyze_posts(self, posts: List[Dict]) -> List[Dict]:
        """Analyze posts for AI art newsletter relevance."""
        analyzed_posts = []
        for post in posts:
            prompt = f"""
            Analyze this LinkedIn post from {post['company']} for AI art news:
            Content: {post['content']}
            
            Extract:
            1. Key announcement or news
            2. Technology/art innovations mentioned
            3. Relevance to AI art community
            
            Format as a concise newsletter-ready summary focusing on AI art relevance.
            Skip if not relevant to AI art.
            """
            
            result = await self.agent.run(prompt)
            if result.data.strip():  # Only include if there's relevant content
                post['analysis'] = result.data
                analyzed_posts.append(post)
        
        return analyzed_posts