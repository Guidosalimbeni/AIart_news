import requests
import feedparser
from datetime import datetime, timedelta, timezone
import urllib.parse

def get_recent_papers(query="AI Creativity OR AI artists", days=7, max_results = 10):
    """
    Fetch recent papers from arXiv based on query and date range.
    
    Args:
        query (str): Search query for papers
        days (int): Number of days to look back (default: 7)
    
    Returns:
        list: List of papers with their details
    """
    # Calculate the date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Format the query
    search_query = f"{query} AND submittedDate:[{start_date.strftime('%Y%m%d')}* TO {end_date.strftime('%Y%m%d')}*]"
    encoded_query = urllib.parse.quote(search_query)
    
    # arXiv API endpoint
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": encoded_query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results  # Adjust as needed
    }
    
    # Make the GET request
    response = requests.get(base_url, params=params)
    
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        return None
    
    # Parse the response using feedparser
    feed = feedparser.parse(response.text)
    
    # Process and extract relevant information from each paper
    papers = []
    for entry in feed.entries:
        paper = {
            "title": entry.title,
            "abstract": entry.summary,
            "authors": [author.name for author in entry.authors],
            "published": entry.published,
            "url": entry.link,
            "arxiv_id": entry.id.split("/abs/")[-1]
        }
        papers.append(paper)
    
    return papers

def format_paper_details(paper):
    """
    Format paper details into a readable string.
    
    Args:
        paper (dict): Paper details including title, abstract, authors, etc.
    
    Returns:
        str: Formatted string with paper details
    """
    authors_str = ", ".join(paper["authors"])
    published_date = datetime.strptime(paper["published"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
    
    formatted_text = f"""Title: {paper["title"]}
Authors: {authors_str}
Published: {published_date}
URL: {paper["url"]}

Abstract:
{paper["abstract"]}
"""
    return formatted_text
