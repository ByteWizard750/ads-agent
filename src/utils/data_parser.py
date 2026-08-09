import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple


def format_json_stat_entry(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes complex proprietary JSON objects (e.g. stock/crypto signal reports)
    into a clean, voiceover-friendly stat claim string.
    """
    if "claim" in item and isinstance(item["claim"], str):
        return item

    ticker = item.get("ticker") or item.get("symbol") or ""
    title = item.get("title") or item.get("headline") or ""
    direction = item.get("direction") or ""
    price = item.get("current price") or item.get("price") or ""
    target = item.get("target 1") or item.get("target") or ""
    recommendation = item.get("Trading Recommendation") or item.get("recommendation") or ""

    parts = []
    if ticker and direction:
        parts.append(f"Proprietary sentiment signal on {ticker}: {direction}")
    if price and target:
        parts.append(f"Current price ${price} targeting ${target}")
    if title:
        parts.append(f"({title})")

    if parts:
        formatted_claim = " — ".join(parts)
    elif recommendation:
        formatted_claim = str(recommendation)[:200]
    else:
        formatted_claim = json.dumps(item)[:200]

    return {
        "ticker": ticker,
        "direction": direction,
        "price": price,
        "target": target,
        "claim": formatted_claim,
        "raw": item
    }


def parse_proprietary_data(client_data_dir: Path) -> Tuple[List[Dict[str, Any]], bool, str]:
    """
    Format-tolerant parser for client proprietary data in clients/<client_id>/data/.
    Supports CSV, JSON, Markdown, and TXT files.
    Returns: (list_of_stats, has_data_flag, warning_or_info_message)
    """
    if not client_data_dir.exists():
        return [], False, f"Directory {client_data_dir} does not exist."

    # Look for data files excluding hidden files and raw ad dataset cache
    data_files = [
        f for f in client_data_dir.iterdir()
        if f.is_file() 
        and not f.name.startswith(".")
        and not f.name.startswith("ads_sample_raw")
    ]

    if not data_files:
        warning_msg = (
            f"[PROPRIETARY DATA NOTICE] No domain proprietary data files found in '{client_data_dir}'. "
            "Please drop CSV, JSON, Markdown, or TXT data files into this directory for Variant B stat generation."
        )
        print(warning_msg)
        return [], False, warning_msg

    stats = []
    for data_file in data_files:
        ext = data_file.suffix.lower()
        print(f"[Proprietary Data Parser] Ingesting {data_file.name} ({ext})...")

        try:
            if ext == ".json":
                with open(data_file, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                stats.append(format_json_stat_entry(item))
                            else:
                                stats.append({"claim": str(item)})
                    elif isinstance(content, dict):
                        stats.append(format_json_stat_entry(content))

            elif ext == ".csv":
                with open(data_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        stats.append(format_json_stat_entry(dict(row)))

            elif ext in [".txt", ".md"]:
                with open(data_file, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                    for line in lines:
                        stats.append({"claim": line})

        except Exception as e:
            print(f"[Proprietary Data Parser Error] Failed to parse {data_file.name}: {e}")

    if not stats:
        warning_msg = f"[PROPRIETARY DATA NOTICE] Data files found in '{client_data_dir}', but 0 valid stat rows were extracted."
        return [], False, warning_msg

    info_msg = f"Successfully ingested {len(stats)} proprietary data stat entries from {len(data_files)} file(s)."
    print(f"[Proprietary Data Parser] {info_msg}")
    return stats, True, info_msg
