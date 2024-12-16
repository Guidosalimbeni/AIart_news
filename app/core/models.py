from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class NewsItem(BaseModel):
    """Model for news items."""
    title: str
    url: str
    snippet: str


class AIArtNews(NewsItem):
    """Model for AI art news items."""
    summary: str
    context: Optional[str] = None
    relevance: float = 1.0
    date: datetime = datetime.now()


class ArtistContext(BaseModel):
    """Model for artist-specific context."""
    title: str
    insight: str
    relevance: float = 1.0
    source_url: Optional[str] = None


class Newsletter(BaseModel):
    """Model for the final newsletter structure."""
    date: datetime
    headline: str
    introduction: str
    news_items: List[AIArtNews]
    artist_insights: List[ArtistContext]
    conclusion: str
    
    def to_markdown(self) -> str:
        """Convert the newsletter to markdown format."""
        md = f"# AI Art Newsletter - {self.date.strftime('%Y-%m-%d')}\n\n"
        md += f"## {self.headline}\n\n"
        md += f"{self.introduction}\n\n"
        
        md += "## Latest in AI Art\n\n"
        for news in self.news_items:
            md += f"### {news.title}\n"
            md += f"*Source: [{news.url}]({news.url})*\n\n"
            md += f"{news.summary}\n\n"
        
        md += "## Artist Insights & Context\n\n"
        for insight in self.artist_insights:
            md += f"### {insight.title}\n"
            md += f"{insight.insight}\n"
            md += f"*Source: {insight.source_url}*\n\n"
        
        md += f"## Final Thoughts\n\n{self.conclusion}\n"
        
        return md
