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

    # Strip non-database metadata keys (e.g. _field_mapping, _compliance_note)
    db_payload = []
    for s in scripts_data:
        clean = {k: v for k, v in s.items() if not k.startswith("_")}
        db_payload.append(clean)

    res = client.table("scripts").insert(db_payload).execute()
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
    Script Agent: Uses OpenRouter frontier model routing or structured fallback to generate 3 distinct 30-60s script variants
    (Variant A: Pain Point, Variant B: Proprietary Stat, Variant C: Product Solution).
    """
    openrouter_key = os.getenv("OPENROUTER_API_KEY") or settings.openrouter_api_key

    client_id = client_cfg.id
    raw_cfg = client_cfg.raw_config.get("scripting", {})
    target_audience = raw_cfg.get("target_audience", "Retail traders and investors")
    tone = raw_cfg.get("tone", "Authoritative, data-backed, relatable, energetic")
    value_prop = raw_cfg.get("primary_value_proposition", "Quantitative sentiment analysis and algorithmic indicators")
    cta = raw_cfg.get("call_to_action", "Claim your free 7-day trial of CrowdWisdomTrading signals now")

    top_concept = concepts[0] if concepts else {
        "angle_name": "Emotional Trading vs Data-Driven Signals",
        "pain_point": "Retail traders suffering consistent losses due to emotional FOMO and lack of systematic risk management",
        "hook_style": "Pain Point Lead"
    }

    # If OpenRouter key is missing or placeholder, use explicit fallback tagged [FALLBACK - NOT LLM GENERATED]
    if not openrouter_key or "your-openrouter" in openrouter_key:
        print("[SCRIPT AGENT NOTICE] OPENROUTER_API_KEY is missing or placeholder. Using fallback tagged [FALLBACK - NOT LLM GENERATED].")
        return _fallback_script_generation(client_cfg, top_concept, has_data, data_warning, run_id, proprietary_stats)

    # Call OpenRouter API
    try:
        print(f"[Script Agent] Calling OpenRouter LLM (google/gemini-2.5-flash) for client '{client_id}'...")
        stat_reference = json.dumps(proprietary_stats[0]) if has_data and proprietary_stats else "No proprietary data files."
        
        prompt = f"""You are a world-class direct-response video ad scriptwriter and hook engineer for {client_cfg.name} ({client_cfg.niche}).
Target Audience: {target_audience}
Brand Tone: {tone}
Value Proposition: {value_prop}
CTA: {cta}
Market Pain Point: {top_concept.get('pain_point')}
Proprietary Data Stat: {stat_reference}

Generate 3 distinct 30-60 second video ad scripts following these STRICT rules:
1. Variant A (variant_a_pain_point): Hook leads with customer pain point. Focus on emotional stress, FOMO, and over-trading. Do NOT cite specific stock price numbers or ticker symbols.
2. Variant B (variant_b_stat): Exclusively holds specific price targets from Proprietary Data ({stat_reference}). MUST use historical framing ("Here's a real call we made on...") and softened confidence (e.g., "modest 46% confidence"). The spoken body MUST end cleanly at the CTA. Do NOT include disclaimer text inside the spoken voiceover script.
3. Variant C (variant_c_solution): Hook leads with product automation solution (scanning market sentiment in 5 minutes). Focus on system benefits. Do NOT cite specific stock price numbers or ticker symbols.

