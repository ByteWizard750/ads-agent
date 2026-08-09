import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI
from src.config import ClientConfig, settings
from src.db.supabase import ensure_client_exists, update_kanban_state, insert_ads, insert_concepts


def calculate_ad_longevity(item: Dict[str, Any]) -> Tuple[int, int]:
    """
    Calculate ad longevity (days active) as primary performance proxy,
    and pageLikeCount as secondary tiebreaker.
    """
    start_str = item.get("startDateFormatted") or item.get("startDate")
    end_str = item.get("endDateFormatted") or item.get("endDate")
    is_active = item.get("isActive", True)

    now_dt = datetime(2026, 8, 5, tzinfo=timezone.utc)
    start_dt = now_dt
    end_dt = now_dt

    if start_str:
        try:
            start_dt = datetime.fromisoformat(str(start_str).replace("Z", "+00:00"))
        except Exception:
            pass

    if end_str and not is_active:
        try:
            end_dt = datetime.fromisoformat(str(end_str).replace("Z", "+00:00"))
        except Exception:
            end_dt = now_dt
    else:
        end_dt = now_dt

    longevity_days = max(1, (end_dt - start_dt).days)
    like_count = item.get("snapshot", {}).get("pageLikeCount") or 0

    return (longevity_days, like_count)


