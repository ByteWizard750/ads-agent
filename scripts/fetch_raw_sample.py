import os
import json
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

# Fetch last run of apify/facebook-ads-scraper
runs = client.actor("apify/facebook-ads-scraper").runs().list(limit=1, desc=True)

if runs.items:
    last_run = runs.items[0]
    dataset_id = getattr(last_run, "default_dataset_id", None) or last_run.get("defaultDatasetId")
    print(f"Fetching dataset items for Dataset ID: {dataset_id}")
    dataset_items = list(client.dataset(dataset_id).iterate_items(limit=1))
    print(f"Fetched {len(dataset_items)} sample item(s).\n")
    if dataset_items:
        print("=== SAMPLE RAW ITEM FROM APIFY META ADS SCRAPER ===")
        print(json.dumps(dataset_items[0], indent=2))
    else:
        print("Dataset is currently empty or still initializing.")
else:
    print("No runs found.")
