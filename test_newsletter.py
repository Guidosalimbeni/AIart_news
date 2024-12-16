from app.agents.collector_agent import NewsCollectorAgent
from app.agents.contest_agent import ContestAgent
from app.agents.editor_agent import EditorAgent
import asyncio
from datetime import datetime
import os
from app.core.config import get_settings

settings = get_settings()

async def test_newsletter_generation():
    print("Starting newsletter generation test...")
    
    # Initialize agents
    collector = NewsCollectorAgent()
    contest_agent = ContestAgent()
    editor = EditorAgent()
    
    try:
        # 1. Collect AI art news (limit to 5 items)
        print("\n1. Collecting AI art news...")
        news_items = await collector.collect_news(days=1, limit=5)
        print(f"Found {len(news_items)} news items")
        
        # 2. Gather contest and exhibition information
        print("\n2. Gathering contest and exhibition information...")
        contest_items = await contest_agent.gather_context()
        print(f"Found {len(contest_items)} contests and exhibitions")
        
        # 3. Create and save newsletter
        print("\n3. Creating newsletter...")
        newsletter = await editor.create_newsletter(
            news_items=news_items,
            artist_contests=contest_items
        )
        
        # Save the newsletter
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(
            settings.OUTPUT_DIR,
            f"newsletter_{datetime.now().strftime('%Y%m%d')}.md"
        )
        
        with open(output_path, "w") as f:
            f.write(newsletter.content)  # Use the formatted content from the editor
            
        print(f"\nNewsletter saved to: {output_path}")
        
    except Exception as e:
        print(f"\nError during newsletter generation: {str(e)}")
        raise e

if __name__ == "__main__":
    asyncio.run(test_newsletter_generation())
