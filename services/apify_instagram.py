from apify_client import ApifyClient
import os
from dotenv import load_dotenv
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# services/apify_instagram.py
import httpx
import os
from typing import List

def scrape_instagram_data(instagram_id: str, all_posts: bool = False) -> List[dict]:
    APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN")
    if not APIFY_API_TOKEN:
        raise ValueError("APIFY_API_TOKEN environment variable not found. Please set it in your .env file.")
    
    # Initialize the ApifyClient with your API token
    client = ApifyClient(APIFY_API_TOKEN)

    # Prepare the actor input
    run_input_slow = {
        "directUrls": [f"https://www.instagram.com/{instagram_id}/"],
        "resultsLimit": 50,
        "resultsType": "posts",
        "searchLimit": 1,
        "searchType": "user"
    }
    
    run_input_fast = {
        "directUrls": [f"https://www.instagram.com/{instagram_id}/"],
        "resultsLimit": 1,
        "resultsType": "details",
        "searchLimit": 1,
        "searchType": "hashtag",
        "extendOutputFunction": "",
        "extendScraperFunction": "",
        "customData": {}
    }

    if all_posts:
        print("DEBUG: scraping with slow method !")
        run_input = run_input_slow
    else:
        print(f"DEBUG: scraping with fast method ! for ({instagram_id})")
        run_input = run_input_fast

    # Run the actor and wait for it to finish
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)

    # Fetch and collect actor results from the run's dataset (if there are any)
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)
        
    if all_posts:
        # print(results)
        return results
    else:
        return results[0]["latestPosts"] if len(results) >= 1 else []


if __name__ == "__main__":
    instagram_id = "21n.78e"  # Replace with the desired Instagram profile ID
    scraped_data = scrape_instagram_data(instagram_id,all_posts=False)
    print(scraped_data)
    # Save the result to a JSON file
    output_file = f"{instagram_id}_scraped_data.json"
    with open(output_file, "w") as f:
        json.dump(scraped_data, f)

    print(f"Scraped data saved to {output_file}")
