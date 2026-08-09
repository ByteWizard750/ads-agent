import sys
import json
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.research import run_research_agent
from src.db.supabase import create_run_record


def main():
    print("=== Executing Research Agent for CrowdWisdomTrading ===")
    
    client_config_path = "clients/crowdwisdom/config.yaml"
    run_id = create_run_record("crowdwisdom")
    print(f"Created Run Record in Supabase DB: {run_id}")

    res = run_research_agent(client_config_path=client_config_path, run_id=run_id)

    print("\n--- RESEARCH AGENT SUMMARY RESULTS ---")
    print(f"Run ID: {run_id}")
    print(f"Kanban State: {res['kanban_state']}")
    print(f"Total Raw Ads Scraped & Ranked: {res['raw_ads_count']}")
    print(f"Total Extracted Concepts: {len(res['concepts'])}\n")

    print("================ EXTRACTED MARKETING CONCEPTS ================")
    for idx, concept in enumerate(res["concepts"], 1):
        print(f"\nConcept #{idx}: {concept.get('angle_name')}")
        print(f"  • Pain Point: {concept.get('pain_point')}")
        print(f"  • Hook Style: {concept.get('hook_style')}")
        print(f"  • Strategic Rationale: {concept.get('pattern_description')}")
        print(f"  • Source Ad IDs: {concept.get('source_ad_ids')}")

    print("\n=== Research Agent Run Completed Successfully! ===")


if __name__ == "__main__":
    main()
