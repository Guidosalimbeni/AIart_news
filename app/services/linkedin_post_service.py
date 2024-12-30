import requests
from datetime import datetime, timedelta, timezone
from app.core.config import get_settings
import time
import json

# Get settings
settings = get_settings()

def get_recent_posts(dataset_id, profile_urls, days=5):
    """
    Fetch recent posts from LinkedIn profiles using Brightdata API.
    
    Args:
        dataset_id (str): The Brightdata dataset ID for LinkedIn
        profile_urls (list): List of LinkedIn profile URLs to fetch
        days (int): Number of days to look back (default: 5)
    
    Returns:
        dict: Response data from the API containing snapshot_id
    """
    api_token = settings.LINKEDIN_API_TOKEN
    url = "https://api.brightdata.com/datasets/v3/trigger"
    
    # Calculate the date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Format dates in ISO 8601 format
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    # Construct the data payload
    # data = [
    #     {"url": profile_url, "start_date": start_date_str, "end_date": end_date_str}
    #     for profile_url in profile_urls
    # ]
    data = [
        {"url": profile_url}
        for profile_url in profile_urls
    ]
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Make the POST request
    response = requests.post(
        url,
        headers=headers,
        json=data,
        params={
            "dataset_id": dataset_id,
            "include_errors": "true",
            "type": "discover_new",
            "discover_by": "profile_url"
        }
    )
    
    # Check the response status code
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        print(f"Response text: {response.text}")
        return None
    
    try:
        response_data = response.json()
        return response_data
    except ValueError as e:
        print("Error decoding JSON response:", e)
        print("Response text:", response.text)
        return None

def get_snapshot(snapshot_id, max_retries=90):  # 15 min max wait
    """
    Retrieve and process the snapshot data from LinkedIn.
    
    Args:
        snapshot_id (str): The snapshot ID to retrieve
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        list: Processed posts with key LinkedIn fields
    """
    api_token = settings.LINKEDIN_API_TOKEN
    headers = {"Authorization": f"Bearer {api_token}"}
    snapshot_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"
    
    for _ in range(max_retries):
        snapshot_response = requests.get(snapshot_url, headers=headers)
        
        if snapshot_response.status_code == 200:
            # Parse the JSON response
            posts = json.loads(snapshot_response.text)
            
            # Process each post to extract relevant LinkedIn fields
            processed_posts = []
            for post in posts:
                processed_post = {
                    "post_id": post.get("id"),
                    "user_id": post.get("user_id"),
                    "profile_url": post.get("use_url"),
                    "title": post.get("title"),
                    "headline": post.get("headline"),
                    "post_text": post.get("post_text"),
                    "date_posted": post.get("date_posted"),
                    "hashtags": post.get("hashtags", []),
                    "embedded_links": post.get("embedded_links", []),
                    "images": post.get("images", []),
                    "videos": post.get("videos"),
                    "num_likes": post.get("num_likes", 0),
                    "num_comments": post.get("num_comments", 0),
                    "user_followers": post.get("user_followers", 0),
                    "user_posts": post.get("user_posts", 0),
                    "tagged_companies": post.get("tagged_companies", []),
                    "tagged_people": post.get("tagged_people", [])
                }
                processed_posts.append(processed_post)
            
            return processed_posts
            
        elif snapshot_response.status_code == 202:
            print("Snapshot not ready. Waiting 10 seconds...")
            time.sleep(10)
        else:
            raise Exception(f"Failed to get snapshot: {snapshot_response.status_code}")
    
    raise TimeoutError("Max retries reached waiting for snapshot")

# # Example usage:
# if __name__ == "__main__":
#     # Example profile URLs
#     profile_urls = [
#         "https://www.linkedin.com/in/example1/",
#         "https://www.linkedin.com/in/example2/"
#     ]
    
#     # First, trigger the data collection
#     response = get_recent_posts("your_dataset_id", profile_urls)
    
#     if response and "snapshot_id" in response:
#         # Then fetch and process the snapshot
#         posts = get_snapshot(response["snapshot_id"])
#         print(json.dumps(posts, indent=2))