Return ONLY a valid JSON array of 3 objects with exact keys:
"variant_type", "hook_text", "body_script", "duration_seconds"
"""
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key
        )
        response = client.chat.completions.create(
            model="google/gemini-2.5-pro",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(content)
        
        variants = []
        for item in parsed:
            concept_id = top_concept.get("id") if isinstance(top_concept.get("id"), str) and len(top_concept.get("id")) == 36 else None
            variant_dict = {
                "client_id": client_id,
                "run_id": run_id,
                "concept_id": concept_id,
                "variant_type": item["variant_type"],
                "hook_text": item["hook_text"],
                "body_script": item["body_script"],
                "duration_seconds": item.get("duration_seconds", 45),
                "approval_status": "pending"
            }
            # Attach compliance note metadata if specific price targets or Variant B
            if item["variant_type"] == "variant_b_stat" or "140" in item["body_script"] or "$" in item["body_script"]:
                variant_dict["_compliance_note"] = "Financial ad scripts featuring specific price targets require compliance/legal review before public ad deployment."
            
            variants.append(variant_dict)
        return variants

    except Exception as e:
        print(f"[SCRIPT AGENT LLM ERROR] OpenRouter API call failed ({e}). Falling back to [FALLBACK - NOT LLM GENERATED].")
        return _fallback_script_generation(client_cfg, top_concept, has_data, data_warning, run_id, proprietary_stats)


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
    cta = client_cfg.raw_config.get("scripting", {}).get("call_to_action", "Claim your free 7-day trial of CrowdWisdomTrading signals now")

    # Variant A: Pain point lead
    variant_a = {
        "client_id": client_id,
        "run_id": run_id,
        "concept_id": concept_id,
        "variant_type": "variant_a_pain_point",
        "hook_text": "[FALLBACK - NOT LLM GENERATED] Stop letting emotional FOMO trades wipe out your hard-earned capital.",
        "body_script": (
            "[FALLBACK - NOT LLM GENERATED] Stop letting emotional FOMO trades wipe out your hard-earned capital. "
            "The biggest mistake retail traders make is buying at the peak and selling in panic. "
            f"With {client_cfg.name}, you get automated quantitative market sentiment analysis directly to your phone. "
            "No guess work, no emotional stress — just systematic data-backed trade setups. "
            f"{cta}!"
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
        stat = proprietary_stats[0]
        raw = stat.get("raw", stat)
        
        ticker = raw.get("ticker", "SNOW")
        direction = raw.get("direction", "LONG")
        price = raw.get("current price", "140.32")
        target_1 = raw.get("target 1", "144.80")
        stop_1 = raw.get("stop 1", "137.20")
        confidence = raw.get("confidence level", "46")
        
        hook_b = f"[FALLBACK - NOT LLM GENERATED] Here's a real call we made on {ticker}: Early social sentiment flagged a modest {confidence}% confidence {direction} setup at ${price} targeting ${target_1}."
        body_b = (
            f"[FALLBACK - NOT LLM GENERATED] Here's a real call we made on {ticker}: Early social sentiment signals flagged a modest {confidence}% confidence {direction} setup at ${price} targeting ${target_1} with stop loss at ${stop_1}. "
            f"{client_cfg.name} tracks early community sentiment shifts to surface momentum setups before major moves happen. "
            f"{cta}!"
        )

        variant_b = {
            "client_id": client_id,
            "run_id": run_id,
            "concept_id": concept_id,
            "variant_type": "variant_b_stat",
            "hook_text": hook_b,
            "body_script": body_b,
            "duration_seconds": 45,
            "approval_status": "pending",
            "_compliance_note": "Financial ad scripts featuring specific price targets require compliance/legal review before public ad deployment.",
            "_field_mapping": {
                "fallback notice": "[FALLBACK - NOT LLM GENERATED] Rule-based fallback script generation because OPENROUTER_API_KEY is missing/placeholder.",
                "historical framing": "Explicitly framed as a past historical call ('Here's a real call we made on SNOW')",
                "confidence level": f"Softened to match source 46% confidence ('modest {confidence}% confidence setup')",
                "compliance note": "Tracked separately in .agents/AGENTS.md & metadata (not spoken by Edge-TTS)",
                "ticker": f"ticker -> '{ticker}'",
                "direction": f"direction -> '{direction}'",
                "current price": f"current price -> '${price}'",
                "target 1": f"target 1 -> '${target_1}'",
                "stop 1": f"stop 1 -> '${stop_1}'"
            }
        }

    # Variant C: Product solution lead
    variant_c = {
        "client_id": client_id,
        "run_id": run_id,
        "concept_id": concept_id,
        "variant_type": "variant_c_solution",
        "hook_text": f"[FALLBACK - NOT LLM GENERATED] Here is how {client_cfg.name} automates your market analysis in under 5 minutes a day.",
        "body_script": (
            f"[FALLBACK - NOT LLM GENERATED] Here is how {client_cfg.name} automates your market analysis in under 5 minutes a day. "
            "Our proprietary indicators scan institutional market sentiment and highlight high-probability trade setups automatically. "
            "You get precise entry targets, stop-loss protection, and profit levels delivered straight to your dashboard. "
            f"{cta}!"
        ),
        "duration_seconds": 45,
        "approval_status": "pending"
    }

    return [variant_a, variant_b, variant_c]


def run_script_agent(client_config_path: str, run_id: str, concepts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Main entry point for Script Agent execution node.
    """
    client_dir = Path(client_config_path).parent
    client_cfg = ClientConfig.load_from_dir(client_dir)

    data_dir = client_dir / "data"
    proprietary_stats, has_data, data_warning = parse_proprietary_data(data_dir)

    update_kanban_state(client_cfg.id, run_id, "Writing Script")

    script_variants = generate_script_variants(
        client_cfg=client_cfg,
        concepts=concepts,
        proprietary_stats=proprietary_stats,
        has_data=has_data,
        data_warning=data_warning,
        run_id=run_id
    )

    persisted_scripts = insert_scripts(script_variants)
    print(f"[Script Agent] Persisted {len(persisted_scripts)} script variants into Supabase `scripts` table.")

    update_kanban_state(client_cfg.id, run_id, "Awaiting Approval")
    print(f"[Script Agent] Kanban state updated to 'Awaiting Approval'. Execution paused for human review.")

    return {
        "client_id": client_cfg.id,
        "run_id": run_id,
        "has_proprietary_data": has_data,
        "data_warning": data_warning,
        "scripts": persisted_scripts,
        "field_mapping": script_variants[1].get("_field_mapping") if len(script_variants) > 1 else {},
        "kanban_state": "Awaiting Approval"
    }