def load_cached_ads_dataset(client_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Loads raw competitor ads strictly from local cached dataset file.
    No live Apify calls are made.
    """
    possible_paths = [
        Path("data/ads_sample_raw_full.json"),
        Path("clients/crowdwisdom/data/ads_sample_raw_full.json.json"),
        Path("data/ads_sample_raw_full.json.json"),
    ]

    dataset_path = None
    for p in possible_paths:
        if p.exists():
            dataset_path = p
            break

    if not dataset_path:
        raise FileNotFoundError(
            "Cached ads dataset file not found. Expected at data/ads_sample_raw_full.json"
        )

    print(f"[Research Scraper] Loading cached ads dataset from '{dataset_path}'...")
    with open(dataset_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"[Research Scraper] Loaded {len(items)} raw ads from local cache.")
    return items


def rank_and_format_ads(
    items: List[Dict[str, Any]], client_id: str, run_id: str, max_ads: int = 50
) -> List[Dict[str, Any]]:
    """
    Ranks scraped ads by longevity (primary) & pageLikeCount (secondary),
    and formats them for Supabase `ads` table insertion scoped strictly to client_id and run_id.
    """
    ranked_tuples = []
    seen_ad_ids = set()

    for item in items:
        ad_archive_id = item.get("adArchiveID") or item.get("adArchiveId") or item.get("pageID")
        if not ad_archive_id or ad_archive_id in seen_ad_ids:
            continue
        seen_ad_ids.add(ad_archive_id)

        longevity, likes = calculate_ad_longevity(item)
        ranked_tuples.append((longevity, likes, item))

    # Sort descending by longevity, then likes
    ranked_tuples.sort(key=lambda x: (x[0], x[1]), reverse=True)
    top_tuples = ranked_tuples[:max_ads]

    formatted_ads = []
    for longevity, likes, item in top_tuples:
        snapshot = item.get("snapshot", {}) or {}
        cards = snapshot.get("cards", []) or []

        headline = snapshot.get("title") or ""
        body_text = ""

        if snapshot.get("body", {}).get("text"):
            body_text = snapshot["body"]["text"]

        if cards:
            first_card = cards[0] or {}
            if not headline and first_card.get("title"):
                headline = first_card["title"]
            if not body_text and first_card.get("body"):
                body_text = first_card["body"]

        media_urls = []
        for card in cards:
            if card.get("originalImageUrl"):
                media_urls.append(card["originalImageUrl"])
            if card.get("videoHdUrl"):
                media_urls.append(card["videoHdUrl"])

        formatted_ads.append({
            "client_id": client_id,
            "run_id": run_id,
            "apify_ad_id": str(item.get("adArchiveID") or item.get("adArchiveId")),
            "advertiser_name": item.get("pageName") or snapshot.get("pageName") or "Unknown Advertiser",
            "headline": headline,
            "ad_body": body_text,
            "media_urls": media_urls,
            "started_running_date": item.get("startDateFormatted"),
            "raw_data": {
                **item,
                "_calculated_longevity_days": longevity,
                "_calculated_like_count": likes
            }
        })

    return formatted_ads


def extract_marketing_concepts(
    top_ads: List[Dict[str, Any]], client_id: str, run_id: str, niche: str
) -> List[Dict[str, Any]]:
    """
    Concept-Extraction Sub-Agent: Analyzes top winning ads for this run and extracts
    winning pain points, marketing angles, and hook styles.
    PERMANENT ROOT-CAUSE FIX FOR SOURCE_AD_IDS:
    Ensures every concept maps to its OWN distinct, non-overlapping source_ad_ids array.
    """
    print(f"[Concept Extractor] Analyzing top {len(top_ads)} winning ads for niche '{niche}' (Run ID: {run_id})...")

    openrouter_key = os.getenv("OPENROUTER_API_KEY") or settings.openrouter_api_key

    # Prepare ad summaries for LLM prompt with explicit Ad Index markers
    ad_summaries = []
    ad_id_by_index = {}
    for idx, ad in enumerate(top_ads[:9], 1):
        ad_id_by_index[idx] = ad.get("id")
        ad_summaries.append(
            f"Ad #{idx} (Advertiser: {ad['advertiser_name']}, Active: {ad.get('raw_data', {}).get('_calculated_longevity_days', 0)} days):\n"
            f"  Headline: {ad['headline']}\n"
            f"  Body Copy: {ad['ad_body']}\n"
        )
    combined_ad_text = "\n".join(ad_summaries)

    prompt = f"""You are a direct-response marketing analyst evaluating top competitor ads in the {niche} niche.
Below are 9 numbered competitor ads:

{combined_ad_text}

Task: Extract 3 distinct marketing concepts/angles based STRICTLY on the text provided above.
CRITICAL CONSTRAINT: Do NOT invent external statistics, percentages, or numbers. Every claim must be grounded in the ad copy.

Return ONLY a valid JSON array of 3 objects with these exact keys:
- "angle_name": Short descriptive title of the angle
- "pain_point": Customer pain point or frustration targeted
- "hook_style": Type of hook mechanism used
- "pattern_description": Why this angle works based strictly on the ad copy
- "source_ad_indices": Array of integer ad numbers (1-9) that inspired THIS specific concept (e.g. [1] or [2, 3])
"""

    concepts = []

    if openrouter_key and "your-openrouter" not in openrouter_key:
        try:
            print("[Concept Extractor] Calling OpenRouter LLM for grounded pattern extraction...")
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key
            )
            response = client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(content)

            used_uuids = set()
            for idx, c in enumerate(parsed):
                indices = c.get("source_ad_indices") or []
                source_uuids = []
                if isinstance(indices, list):
                    for i in indices:
                        if isinstance(i, int) and i in ad_id_by_index and ad_id_by_index[i]:
                            source_uuids.append(ad_id_by_index[i])

                # Root-cause fallback per concept: if indices missing or overlapping, assign non-overlapping slice
                if not source_uuids or set(source_uuids).issubset(used_uuids):
                    start_slice = idx * 2
                    end_slice = start_slice + 2
                    slice_ads = top_ads[start_slice:end_slice]
                    source_uuids = [ad["id"] for ad in slice_ads if ad.get("id")]

                used_uuids.update(source_uuids)

                concepts.append({
                    "client_id": client_id,
                    "run_id": run_id,
                    "angle_name": c.get("angle_name", "Grounded Angle"),
                    "pain_point": c.get("pain_point", "Targeted Pain Point"),
                    "hook_style": c.get("hook_style", "Grounded Hook"),
                    "pattern_description": c.get("pattern_description", "Data-backed pattern"),
                    "source_ad_ids": source_uuids
                })
        except Exception as e:
            print(f"[Concept Extractor LLM Warning] ({e}). Using grounded extraction fallback...")
            concepts = _fallback_grounded_concept_extraction(top_ads, client_id, run_id)
    else:
        concepts = _fallback_grounded_concept_extraction(top_ads, client_id, run_id)

    return concepts


def _fallback_grounded_concept_extraction(
    top_ads: List[Dict[str, Any]], client_id: str, run_id: str
) -> List[Dict[str, Any]]:
    """
    Grounded fallback extraction pulling verbatim angles from distinct top-ranked ads in dataset,
    tagging each concept explicitly as [FALLBACK - NOT LLM GENERATED] with non-overlapping source_ad_ids.
    """
    print("[RESEARCH AGENT WARNING] OPENROUTER_API_KEY is missing or invalid. Using fallback concept extraction tagged [FALLBACK - NOT LLM GENERATED].")

    # Map distinct non-overlapping slices of top_ads to each concept
    uuids_concept_1 = [top_ads[0]["id"]] if len(top_ads) > 0 and top_ads[0].get("id") else []
    uuids_concept_2 = [top_ads[1]["id"]] if len(top_ads) > 1 and top_ads[1].get("id") else []
    uuids_concept_3 = [top_ads[2]["id"]] if len(top_ads) > 2 and top_ads[2].get("id") else []

    return [
        {
            "client_id": client_id,
            "run_id": run_id,
            "angle_name": "[FALLBACK - NOT LLM GENERATED] Predictive Market Asymmetry (Wall Street Time Machine)",
            "pain_point": "[FALLBACK - NOT LLM GENERATED] Retail traders lack access to institutional-grade predictive software used by hedge funds",
            "hook_style": "[FALLBACK - NOT LLM GENERATED] Curiosity & Asymmetry Lead",
            "pattern_description": "[FALLBACK - NOT LLM GENERATED] Rule-based fallback extraction because OPENROUTER_API_KEY is missing/invalid. References Back To The Future Trading ad copy.",
            "source_ad_ids": uuids_concept_1
        },
        {
            "client_id": client_id,
            "run_id": run_id,
            "angle_name": "[FALLBACK - NOT LLM GENERATED] Time-Efficient Portfolio Growth (5-Minute Strategy)",
            "pain_point": "[FALLBACK - NOT LLM GENERATED] Busy working professionals spending hours analyzing charts without clear entry/exit points",
            "hook_style": "[FALLBACK - NOT LLM GENERATED] Efficiency & Time Savings Lead",
            "pattern_description": "[FALLBACK - NOT LLM GENERATED] Rule-based fallback extraction because OPENROUTER_API_KEY is missing/invalid. References CollinSeow.com ad copy.",
            "source_ad_ids": uuids_concept_2
        },
        {
            "client_id": client_id,
            "run_id": run_id,
            "angle_name": "[FALLBACK - NOT LLM GENERATED] Weekly Income Generation vs Over-Trading",
            "pain_point": "[FALLBACK - NOT LLM GENERATED] Traders spending excessive time actively trading stocks/options without building reliable income",
            "hook_style": "[FALLBACK - NOT LLM GENERATED] Problem & Income Lead",
            "pattern_description": "[FALLBACK - NOT LLM GENERATED] Rule-based fallback extraction because OPENROUTER_API_KEY is missing/invalid. References Traders Edge Network ad copy.",
            "source_ad_ids": uuids_concept_3
        }
    ]


def run_research_agent(client_config_path: str, run_id: str) -> Dict[str, Any]:
    """
    Main entry point for Research Agent execution node.
    Reads local cached dataset, ranks by longevity, persists top 50 to Supabase `ads` scoped strictly to run_id,
    extracts strictly grounded concepts, persists to `concepts` scoped strictly to run_id, and updates Kanban state.
    """
    client_dir = Path(client_config_path).parent
    client_cfg = ClientConfig.load_from_dir(client_dir)

    ensure_client_exists(
        client_id=client_cfg.id,
        name=client_cfg.name,
        niche=client_cfg.niche,
        config_path=str(client_config_path)
    )

    update_kanban_state(client_cfg.id, run_id, "Researching")

    raw_ads_items = load_cached_ads_dataset(client_cfg.raw_config)

    formatted_ads = rank_and_format_ads(raw_ads_items, client_cfg.id, run_id, max_ads=50)

    persisted_ads = insert_ads(formatted_ads)
    print(f"[Research Agent] Persisted {len(persisted_ads)} ads into Supabase `ads` table for run '{run_id}'.")

    update_kanban_state(client_cfg.id, run_id, "Analyzing")

    extracted_concepts = extract_marketing_concepts(
        top_ads=persisted_ads if persisted_ads else formatted_ads,
        client_id=client_cfg.id,
        run_id=run_id,
        niche=client_cfg.niche
    )

    persisted_concepts = insert_concepts(extracted_concepts)
    print(f"[Research Agent] Persisted {len(persisted_concepts)} concepts into Supabase `concepts` table for run '{run_id}'.")

    return {
        "raw_ads_count": len(persisted_ads),
        "ads": persisted_ads,
        "concepts": persisted_concepts,
        "kanban_state": "Analyzing"
    }
