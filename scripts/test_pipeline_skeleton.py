import sys
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import ClientConfig
from src.pipeline.graph import build_pipeline_graph


def run_pipeline_test():
    print("=== Testing LangGraph 3-Agent Pipeline Skeleton ===")

    # 1. Load client configuration for crowdwisdom
    client_dir = Path(__file__).parent.parent / "clients" / "crowdwisdom"
    client_cfg = ClientConfig.load_from_dir(client_dir)
    print(f"Loaded Client Config: {client_cfg.name} (ID: {client_cfg.id})")

    # 2. Compile graph with memory checkpointing
    graph = build_pipeline_graph()
    run_id = str(uuid.uuid4())
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

    # 3. Phase A: Run graph until human approval interrupt (before video_node)
    print("\n--- Phase A: Running Graph (Research -> Script -> Approval Gate) ---")
    for event in graph.stream(initial_state, config=thread_config):
        print(f"Graph Event: {list(event.keys())}")

    current_state = graph.get_state(thread_config)
    print(f"\n[Interrupt Gate Reached] Current Kanban State: {current_state.values.get('kanban_state')}")
    print(f"Generated Script Variants count: {len(current_state.values.get('scripts', []))}")
    for s in current_state.values.get('scripts', []):
        print(f"  - [{s['id']}] {s['variant_type']}: \"{s['hook_text']}\"")

    # Verify pipeline paused before video_node
    next_nodes = current_state.next
    print(f"Next Node(s) Waiting for Human Approval: {next_nodes}")
    assert "video_node" in next_nodes, "Graph should be interrupted right before video_node"

    # 4. Phase B: Human Approval Simulation
    chosen_script_id = "script_var_b"
    print(f"\n--- Phase B: Simulating Human Approval via Telegram for '{chosen_script_id}' ---")

    # Update graph state with approval selection
    graph.update_state(
        thread_config,
        {
            "approved_script_id": chosen_script_id,
            "approval_status": "approved",
        },
        as_node="script_node"
    )

    # 5. Resume Graph Execution through video_node to Completion
    print("\n--- Resuming Graph Execution to Render Video ---")
    for event in graph.stream(None, config=thread_config):
        print(f"Graph Event: {list(event.keys())}")

    final_state = graph.get_state(thread_config)
    print(f"\n[Final State] Kanban State: {final_state.values.get('kanban_state')}")
    print(f"Rendered Video Result: {final_state.values.get('video_result')}")
    print("\nState History Lifecycle Trail:")
    for h in final_state.values.get("history", []):
        print(f"  - [{h['state']}] {h['detail']} (at {h['timestamp']})")

    print("\n=== Skeleton Test Completed Successfully! ===")


if __name__ == "__main__":
    run_pipeline_test()
