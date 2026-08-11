import os
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
from src.db.supabase import get_supabase_client

def test_openrouter():
    print("\n--- 1. FRESH OPENROUTER API TEST ---")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_key
    )
    res = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[{"role": "user", "content": "Return JSON: {\"status\": \"live\", \"service\": \"openrouter\"}"}],
        temperature=0.0,
        max_tokens=100
    )
    print(f"OpenRouter Model Used: {res.model}")
    print(f"OpenRouter Raw Choice Response: {res.choices[0].message.content}")
    print(f"OpenRouter Full Response Object ID: {res.id}")

def test_supabase_roundtrip():
    print("\n--- 2. FRESH SUPABASE ROUND-TRIP TEST ---")
    client = get_supabase_client()
    
    # Fetch valid run_id from runs table
    runs_res = client.table("runs").select("id").limit(1).execute()
    test_run_id = runs_res.data[0]["id"]
    
    # Write test row
    insert_res = client.table("cost_logs").insert({
        "client_id": "crowdwisdom",
        "run_id": test_run_id,
        "agent_name": "audit_agent",
        "provider": "openrouter",
        "model_or_service": "google/gemini-2.5-flash",
        "estimated_cost_usd": 0.001
    }).execute()
    
    written_row = insert_res.data[0]
    print(f"Fresh Write Success | Inserted Row ID: {written_row['id']} | Agent: {written_row['agent_name']}")
    
    # Read back test row
    read_res = client.table("cost_logs").select("*").eq("id", written_row['id']).execute()
    read_row = read_res.data[0]
    print(f"Fresh Read Success  | Retrieved Row ID: {read_row['id']} | Estimated Cost USD: {read_row['estimated_cost_usd']}")

if __name__ == "__main__":
    test_openrouter()
    test_supabase_roundtrip()
