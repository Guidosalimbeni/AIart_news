import requests
from datetime import datetime, timedelta, timezone
from app.core.config import get_settings
import time
import json

# Get settings
settings = get_settings()

def get_recent_posts(dataset_id, profile_urls, days=5):
    """
    Fetch recent posts from X (Twitter) profiles using Brightdata API.
    
    Args:
        dataset_id (str): The Brightdata dataset ID for X/Twitter
        profile_urls (list): List of X profile URLs to fetch
        days (int): Number of days to look back (default: 5)
    
    Returns:
        dict: Response data from the API
    """
    api_token = settings.TWITTER_API_TOKEN
    url = "https://api.brightdata.com/datasets/v3/trigger"
    
    # Calculate the date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Format dates in ISO 8601 format
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    # Construct the data payload
    data = [
        {"url": profile_url, "start_date": start_date_str, "end_date": end_date_str}
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

def get_snapshot(snapshot_id, max_retries=30):  # 5 min max wait
    """
    Retrieve and process the snapshot data, extracting only required fields.
    
    Args:
        snapshot_id (str): The snapshot ID to retrieve
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        list: Processed posts with only description, url, and biography fields
    """
    api_token = settings.TWITTER_API_TOKEN
    headers = {"Authorization": f"Bearer {api_token}"}
    snapshot_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"
    
    for _ in range(max_retries):
        snapshot_response = requests.get(snapshot_url, headers=headers)
        
        if snapshot_response.status_code == 200:
            # Parse the JSON response
            posts = json.loads(snapshot_response.text)
            
            # Extract only the required fields
            processed_posts = [
                {
                    "description": post.get("description"),
                    "url": post.get("url"),
                    "biography": post.get("biography")
                }
                for post in posts
            ]
            
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
#         "https://x.com/example1",
#         "https://x.com/example2"
#     ]
    
#     # First, trigger the data collection
#     response = get_recent_posts("your_dataset_id", profile_urls)
    
#     if response and "snapshot_id" in response:
#         # Then fetch and process the snapshot
#         posts = get_snapshot(response["snapshot_id"])
#         print(json.dumps(posts, indent=2))