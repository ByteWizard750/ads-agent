import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.supabase import get_supabase_client, update_kanban_state
from src.pipeline.graph import build_pipeline_graph


def approve_script(script_id: str):
    """
    CLI tool to manually approve a script variant, update Supabase DB,
    advance kanban_state to 'Rendering Video', and resume the LangGraph pipeline.
    Usage: python scripts/approve_script.py <script_id>
    """
    client = get_supabase_client()
    if not client:
        print("[ERROR] Could not initialize Supabase DB client.")
        sys.exit(1)

    print(f"=== Manually Approving Script ID: {script_id} ===")

    # 1. Fetch script record from Supabase
    res = client.table("scripts").select("*").eq("id", script_id).execute()
    if not res.data:
        print(f"[ERROR] Script ID '{script_id}' not found in Supabase `scripts` table.")
        sys.exit(1)

    script = res.data[0]
    run_id = script["run_id"]
    client_id = script["client_id"]
    variant_type = script["variant_type"]

    print(f"Found Script Variant: '{variant_type}' | Client: '{client_id}' | Run ID: '{run_id}'")

    # 2. Update script approval_status to 'approved'
    update_res = client.table("scripts").update({"approval_status": "approved"}).eq("id", script_id).execute()
    print(f"[Supabase DB] Script '{script_id}' approval_status updated to 'approved'.")

    # 3. Update kanban_state for this run to 'Rendering Video'
    update_kanban_state(client_id, run_id, "Rendering Video", script_id=script_id)
    print(f"[Supabase DB] Kanban state for run '{run_id}' updated to 'Rendering Video'.")

    # 4. Resume LangGraph pipeline from interrupt gate
    print(f"[LangGraph Pipeline] Resuming thread '{run_id}' from 'Awaiting Approval' checkpoint...")
    graph = build_pipeline_graph()
    thread_config = {"configurable": {"thread_id": run_id}}

    try:
        # Resume graph execution passing approved script ID
        graph.update_state(
            thread_config,
            {
                "approved_script_id": script_id,
                "approval_status": "approved",
                "kanban_state": "Rendering Video"
            },
            as_node="script_node"
        )
        print(f"[LangGraph Pipeline] State updated successfully. Ready for Video Agent (Step 5).")
    except Exception as e:
        print(f"[LangGraph Pipeline Warning] ({e}). DB state is updated and unblocked.")

    print(f"\nSUCCESS: Script '{script_id}' is APPROVED. Kanban state is 'Rendering Video'.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/approve_script.py <script_id>")
        sys.exit(1)

    target_script_id = sys.argv[1].strip()
    approve_script(target_script_id)
