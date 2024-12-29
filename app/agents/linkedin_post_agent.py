from datetime import datetime
from typing import List
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic import BaseModel
from ..core.config import get_settings
from ..services.linkedin_post_service import get_recent_posts, get_snapshot

settings = get_settings()

class LinkedInPost(BaseModel):
    """Model for processed LinkedIn posts"""
    profile_url: str
    headline: str
    post_text: str

class LinkedInPostCollectorAgent:
    def __init__(self):
        model = AnthropicModel('claude-3-5-sonnet-latest', api_key=settings.ANTHROPIC_API_KEY)
        self.agent = Agent(model)
        self.dataset_id = settings.LINKEDIN_DATASET_ID
    
    async def collect_linkedin_posts(self, profile_urls: List[str], days: int = 3) -> str:
        """
        Collect and process posts from LinkedIn profiles
        
        Args:
            profile_urls: List of LinkedIn profile URLs to analyze
            days: Number of days to look back
            
        Returns:
            str: Formatted markdown text summarizing the LinkedIn posts
        """
        # First collect posts using the LinkedIn service
        response = get_recent_posts(self.dataset_id, profile_urls, days)
        
        if not response or "snapshot_id" not in response:
            return "No LinkedIn posts found for the specified profiles."
            
        # Get the detailed post data
        posts = get_snapshot(response["snapshot_id"])
        
        if not posts:
            return "No post content available."
            
        processed_posts = []
        
        # Process each post through the AI agent
        for post in posts:
            prompt = f"""
            Analyze this LinkedIn post:
            Profile URL: {post.get('use_url', '')}
            Headline: {post.get('headline', '')}
            Post content: {post.get('post_text', '')}
            
            Create a concise summary of the post content. If the post appears to be promotional, an advertisement, or irrelevant, indicate that it should be excluded.
            
            Format the response as:
            Include: [Yes/No]
            Summary: [your concise summary of the post]
            """
            
            result = await self.agent.run(prompt)
            
            # Parse the AI response
            lines = result.data.split('\n')
            include_post = False
            summary = ""
            
            for line in lines:
                if line.startswith("Include:"):
                    include_post = "yes" in line.lower()
                elif line.startswith("Summary:"):
                    summary = line.replace("Summary:", "").strip()
            
            if include_post and summary:
                processed_posts.append(
                    LinkedInPost(
                        profile_url=post.get('use_url', ''),
                        headline=post.get('headline', ''),
                        post_text=summary
                    )
                )
        
        # Format the processed posts into markdown
        return self._format_markdown(processed_posts)
    
    def _format_markdown(self, posts: List[LinkedInPost]) -> str:
        """
        Format the processed posts into a markdown string
        """
        if not posts:
            return "No relevant LinkedIn posts found."
            
        markdown = "## Recent LinkedIn Updates\n\n"
        
        for post in posts:
            if post.headline:
                markdown += f"### {post.headline}\n"
            markdown += f"*Profile: {post.profile_url}*\n\n"
            markdown += f"{post.post_text}\n\n"
            markdown += "---\n\n"
        
        return markdown.strip()

# # Example usage:
# if __name__ == "__main__":
#     agent = LinkedInPostCollectorAgent()
#     profiles = [
#         "https://www.linkedin.com/in/example1",
#         "https://www.linkedin.com/in/example2"
#     ]
#     result = await agent.collect_linkedin_posts(profiles)
#     print(result)