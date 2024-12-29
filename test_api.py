import requests
import json
from datetime import datetime

def fetch_x_data(api_token):
    # API endpoint
    url = "https://api.brightdata.com/datasets/v3/trigger"
    
    # Request parameters
    params = {
        "dataset_id": "gd_lwxkxvnf1cynvib9co",
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "profile_url"
    }
    
    # Request headers
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Request data
    data = [{
        "url": "https://x.com/lauramherman_",
        "start_date": "2024-12-10T16:31:04.000Z",
        "end_date": "2024-12-26T22:00:06.000Z"
    }]
    
    # Make the request
    try:
        response = requests.post(url, headers=headers, params=params, json=data)
        
        # Print status code for debugging
        print(f"Status Code: {response.status_code}")
        
        # If successful, print the response
        if response.status_code == 200:
            print("\nResponse:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("\nError Response:")
            print(response.text)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Replace with your actual API token
    api_token = "f83094bc85523d4142e39946c337dbf22e724d5f89b91cf20c65bc9f7e21638a"
    fetch_x_data(api_token)