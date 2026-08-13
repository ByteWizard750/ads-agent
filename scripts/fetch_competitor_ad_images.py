import os
import sys
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.db.supabase import get_supabase_client


def main():
    print("=== Fetching Top Competitor Ad Images by Longevity ===")
    supabase = get_supabase_client()

    # Query top 50 ads ordered by started_running_date ASC (oldest = longest running)
    res = supabase.table("ads").select("id, advertiser_name, started_running_date, media_urls").order("started_running_date", desc=False).limit(50).execute()
    ads = res.data

    if not ads:
        print("[Error] No ads found in Supabase.")
        return

    artifacts_dir = Path("/Users/rohan/.gemini/antigravity-ide/brain/e99eee9b-2642-4eab-bb11-a2b81c975d73")
    images_dir = artifacts_dir / "competitor_ads"
    images_dir.mkdir(parents=True, exist_ok=True)

    markdown_path = artifacts_dir / "competitor_ads_review.md"

    downloaded = []
    
    for ad in ads:
        if len(downloaded) >= 15:
            break

        media_urls = ad.get("media_urls", [])
        if not media_urls:
            continue

        # Find first valid image URL
        img_url = None
        for url in media_urls:
            if isinstance(url, str) and url.startswith("http"):
                # Check for standard image extensions or assume it's valid to try
                img_url = url
                break
        
        if not img_url:
            continue

        page_name = ad.get("advertiser_name", "Unknown")
        started = ad.get("started_running_date", "UnknownDate")[:10] if ad.get("started_running_date") else "UnknownDate"
        safe_name = f"ad_{ad['id']}_{started}.jpg"
        img_path = images_dir / safe_name

        try:
            r = requests.get(img_url, timeout=10)
            if r.status_code == 200:
                with open(img_path, "wb") as f:
                    f.write(r.content)
                downloaded.append({
                    "path": img_path,
                    "page_name": page_name,
                    "started": started
                })
                print(f"Downloaded: {page_name} (Since {started}) -> {safe_name}")
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")

    print(f"\nSuccessfully downloaded {len(downloaded)} competitor ad images.")

    # Generate Markdown Artifact
    md_lines = [
        "# Real Competitor Ad Creatives Review\n",
        "Below are actual creatives from the longest-running active trading/fintech ads in our scraped database. Review these for layout, typography, and how they present data before we design the next template.\n",
    ]

    for item in downloaded:
        md_lines.append(f"### {item['page_name']} (Running since {item['started']})")
        md_lines.append(f"![{item['page_name']} Creative]({item['path']})\n")
        md_lines.append("---\n")

    with open(markdown_path, "w") as f:
        f.write("\n".join(md_lines))

    print(f"Markdown artifact created at {markdown_path}")

if __name__ == "__main__":
    main()
