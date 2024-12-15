from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class AIArtNews(BaseModel):
    """Model for AI art news items."""
    title: str
    url: str
    date: datetime
    summary: str
    source: str
    relevance_score: float


class ArtistContext(BaseModel):
    """Model for artist-specific context."""
    topic: str
    insights: str
    relevance: float
    source: str


class Newsletter(BaseModel):
    """Model for the final newsletter structure."""
    date: datetime
    headline: str
    introduction: str
    news_items: List[AIArtNews]
    artist_insights: List[ArtistContext]
    conclusion: Optional[str]
    
    def to_markdown(self) -> str:
        """Convert the newsletter to markdown format."""
        md = f"# AI Art Newsletter - {self.date.strftime('%Y-%m-%d')}\n\n"
        md += f"## {self.headline}\n\n"
        md += f"{self.introduction}\n\n"
        
        md += "## Latest in AI Art\n\n"
        for news in self.news_items:
            md += f"### {news.title}\n"
            md += f"*Source: [{news.source}]({news.url})*\n\n"
            md += f"{news.summary}\n\n"
        
        md += "## Artist Insights & Context\n\n"
        for insight in self.artist_insights:
            md += f"### {insight.topic}\n"
            md += f"{insight.insights}\n"
            md += f"*Source: {insight.source}*\n\n"
        
        if self.conclusion:
            md += f"## Final Thoughts\n\n{self.conclusion}\n"
        
        return md
