import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI
from src.config import ClientConfig, settings
from src.utils.data_parser import parse_proprietary_data
from src.db.supabase import get_supabase_client, update_kanban_state


def insert_scripts(scripts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    client = get_supabase_client()
    if not client or not scripts_data:
        return scripts_data

    res = client.table("scripts").insert(scripts_data).execute()
    return res.data or []


def generate_script_variants(
    client_cfg: ClientConfig,
    concepts: List[Dict[str, Any]],
    proprietary_stats: List[Dict[str, Any]],
    has_data: bool,
    data_warning: str,
    run_id: str
) -> List[Dict[str, Any]]:
    """
    Script Agent: Uses OpenRouter frontier model routing to generate 3 distinct 30-60s script variants
    (Variant A: Pain Point, Variant B: Proprietary Stat, Variant C: Product Solution).
    """
    openrouter_key = os.getenv("OPENROUTER_API_KEY") or settings.openrouter_api_key

    # Target client details
    client_id = client_cfg.id
    raw_cfg = client_cfg.raw_config.get("scripting", {})
    target_audience = raw_cfg.get("target_audience", "Retail traders and investors")
    tone = raw_cfg.get("tone", "Authoritative, data-backed, relatable, energetic")
    value_prop = raw_cfg.get("primary_value_proposition", "Quantitative sentiment analysis and algorithmic indicators")
    cta = raw_cfg.get("call_to_action", "Claim your free 7-day trial of CrowdWisdomTrading signals now")

    # Select top concept pain point
    top_concept = concepts[0] if concepts else {
        "angle_name": "Emotional Trading vs Data-Driven Signals",
        "pain_point": "Retail traders suffering consistent losses due to emotional FOMO and lack of systematic risk management",
        "hook_style": "Pain Point Lead"
    }

    # Format proprietary stat reference for Variant B
    stat_reference = ""
    if has_data and proprietary_stats:
        first_stat = proprietary_stats[0]
        stat_reference = f"Proprietary Stat: {json.dumps(first_stat)}"
    else:
        stat_reference = f"[FLAG: Proprietary data files pending in clients/{client_id}/data/. Using client value proposition metric: '{value_prop}']"

    prompt = f"""You are a world-class direct-response video ad scriptwriter and hook engineer.
Write 3 distinct 30-60 second video ad scripts for brand: {client_cfg.name} (Niche: {client_cfg.niche}).

Client Parameters:
- Target Audience: {target_audience}
- Brand Tone: {tone}
- Value Proposition: {value_prop}
- Call to Action: {cta}
- Extracted Market Pain Point: {top_concept.get('pain_point')}
- {stat_reference}

Required 3 Variants:
1. Variant A (variant_a_pain_point): Leads with the identified customer pain point in the first 1-2 seconds.
2. Variant B (variant_b_stat): Leads with a data-backed stat/metric in the first 1-2 seconds.
3. Variant C (variant_c_solution): Leads with how the product/service directly solves the problem in the first 1-2 seconds.

Return ONLY a valid JSON array of 3 objects with these exact keys:
- "variant_type": "variant_a_pain_point" | "variant_b_stat" | "variant_c_solution"
- "hook_text": First 1-2 seconds scroll-stopping hook sentence
- "body_script": Full 30-60 second voiceover script text including Call to Action
- "duration_seconds": Estimated voiceover duration (between 30 and 60)
"""

    variants = []

    if openrouter_key and "your-openrouter" not in openrouter_key:
        try:
            print("[Script Agent] Routing prompt to OpenRouter frontier model (google/gemini-2.5-flash)...")
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key
            )
            response = client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(content)
            for item in parsed:
                concept_id = top_concept.get("id") if isinstance(top_concept.get("id"), str) and len(top_concept.get("id")) == 36 else None
                variants.append({
                    "client_id": client_id,
                    "run_id": run_id,
                    "concept_id": concept_id,
                    "variant_type": item["variant_type"],
                    "hook_text": item["hook_text"],
                    "body_script": item["body_script"],
                    "duration_seconds": item.get("duration_seconds", 45),
                    "approval_status": "pending"
                })
        except Exception as e:
            print(f"[Script Agent OpenRouter Warning] ({e}). Using structured script fallback...")
            variants = _fallback_script_generation(client_cfg, top_concept, has_data, data_warning, run_id, proprietary_stats)
    else:
        print("[Script Agent] OPENROUTER_API_KEY not set. Using structured script generation fallback...")
        variants = _fallback_script_generation(client_cfg, top_concept, has_data, data_warning, run_id, proprietary_stats)

    return variants


