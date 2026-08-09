import sys
import uuid
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import ClientConfig
from src.pipeline.graph import build_pipeline_graph
from src.db.supabase import create_run_record


def main():
    print("=== Executing Research + Script Agents via LangGraph Pipeline ===")

    client_dir = Path("clients/crowdwisdom")
    client_cfg = ClientConfig.load_from_dir(client_dir)

    run_id = create_run_record(client_cfg.id, client_cfg.name, client_cfg.niche, "clients/crowdwisdom/config.yaml")
    print(f"Created Run Record in Supabase DB: {run_id}")

    graph = build_pipeline_graph()
    thread_config = {"configurable": {"thread_id": run_id}}

    initial_state = {
        "client_id": client_cfg.id,
        "run_id": run_id,
        "config": client_cfg.raw_config,
        "kanban_state": "Todo",
        "raw_ads": [],
        "concepts": [],
        "scripts": [],
        "approved_script_id": None,
        "approval_status": None,
        "rejection_reason": None,
        "video_result": None,
        "error": None,
        "history": [],
    }

    print("\n--- Running Graph Pipeline (Research Node -> Script Node -> Pause at Approval Gate) ---")
    for event in graph.stream(initial_state, config=thread_config):
        print(f"Graph Event Executed: {list(event.keys())}")

    state = graph.get_state(thread_config)
    current_kanban = state.values.get("kanban_state")
    scripts = state.values.get("scripts", [])

    print(f"\n[INTERRUPT GATE REACHED] Current Kanban State: {current_kanban}")
    print(f"Next Node Waiting for Approval: {state.next}")

    print("\n================ SCRIPT AGENT GENERATED VARIANTS ================")
    for idx, script in enumerate(scripts, 1):
        print(f"\nVariant #{idx} [{script['variant_type']}]")
        print(f"  • Hook (First 1-2s): \"{script['hook_text']}\"")
        print(f"  • Full Voiceover Script:\n    {script['body_script']}")
        print(f"  • Estimated Duration: {script.get('duration_seconds', 45)}s")
        print(f"  • Approval Status: {script.get('approval_status')}")

    print("\n================ VARIANT B SOURCE JSON FIELD MAPPING ================")
    source_file = "clients/crowdwisdom/data/SNOW_2026-04-27.json"
    if Path(source_file).exists():
        with open(source_file, "r") as f:
            raw_json = json.load(f)
        print(f"Source JSON File: {source_file}")
        print("Field Mappings:")
        print(f"  1. Ticker Symbol: '{raw_json.get('ticker')}' -> Source field: 'ticker': \"{raw_json.get('ticker')}\"")
        print(f"  2. Trade Direction: '{raw_json.get('direction')}' -> Source field: 'direction': \"{raw_json.get('direction')}\"")
        print(f"  3. Entry Price: '${raw_json.get('current price')}' -> Source field: 'current price': \"{raw_json.get('current price')}\"")
        print(f"  4. Target Price 1: '${raw_json.get('target 1')}' -> Source field: 'target 1': \"{raw_json.get('target 1')}\"")
        print(f"  5. Stop Loss 1: '${raw_json.get('stop 1')}' -> Source field: 'stop 1': \"{raw_json.get('stop 1')}\"")
        print(f"  6. Confidence Score: '{raw_json.get('confidence level')}%' -> Source field: 'confidence level': \"{raw_json.get('confidence level')}\"")
        print(f"  7. Sentiment Weighting: X (30%), Groq (60%) -> Source field: 'sources weights': {raw_json.get('sources weights')}")

    print("\n=== Script Agent Execution Complete (Paused for Human Review) ===")


if __name__ == "__main__":
    main()
