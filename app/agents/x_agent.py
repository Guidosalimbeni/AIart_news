from datetime import datetime
from typing import List
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic import BaseModel
from ..core.config import get_settings
from ..services.twitter_service import get_recent_posts, get_snapshot

settings = get_settings()

class XArtPost(BaseModel):
    """Model for processed X posts about AI art"""
    profile_name: str
    post_url: str
    summary: str
    biography: str | None = None

class XArtNewsCollectorAgent:
    def __init__(self):
        model = AnthropicModel('claude-3-5-sonnet-latest', api_key=settings.ANTHROPIC_API_KEY)
        self.agent = Agent(model)
        self.dataset_id = settings.TWITTER_DATASET_ID
    
    async def collect_x_art_news(self, profile_urls: List[str], days: int = 5) -> str:
        """
        Collect and summarize AI art related posts from X profiles
        
        Args:
            profile_urls: List of X profile URLs to analyze
            days: Number of days to look back
            
        Returns:
            str: Formatted markdown text summarizing the AI art news
        """
        # First collect posts using the X service
        response = get_recent_posts(self.dataset_id, profile_urls, days)
        
        if not response or "snapshot_id" not in response:
            return "No X posts found for the specified profiles."
            
        # Get the detailed post data
        posts = get_snapshot(response["snapshot_id"])
        
        if not posts:
            return "No post content available."
            
        processed_posts = []
        
        # Process each post through the AI agent
        for post in posts:
            prompt = f"""
            Analyze this X (Twitter) post about AI art:
            Post content: {post.get('description', '')}
            Author biography: {post.get('biography', '')}
            
            If this post is about AI art, AI artists, or AI art technology:
            1. Identify the key points about AI art developments, techniques, or artist work
            2. Note any specific artworks or projects mentioned
            3. Extract any relevant technical details about AI art tools or methods
            
            If the post is not about AI art, respond with "Not relevant".
            
            Format the response as:
            Relevant: [Yes/No]
            Summary: [your concise summary focusing on AI art aspects]
            """
            
            result = await self.agent.run(prompt)
            
            # Parse the AI response
            lines = result.data.split('\n')
            is_relevant = False
            summary = ""
            
            for line in lines:
                if line.startswith("Relevant:"):
                    is_relevant = "yes" in line.lower()
                elif line.startswith("Summary:"):
                    summary = line.replace("Summary:", "").strip()
            
            if is_relevant and summary:
                processed_posts.append(
                    XArtPost(
                        profile_name=post.get('user_posted', 'Unknown'),
                        post_url=post.get('url', ''),
                        summary=summary,
                        biography=post.get('biography')
                    )
                )
        
        # Format the processed posts into markdown
        return self._format_markdown(processed_posts)
    
    def _format_markdown(self, posts: List[XArtPost]) -> str:
        """
        Format the processed posts into a markdown string
        """
        if not posts:
            return "No relevant AI art updates found on X."
            
        markdown = "## Latest AI Art Updates from X\n\n"
        
        for post in posts:
            markdown += f"### {post.profile_name}\n"
            if post.biography:
                markdown += f"*{post.biography}*\n\n"
            markdown += f"{post.summary}\n"
            markdown += f"[Read more]({post.post_url})\n\n"
            markdown += "---\n\n"
        
        return markdown.strip()

# Example usage:
# if __name__ == "__main__":
#     agent = XArtNewsCollectorAgent()
#     profiles = [
#         "https://x.com/ai_artist_1",
#         "https://x.com/ai_gallery",
#     ]
#     result = await agent.collect_x_art_news(profiles)
#     print(result)