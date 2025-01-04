from app.agents.collector_agent import NewsCollectorAgent
from app.agents.contest_agent import ContestAgent
from app.agents.editor_agent import EditorAgent
from app.agents.linkedin_agent import LinkedInCollector
from app.agents.artist_editor_agent import ArtistEditorAgent
from app.agents.x_agent import XArtNewsCollectorAgent
from app.agents.linkedin_post_agent import LinkedInPostCollectorAgent
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
    linkedin_company_post_agent = LinkedInCollector(settings.LINKEDIN_POSTBYCOMPANY_DATASET_ID)
    editor_artist = ArtistEditorAgent()
    editor = EditorAgent()
    x_agent = XArtNewsCollectorAgent()
    linkedin_profile_post_agent = LinkedInPostCollectorAgent()
    
    try:
        # 1. Collect AI art news (limit to 5 items)
        print("\n1. Collecting AI art news...")
        news_items = await collector.collect_news(days=1, limit=5)
        print(f"Found {len(news_items)} news items")
        
        # 2. Gather contest and exhibition information
        print("\n2. Gathering contest and exhibition information...")
        contest_items = await contest_agent.gather_context()
        print(f"Found {len(contest_items)} contests and exhibitions")

        # 3. Gather LinkedIn company posts
        print("\n3. Gathering LinkedIn posts from companies...")
        company_urls = [
            # "https://www.linkedin.com/company/midjourney/",
            "https://www.linkedin.com/company/arselectronica/",
            # "https://www.linkedin.com/company/runwayml/",
            "https://www.linkedin.com/showcase/somabotics-creatively-embodying-ai/",
            "https://www.linkedin.com/company/the-ai-art-magazine/"
        ]
        try:
            linkedin_posts = await linkedin_company_post_agent.get_linkedin_posts(company_urls, days=5)
            print(f"Found {len(linkedin_posts)} LinkedIn posts")
        except:
            linkedin_posts = []


        # 4. Create the sub newsletter specific to artists news
        print("\n4. Creating newsletter from AI artist news...")
        artists = ['Refik Anadol', 'Sougwen Chung','Stephanie Dinkins', 
                   'Jake Elwes', 'Libby Heaney','Mario Klingemann',
                    'Trevor Paglen', 'Anna Ridler', 'Annie Dorsen',
                    'Caroline Sinders', 'Ellen Pearlman','Gene Kogan',
                    'Mimi Onouha', 'Rachel Ginsberg', 'Tega Brain',
                    'Cecilie Waagner Falkenstrøm','Karen Palmer',
                    'Memo Akten',  'Scott Eaton',  'Wayne McGregor',
                    'Alexander Reben', 'Lauren McCarthy', 'Ross Goodwin',
                    'Nadine Lessio', 'Joy Buolamwini', 'Sofia Crespo',
                    'Tom White', 'Simon Colton', 'William Latham' ]

        sub_newsletter_artists = await editor_artist.create_newsletter(artists)

        # 5 x-twitter news
        print("\n5. Creating newsletter from twitter profile post news...")

        # profiles = [
        #     "https://x.com/elluba",
        #     "https://x.com/SimonGColton",
        #     "https://x.com/lauramherman_"
        # ]
        # days = 20
        # result_x_news = await x_agent.collect_x_art_news(profiles,days)
        # print (result_x_news)
        result_x_news = " "
        print ('skipped as return dead pages')

        # 6 linkedin post news by profile
        print("\n6. Creating newsletter from linkedin profile post news...")

        profile_urls = [
            "https://www.linkedin.com/in/lubaelliott/",
            "https://www.linkedin.com/in/lauraherman-/",
            # "https://www.linkedin.com/in/william-latham-757326/"
        ]
        days = 60
        try:
            result_linkedin_news = await linkedin_profile_post_agent.collect_linkedin_posts(profile_urls,days)
            print (result_linkedin_news)
        except:
            result_linkedin_news = " "
        # print ("Linkedin post by profile not used as no data retrieving")
        # result_linkedin_news = " "

        # 7. Create and save newsletter
        print("\n7. Creating newsletter...")
        newsletter = await editor.create_newsletter(
            news_items=news_items,
            artist_contests=contest_items,
            linkedin_posts=linkedin_posts,
            sub_newsletter_artists=sub_newsletter_artists,
            result_x_news=result_x_news,
            result_linkedin_news=result_linkedin_news
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
