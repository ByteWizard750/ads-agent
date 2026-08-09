import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.supabase import get_supabase_client

def audit_supabase_tables():
    client = get_supabase_client()
    tables = ["clients", "runs", "ads", "concepts", "scripts", "videos", "kanban_state", "cost_logs"]
    
    print("=== ITEM 1: SUPABASE LIVE TABLES AUDIT ===")
    for table in tables:
        try:
            res = client.table(table).select("*").limit(1).execute()
            print(f"Table: '{table}' | Access Status: EXISTS & ACCESSIBLE | Sample Row Fetched: {len(res.data) > 0}")
        except Exception as e:
            print(f"Table: '{table}' | Access Status: ERROR ({e})")

if __name__ == "__main__":
    audit_supabase_tables()
