import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.supabase import get_supabase_client
from src.agents.video import run_video_agent

def get_pending_script_approvals():
    """
    Fetches all script variants that belong to runs currently in 'Awaiting Approval'.
    Returns a list of dicts with run_id, script_id, hook_text, body, client_id.
    """
    client = get_supabase_client()
    
    # Get runs in Awaiting Approval
    runs_res = client.table("runs").select("id, client_id").eq("kanban_state", "Awaiting Approval").execute()
    pending_runs = runs_res.data
    
    if not pending_runs:
        return []
        
    results = []
    for run in pending_runs:
        run_id = run["id"]
        scripts_res = client.table("scripts").select("id, variant_type, hook_text, body_script").eq("run_id", run_id).eq("approval_status", "pending").execute()
        
        client_info = client.table("clients").select("config_path").eq("id", run["client_id"]).execute()
        config_path = client_info.data[0]["config_path"] if client_info.data else "clients/crowdwisdom/config.yaml"

        for script in scripts_res.data:
            results.append({
                "run_id": run_id,
                "client_id": run["client_id"],
                "config_path": config_path,
                "script_id": script["id"],
                "variant_type": script["variant_type"],
                "hook_text": script["hook_text"],
                "body_script": script["body_script"]
            })
            
    return results


def approve_script_and_render(run_id: str, script_id: str, config_path: str):
    """
    Approves the chosen script, updates kanban state, and immediately triggers video rendering.
    Returns the absolute path to the local rendered mp4 file.
    """
    client = get_supabase_client()
    
    print(f"[Approval Service] Approving Script {script_id} for Run {run_id}...")
    
    # 1. Update script approval status
    client.table("scripts").update({"approval_status": "approved"}).eq("id", script_id).execute()
    
    # Reject other scripts for this run
    client.table("scripts").update({"approval_status": "rejected"}).eq("run_id", run_id).eq("approval_status", "pending").execute()
    
    # 2. Update Kanban state to Rendering
    client.table("runs").update({"kanban_state": "Rendering Video"}).eq("id", run_id).execute()
    
    # 3. Call Video Agent to render
    print(f"[Approval Service] Triggering Video Agent...")
    video_res = run_video_agent(
        client_config_path=config_path,
        run_id=run_id,
        script_id=script_id
    )
    
    # 4. Update Kanban state to Awaiting Video Approval
    client.table("runs").update({"kanban_state": "Awaiting Video Approval"}).eq("id", run_id).execute()
    
    # Video Agent returns video_record which contains the local file path or public URL
    # But since run_video_agent uploads it, we need the local file path to send inline on Telegram.
    local_mp4 = f"output/crowdwisdom_{run_id}_final.mp4" 
    
    return local_mp4, video_res["video_record"]["id"]


def get_pending_video_approvals():
    """
    Fetches all runs in 'Awaiting Video Approval'.
    """
    client = get_supabase_client()
    runs_res = client.table("runs").select("id, client_id").eq("kanban_state", "Awaiting Video Approval").execute()
    return runs_res.data


def approve_video(run_id: str):
    """
    Approves the video and marks pipeline as Completed.
    """
    client = get_supabase_client()
    print(f"[Approval Service] Approving Video for Run {run_id}...")
    
    # Note: Phase 1 db has videos table, we could add approval_status there if needed, 
    # but updating the run is sufficient for Kanban state.
    client.table("runs").update({"kanban_state": "Completed"}).eq("id", run_id).execute()
    
    return True
