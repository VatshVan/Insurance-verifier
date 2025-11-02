import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

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
        
    query = f"{provider_name} customer reviews"
    
    params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query,
        'num': 1
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'items' in data and len(data['items']) > 0:
            result = data['items'][0]
            
            summary = result.get('snippet', 'No snippet available.')
            details = f"Source: {result.get('displayLink', 'N/A')} | Title: {result.get('title', 'N/A')}"
            
            return {
                "status": "info",
                "summary": summary,
                "details": details
            }
        else:
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