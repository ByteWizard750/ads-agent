import sys
import uuid
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

    print("\n=== Script Agent Execution Complete (Paused for Human Review) ===")


if __name__ == "__main__":
    main()
