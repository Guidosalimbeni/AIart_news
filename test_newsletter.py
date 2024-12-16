from app.agents.collector_agent import NewsCollectorAgent
from app.agents.context_agent import ContextAgent
from app.agents.editor_agent import EditorAgent
import asyncio
from datetime import datetime

async def test_newsletter_generation():
    print("Starting newsletter generation test...")
    
    # Initialize agents
    collector = NewsCollectorAgent()
    context_agent = ContextAgent()
    editor = EditorAgent()
    
    try:
        # Step 1: Collect news
        print("\n1. Collecting AI art news...")
        news_items = await collector.collect_news()
        print(f"Found {len(news_items)} news items")
        
        # Step 2: Add context to news items
        print("\n2. Adding context to news items...")
        news_with_context = await context_agent.add_context(news_items)
        print("Context added successfully")
        
        # Step 3: Generate artist insights
        print("\n3. Gathering artist context...")
        artist_contexts = await context_agent.gather_context()
        print(f"Generated {len(artist_contexts)} artist insights")
        
        # Step 4: Create newsletter
        print("\n4. Creating newsletter...")
        newsletter = await editor.create_newsletter(news_with_context, artist_contexts)
        
        # Print the result
        print("\n=== Generated Newsletter ===")
        print(f"Date: {newsletter.date}")
        print(f"\nHeadline: {newsletter.headline}")
        print(f"\nIntroduction:\n{newsletter.introduction}")
        
        print("\nNews Items:")
        for item in newsletter.news_items:
            print(f"\n- {item.title}")
            print(f"  Summary: {item.summary}")
            print(f"  Context: {item.context}")
            print(f"  URL: {item.url}")
        
        print("\nArtist Insights:")
        for insight in newsletter.artist_insights:
            print(f"\n- {insight.title}")
            print(f"  Insight: {insight.insight}")
        
        print(f"\nConclusion:\n{newsletter.conclusion}")
        
        print("\nNewsletter generation test completed successfully! ✅")
        
    except Exception as e:
        print(f"\nError during newsletter generation: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_newsletter_generation())