def _fallback_script_generation(
    client_cfg: ClientConfig,
    concept: Dict[str, Any],
    has_data: bool,
    data_warning: str,
    run_id: str,
    proprietary_stats: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    client_id = client_cfg.id
    concept_id = concept.get("id") if isinstance(concept.get("id"), str) and len(concept.get("id")) == 36 else None

    # Variant A: Pain point lead
    variant_a = {
        "client_id": client_id,
        "run_id": run_id,
        "concept_id": concept_id,
        "variant_type": "variant_a_pain_point",
        "hook_text": "Stop letting emotional FOMO trades wipe out your hard-earned capital.",
        "body_script": (
            "Stop letting emotional FOMO trades wipe out your hard-earned capital. "
            "The biggest mistake retail traders make is buying at the peak and selling in panic. "
            f"With {client_cfg.name}, you get automated quantitative market sentiment analysis directly to your phone. "
            "No guess work, no emotional stress — just systematic data-backed trade setups. "
            "Claim your free 7-day trial of CrowdWisdomTrading signals today!"
        ),
        "duration_seconds": 45,
        "approval_status": "pending"
    }

    # Variant B: Proprietary stat lead (STRICTLY BLOCKED if has_data is False)
    if not has_data or not proprietary_stats:
        print(f"[SCRIPT AGENT BLOCK] {data_warning}")
        variant_b = {
            "client_id": client_id,
            "run_id": run_id,
            "concept_id": concept_id,
            "variant_type": "variant_b_stat",
            "hook_text": f"[BLOCKED: Missing proprietary data in clients/{client_id}/data/]",
            "body_script": (
                f"[BLOCKED: Cannot generate Variant B. No proprietary data files found in clients/{client_id}/data/. "
                "Please drop CSV, JSON, Markdown, or TXT data files into this directory and re-run.]"
            ),
            "duration_seconds": 0,
            "approval_status": "pending"
        }
    else:
        # Build Variant B using real ingested proprietary data
        first_stat = proprietary_stats[0]
        stat_claim = first_stat.get("claim") or first_stat.get("stat") or str(first_stat)
        variant_b = {
            "client_id": client_id,
            "run_id": run_id,
            "concept_id": concept_id,
            "variant_type": "variant_b_stat",
            "hook_text": f"According to verified data: {stat_claim}",
            "body_script": (
                f"According to verified data: {stat_claim}. "
                f"{client_cfg.name} turns proprietary market metrics into real-time trade signals. "
                "Execute with statistical edge and eliminate impulse trading. "
                "Claim your free 7-day trial of CrowdWisdomTrading signals now!"
            ),
            "duration_seconds": 45,
            "approval_status": "pending"
        }

    # Variant C: Product solution lead
    variant_c = {
        "client_id": client_id,
        "run_id": run_id,
        "concept_id": concept_id,
        "variant_type": "variant_c_solution",
        "hook_text": f"Here is how {client_cfg.name} automates your market analysis in under 5 minutes a day.",
        "body_script": (
            f"Here is how {client_cfg.name} automates your market analysis in under 5 minutes a day. "
            "Our proprietary indicators scan institutional market sentiment and highlight high-probability trade setups automatically. "
            "You get precise entry targets, stop-loss protection, and profit levels delivered straight to your dashboard. "
            "Claim your free 7-day trial of CrowdWisdomTrading signals now!"
        ),
        "duration_seconds": 45,
        "approval_status": "pending"
    }

    return [variant_a, variant_b, variant_c]


def run_script_agent(client_config_path: str, run_id: str, concepts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Main entry point for Script Agent execution node.
    1. Parses proprietary data from clients/<client_id>/data/ (flags clearly if missing).
    2. Generates 3 script variants (A, B, C) via OpenRouter frontier model.
    3. Persists scripts to Supabase `scripts` table with approval_status = 'pending'.
    4. Updates Kanban state: Writing Script -> Awaiting Approval (Human Gate).
    """
    client_dir = Path(client_config_path).parent
    client_cfg = ClientConfig.load_from_dir(client_dir)

    data_dir = client_dir / "data"
    proprietary_stats, has_data, data_warning = parse_proprietary_data(data_dir)

    # 1. Update Kanban state to Writing Script
    update_kanban_state(client_cfg.id, run_id, "Writing Script")

    # 2. Generate 3 script variants
    script_variants = generate_script_variants(
        client_cfg=client_cfg,
        concepts=concepts,
        proprietary_stats=proprietary_stats,
        has_data=has_data,
        data_warning=data_warning,
        run_id=run_id
    )

    # 3. Persist scripts to Supabase `scripts` table
    persisted_scripts = insert_scripts(script_variants)
    print(f"[Script Agent] Persisted {len(persisted_scripts)} script variants into Supabase `scripts` table.")

    # 4. Update Kanban state to Awaiting Approval (Pause at Human Gate)
    update_kanban_state(client_cfg.id, run_id, "Awaiting Approval")
    print(f"[Script Agent] Kanban state updated to 'Awaiting Approval'. Execution paused for human review.")

    return {
        "client_id": client_cfg.id,
        "run_id": run_id,
        "has_proprietary_data": has_data,
        "data_warning": data_warning,
        "scripts": persisted_scripts,
        "kanban_state": "Awaiting Approval"
    }
