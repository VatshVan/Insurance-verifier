import requests
import os
from dotenv import load_dotenv

# Load the .env file to get our secret keys
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

# The URL for the Google Custom Search JSON API
BASE_URL = "https://www.googleapis.com/customsearch/v1"

def get_provider_stats(provider_name):
    """
    Checks the live Google Custom Search API for provider reviews or news.
    """
    if not API_KEY or not SEARCH_ENGINE_ID:
        print("ERROR: GOOGLE_API_KEY or SEARCH_ENGINE_ID not found. Please check your .env file.")
        return {
            "status": "error",
            "summary": "Google Search API keys not configured."
        }
        
    # We will search for the provider's name + "customer reviews"
    query = f"{provider_name} customer reviews"
    
    params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query,
        'num': 1  # We only need the top result
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raises an error for bad responses
        
        data = response.json()
        
        if 'items' in data and len(data['items']) > 0:
            # Success! We found results.
            result = data['items'][0] # Get the top result
            
            # The 'snippet' is the Google search description, perfect for a summary
            summary = result.get('snippet', 'No snippet available.')
            details = f"Source: {result.get('displayLink', 'N/A')} | Title: {result.get('title', 'N/A')}"
            
            return {
                "status": "info",
                "summary": summary,
                "details": details
            }
        else:
            # API call worked, but no results found
            return {
                "status": "info",
                "summary": f"No search results found for '{query}'.",
                "details": "This may mean the provider is not widely discussed."
            }

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return {"status": "error", "summary": f"Could not connect to Google Search (HTTP Error: {http_err.response.status_code})."}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"status": "error", "summary": "An unknown error occurred during Google Search."}