import os
import requests
from pathlib import Path
from typing import Dict, Optional, List
from dotenv import load_dotenv

load_dotenv()


def search_and_download_pexels_video(
    query: str,
    output_path: Path,
    orientation: str = "portrait"
) -> Optional[Path]:
    """
    Searches Pexels Stock Video API for portrait video footage matching query
    and downloads the best HD MP4 clip to output_path.
    """
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key or "your-pexels" in api_key or len(api_key) < 10:
        print(f"[Pexels Stock Video Warning] PEXELS_API_KEY missing/placeholder for query '{query}'.")
        return None

    url = f"https://api.pexels.com/videos/search?query={query}&orientation={orientation}&per_page=5"
    headers = {"Authorization": api_key}

    try:
        print(f"[Pexels Stock Video API] Searching portrait video clips for '{query}'...")
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[Pexels Stock Video Error] HTTP {response.status_code}: {response.text}")
            return None

        data = response.json()
        videos = data.get("videos", [])
        if not videos:
            print(f"[Pexels Stock Video] No videos found for query '{query}'.")
            return None

        # Pick the first video with valid HD MP4 file URL
        target_file_url = None
        for v in videos:
            video_files = v.get("video_files", [])
            # Prefer HD MP4 file with height >= 1280 or portrait ratio
            for vf in video_files:
                if vf.get("file_type") == "video/mp4" and vf.get("link"):
                    if vf.get("width", 0) < vf.get("height", 0) or vf.get("height", 0) >= 1080:
                        target_file_url = vf["link"]
                        break
            if target_file_url:
                break
            if video_files:
                target_file_url = video_files[0].get("link")
                break

        if not target_file_url:
            print(f"[Pexels Stock Video] No valid MP4 download link found for '{query}'.")
            return None

        print(f"[Pexels Stock Video] Downloading stock video clip from {target_file_url[:60]}...")
        vid_res = requests.get(target_file_url, stream=True, timeout=30)
        if vid_res.status_code == 200:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                for chunk in vid_res.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[Pexels Stock Video] Stock video saved successfully to '{output_path}'.")
            return output_path
        else:
            print(f"[Pexels Stock Video] Download failed with HTTP {vid_res.status_code}.")
            return None

    except Exception as e:
        print(f"[Pexels Stock Video Exception] ({e}). Skipping clip download.")
        return None


def fetch_stock_footage_for_scenes(
    scenes_queries: Dict[str, str],
    remotion_public_dir: Path = Path("remotion/public/stock_clips")
) -> Dict[str, Optional[str]]:
    """
    Downloads stock footage for each scene and returns relative public paths.
    """
    remotion_public_dir.mkdir(parents=True, exist_ok=True)
    stock_paths = {}

    for scene_key, search_term in scenes_queries.items():
        clip_path = remotion_public_dir / f"{scene_key}.mp4"
        downloaded = search_and_download_pexels_video(search_term, clip_path)
        if downloaded:
            stock_paths[scene_key] = f"stock_clips/{scene_key}.mp4"
        else:
            stock_paths[scene_key] = None

    return stock_paths
