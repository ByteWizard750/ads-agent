import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client, Client
from src.config import settings

load_dotenv()


def get_supabase_client() -> Optional[Client]:
    url = os.getenv("SUPABASE_URL") or settings.supabase_url
    key = os.getenv("SUPABASE_KEY") or settings.supabase_key
    if not url or not key or "your-supabase" in key:
        return None
    return create_client(url, key)


def ensure_client_exists(client_id: str, name: str, niche: str, config_path: str):
    client = get_supabase_client()
    if not client:
        return
    client.table("clients").upsert(
        {
            "id": client_id,
            "name": name,
            "niche": niche,
            "config_path": config_path,
            "is_active": True,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    ).execute()


def create_run_record(client_id: str, client_name: str = "CrowdWisdomTrading", niche: str = "trading_and_fintech_education", config_path: str = "clients/crowdwisdom/config.yaml") -> str:
    ensure_client_exists(client_id, client_name, niche, config_path)
    client = get_supabase_client()
    if not client:
        import uuid
        return str(uuid.uuid4())
    
    res = client.table("runs").insert(
        {
            "client_id": client_id,
            "status": "running",
            "metadata": {"source": "research_agent_run"},
        }
    ).execute()
    
    if res.data:
        return res.data[0]["id"]
    import uuid
    return str(uuid.uuid4())


def update_kanban_state(
    client_id: str,
    run_id: str,
    state_name: str,
    script_id: Optional[str] = None,
    history: Optional[List[Dict[str, Any]]] = None
):
    client = get_supabase_client()
    if not client:
        print(f"[LOCAL KANBAN STATE UPDATE] Client '{client_id}' -> '{state_name}'")
        return

    payload = {
        "client_id": client_id,
        "run_id": run_id,
        "current_state": state_name,
        "history": history or [],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if script_id:
        payload["script_id"] = script_id

    client.table("kanban_state").insert(payload).execute()


def insert_ads(ads_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    client = get_supabase_client()
    if not client or not ads_data:
        return ads_data
    
    res = client.table("ads").insert(ads_data).execute()
    return res.data or []


def insert_concepts(concepts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    client = get_supabase_client()
    if not client or not concepts_data:
        return concepts_data

    res = client.table("concepts").insert(concepts_data).execute()
    return res.data or []
