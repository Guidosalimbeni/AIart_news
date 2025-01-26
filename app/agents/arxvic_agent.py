from datetime import datetime
from typing import List
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic import BaseModel
from ..core.config import get_settings
from ..services.arxiv_service import get_recent_papers, format_paper_details


settings = get_settings()

class ArxvicPreprint(BaseModel):
    """Model for processed X posts about AI art"""
    Title: str
    Authors: str
    Published: str
    URL: str 
    summary: str 

class ArxvicCollectorAgent:
    def __init__(self):
        model = AnthropicModel('claude-3-5-sonnet-latest', api_key=settings.ANTHROPIC_API_KEY)
        self.agent = Agent(model)
        
    
    async def collect_Arxvic_preprints(self, days= 30, max_results=10) -> str:
        """
        Collect and summarize AI art ppreprints
        """
        papers = get_recent_papers(query="AI creativity", days=days, max_results=max_results)
        
        
        if len (papers) < 1:
            return "No preprint content available."
        
        # Process each preprint through the AI agent
        for paper in papers:
            prompt = f"""
            Analyze this preprint about AI creativity or Artistic Applications of AI:
            Preprint Title: {paper.get('title', '')}
            Preprint abstract: {paper.get('abstract', '')}
            Author information: {", ".join(paper.get("authors", ''))}
            
           
            1. Identify the key points about AI art developments, techniques, or artist work
            2. Note any specific artworks or projects mentioned
            3. Extract any relevant technical details about AI art tools or methods
            
            If the preprint is not about AI art, respond with Relevant: no
            If the preprint is about AI art or AI artworks or AI for creativity, respond with Relevant: yes
            
            Format the response as:
            
            title: {paper.get('title', '')} [the title of the preprint]
            Author information: {", ".join(paper.get("authors", ''))}
            Published: {paper.get("published_date", '')}
            Summary: [your concise summary focusing on AI art aspects]
            url: {paper.get('url', '')} [report the url as provided]
            Relevant: [yes or no]
            
            """
            
            result = await self.agent.run(prompt)
            
            # Parse the AI response
            lines = result.data.split('\n')
            is_relevant = False
            summary = " "
            
            for line in lines:
                if line.startswith("Relevant:"):
                    is_relevant = "yes" in line.lower()
                if line.startswith("Summary:"):
                    summary = line.replace("Summary:", "").strip()
   
            processed_preprints = []
            if is_relevant and summary:
                processed_preprints.append(
                    ArxvicPreprint(
                        Title=paper.get('title', 'Unknown'),
                        Authors = ", ".join(paper.get("authors", '')),
                        Published=paper.get('published_date', ''),
                        summary=summary,
                        URL=paper.get('url')
                    )
                )
        
        # Format the processed posts into markdown
        return self._format_markdown(processed_preprints)
    
    def _format_markdown(self, papers: List[ArxvicPreprint]) -> str:
        """
        Format the processed posts into a markdown string
        """
        # if len(papers) < 1 :
        #     return "No relevant AI art updates found on Preprints."
            
        markdown = "## Latest AI Art Preprints \n\n"
        
        for paper in papers:
            markdown += f"### {paper.Title}\n"
            if paper.Authors:
                markdown += f"*{paper.Authors}*\n\n"
            markdown += f"{paper.summary}\n"
            markdown += f"[Read more]({paper.URL})\n\n"
            markdown += f"[Date: ]({paper.Published})\n\n"
            markdown += "---\n\n"
        
        return markdown.strip()

