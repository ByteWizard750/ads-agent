import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.video import run_video_agent
from src.db.supabase import get_supabase_client


def main():
    script_id = "21621ce1-ead5-45ce-a454-c2aae65e2be0"
    run_id = "1b12362d-d2f1-4e79-9fb9-bbdf5bc0aea4"
    config_path = "clients/crowdwisdom/config.yaml"

    print(f"=== Rendering Approved Script '{script_id}' via Video Agent (Step 5) ===")

    # Verify script in Supabase
    client = get_supabase_client()
    res = client.table("scripts").select("*").eq("id", script_id).execute()
    if not res.data:
        print(f"[ERROR] Script ID '{script_id}' not found.")
        sys.exit(1)

    script = res.data[0]
    print(f"Script Variant: {script['variant_type']} | Status: {script['approval_status']}")
    print(f"Body Text: {script['body_script'][:120]}...")

    # Run Video Agent
    video_res = run_video_agent(
        client_config_path=config_path,
        run_id=run_id,
        script_id=script_id,
        design_variant="option3_terminal"
    )

    print("\n================ VIDEO AGENT RENDERING SUMMARY ================")
    print(f"Run ID: {video_res['run_id']}")
    print(f"Script ID: {video_res['script_id']}")
    print(f"Storage Path: {video_res['video_record'].get('storage_path')}")
    print(f"Public Storage URL: {video_res['public_url']}")
    print(f"Kanban State: {video_res['kanban_state']}")
    print("=== Step 5 Video Agent Execution Completed Successfully! ===")


if __name__ == "__main__":
    main()
