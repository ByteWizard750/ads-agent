import os
import sys
import json
import requests
from pathlib import Path

def main():
    print("=== Checking Cached Ads Dataset for Valid Media / Base64 ===")
    
    file_path = Path("clients/crowdwisdom/data/ads_sample_raw_full.json.json")
    if not file_path.exists():
        print(f"[Error] File not found: {file_path}")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            ads = json.load(f)
    except Exception as e:
        print(f"[Error] Failed to load JSON: {e}")
        return

    print(f"Loaded {len(ads)} ads from cache.")

    valid_urls = 0
    base64_images = 0

    # test a small subset of urls to avoid massive blocking
    urls_to_test = []

    for ad in ads:
        # Search for base64 in any string fields
        # Check standard media/thumbnail fields in apify output
        # typically: 'image_urls', 'video_urls', 'snapshot_url', 'thumbnail_url', etc.
        # we will convert the ad dict to string and do a quick search for "data:image"
        ad_str = json.dumps(ad)
        if "data:image/" in ad_str:
            base64_images += 1
        
        # collect URLs
        # media fields
        snapshot = ad.get("snapshot", {})
        for field in ["images", "videos", "snapshot_url", "publisher_platform", "cards", "publisherPlatform", "image_urls", "original_image_url"]:
            val = ad.get(field) or snapshot.get(field)
            if val:
                if isinstance(val, str) and val.startswith("http"):
                    urls_to_test.append(val)
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, str) and item.startswith("http"):
                            urls_to_test.append(item)
                        elif isinstance(item, dict):
                            # like cards in carousel
                            if "original_image_url" in item:
                                urls_to_test.append(item["original_image_url"])
                            if "resized_image_url" in item:
                                urls_to_test.append(item["resized_image_url"])
                            if "video_hd_url" in item:
                                urls_to_test.append(item["video_hd_url"])
                            if "video_sd_url" in item:
                                urls_to_test.append(item["video_sd_url"])

    print(f"Found {base64_images} ads containing base64 image data strings.")
    
    unique_urls = list(set(urls_to_test))
    print(f"Found {len(unique_urls)} unique media URLs. Testing a random sample of 25 for validity...")

    import random
    sample_urls = random.sample(unique_urls, min(25, len(unique_urls)))

    valid_urls_found = 0
    for url in sample_urls:
        try:
            r = requests.head(url, timeout=5)
            if r.status_code == 200:
                print(f"[Valid HTTP 200] {url[:60]}...")
                valid_urls_found += 1
            else:
                pass # Expired / 403 / 404
        except Exception:
            pass

    print(f"\nResults:")
    print(f"Base64 Images found: {base64_images}")
    print(f"Valid HTTP 200 URLs found in sample: {valid_urls_found} out of {len(sample_urls)} tested.")

if __name__ == "__main__":
    main()
