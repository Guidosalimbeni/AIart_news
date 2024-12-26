import requests
from datetime import datetime, timedelta, timezone
from app.core.config import get_settings
import time

# Get settings
settings = get_settings()

def get_recent_posts(dataset_id, company_urls, days):
    api_token = settings.LINKEDIN_API_TOKEN
    url = "https://api.brightdata.com/datasets/v3/trigger"
    
    # Calculate the date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    # Format dates in ISO 8601 format
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    # Construct the data payload
    data = [
        {"url": company_url, "start_date": start_date_str, "end_date": end_date_str}
        for company_url in company_urls
    ]

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=data, params={
        "dataset_id": dataset_id,
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "company_url"
    })

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



def getsnapshot(snapshot_id, max_retries=30):  # 5 min max wait
    api_token = settings.LINKEDIN_API_TOKEN 
    headers = {"Authorization": f"Bearer {api_token}"}
    snapshot_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"
    
    for _ in range(max_retries):
        snapshot_response = requests.get(snapshot_url, headers=headers)
        
        if snapshot_response.status_code == 200:
            return snapshot_response.text
        elif snapshot_response.status_code == 202:
            print("Snapshot not ready. Waiting 10 seconds...")
            time.sleep(10)
        else:
            raise Exception(f"Failed to get snapshot: {snapshot_response.status_code}")
            
    raise TimeoutError("Max retries reached waiting for snapshot")




