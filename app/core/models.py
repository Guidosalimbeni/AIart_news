from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class NewsItem(BaseModel):
    """Model for a single news item from search results."""
    title: str
    url: str
    snippet: str


class AIArtNews(BaseModel):
    """Model for processed AI art news with analysis."""
    title: str
    url: str
    summary: str
    relevance: float = 1.0  # Added back for sorting
    date: datetime = datetime.now()


class ArtistContest(BaseModel):
    """Model for artist contest and exhibition opportunities."""
    title: str
    insight: str
    relevance: float = 1.0
    source_url: str


class Newsletter(BaseModel):
    """Model for the complete AI art newsletter."""
    date: datetime
    headline: str
    introduction: str
    news_items: List[AIArtNews]
    artist_insights: List[ArtistContest]
    conclusion: str
    content: str  # The complete formatted markdown content
    
    def to_markdown(self) -> str:
        """Return the complete markdown content."""
        return self.content
