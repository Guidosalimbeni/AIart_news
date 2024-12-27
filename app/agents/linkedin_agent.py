from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from typing import List, Dict
from ..services.brightdata_service import get_recent_posts, getsnapshot
from ..core.config import get_settings
import json

settings = get_settings()

class LinkedInCollector:
    def __init__(self, dataset_id):
        self.settings = settings
        model = AnthropicModel('claude-3-5-sonnet-latest', api_key=self.settings.ANTHROPIC_API_KEY)
        self.agent = Agent(model)
        self.dataset_id = dataset_id

    async def get_linkedin_posts(self, company_urls: List[str], days: int = 2) -> List[Dict]:
        """Collect and analyze recent LinkedIn posts from specified companies."""
        
        response_id = get_recent_posts(self.dataset_id, company_urls, days)  
        response_text = getsnapshot(response_id['snapshot_id'])
        response_data = json.loads(response_text)
  
        posts = []
        for item in response_data:
            # Check if item is a dictionary
            if isinstance(item, dict):
                # Check for warnings in the response
                if 'warning' in item:
                    print(f"Warning: {item['warning']} for URL: {item.get('input', {}).get('url', 'Unknown URL')}")
                    continue  # Skip this item if there's a warning

                # Parse the post data
                post = self._parse_post(item)
                if post:
                    posts.append(post)
            else:
                print(f"Debug: Unexpected item format: {item}")

        # agent work
        analysed_posts = await self._analyze_posts(posts)
        
        return analysed_posts

    def _parse_post(self, item: Dict) -> Dict:
        """Parse a single post item into a structured format."""
        title = item.get('title', 'No Title Available')
        content = item.get('post_text', 'No Content Available')
        url = item.get('url', 'No URL Available')

        # Only return the post if it has valid data
        if title and content:
            return {
                'title': title,
                'content': content,
                'url': url
            }
        return None

    async def _analyze_posts(self, posts: List[Dict]) -> List[Dict]:
        """Analyze posts for AI art newsletter relevance."""
        analyzed_posts = []
        for post in posts:
            prompt = f"""
            Analyze this LinkedIn post for AI art news:
            Title: {post['title']}
            Content: {post['content']}
            
            Extract:
            1. Key announcement or news
            2. Technology/art innovations mentioned
            3. Relevance to AI art community
            
            Format as a concise newsletter-ready summary focusing on AI art relevance.
            

            """
            
            result = await self.agent.run(prompt)
            if result.data.strip():  # Only include if there's relevant content
                post['analysis'] = result.data
                analyzed_posts.append(post)
        
        return analyzed_posts

#