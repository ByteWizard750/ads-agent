import os
import sys
import json
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import ClientConfig, settings


RECOMMENDED_ACTORS = [
    {
        "actor_id": "apify/facebook-ads-scraper",
        "name": "Meta Ads Scraper (Official Apify)",
        "description": "Scrapes Facebook Ads Library via direct search URLs and extracts full creative metadata, captions, media links, and advertiser info.",
    },
    {
        "actor_id": "curious_coder/facebook-ads-library-scraper",
        "name": "Facebook Ads Library Scraper (Curious Coder)",
        "description": "Community actor extracting ad cards, headlines, CTA, and start dates.",
    }
]


def explore_apify():
    print("=== Apify Meta Ads Library Actor Exploration ===")
    
    # 1. Load crowdwisdom search terms
    client_dir = Path(__file__).parent.parent / "clients" / "crowdwisdom"
    cfg = ClientConfig.load_from_dir(client_dir)
    search_terms = cfg.raw_config.get("research", {}).get("search_terms", ["trading signals"])
    print(f"Loaded search terms from config: {search_terms}\n")

    api_token = os.getenv("APIFY_API_TOKEN") or settings.apify_api_token

    if not api_token or api_token == "your-apify-token":
        print("[NOTICE] APIFY_API_TOKEN is not set in .env yet.")
        return

    from apify_client import ApifyClient
    print(f"[INFO] Found APIFY_API_TOKEN. Running test scrape using 'apify/facebook-ads-scraper'...")
    client = ApifyClient(api_token)

    query = search_terms[0]
    encoded_query = urllib.parse.quote(query)
    ad_library_url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=ALL&q={encoded_query}&search_type=keyword_unordered"

    run_input = {
        "startUrls": [{"url": ad_library_url}],
        "maxResults": 3
    }

    try:
        print(f"Submitting test run for URL: {ad_library_url}...")
        run = client.actor("apify/facebook-ads-scraper").call(run_input=run_input)
        dataset_id = run.get("defaultDatasetId")
        print(f"Run completed successfully! Dataset ID: {dataset_id}\n")

        dataset_items = list(client.dataset(dataset_id).iterate_items())
        print(f"Fetched {len(dataset_items)} raw ad items from Apify dataset.\n")

        print("================ RAW OUTPUT STRUCTURE (ITEM 1) ================")
        if dataset_items:
            sample = dataset_items[0]
            print(json.dumps(sample, indent=2))
        else:
            print("Dataset returned 0 items. Checking run log...")

    except Exception as e:
        print(f"[ERROR] Test scrape failed: {e}")


if __name__ == "__main__":
    explore_apify()
