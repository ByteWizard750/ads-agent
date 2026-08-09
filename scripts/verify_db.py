import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings

EXPECTED_TABLES = [
    "clients",
    "runs",
    "ads",
    "concepts",
    "scripts",
    "videos",
    "kanban_state",
    "cost_logs",
]

def verify_tables():
    db_url = os.getenv("SUPABASE_DB_URL") or settings.supabase_db_url
    
    # If SUPABASE_DB_URL is available, use psycopg2 direct DB check
    if db_url and "YOUR-PASSWORD" not in db_url:
        import psycopg2
        print(f"Connecting to Postgres to verify tables...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        existing_tables = set(row[0] for row in cur.fetchall())
        
        cur.execute("""
            SELECT enumlabel 
            FROM pg_enum 
            JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
            WHERE pg_type.typname = 'kanban_status';
        """)
        kanban_enum_values = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        print("\n--- Live Postgres Database Status ---")
        print(f"Found Tables in public schema: {sorted(list(existing_tables))}")
        print(f"Kanban Enum Values: {kanban_enum_values}")
        
        missing = set(EXPECTED_TABLES) - existing_tables
        if missing:
            print(f"[FAIL] Missing expected tables: {missing}")
            sys.exit(1)
        else:
            print("[SUCCESS] All 8 required tables exist in live database!")
            return

    # Fallback to Supabase REST client if DB_URL not provided but SUPABASE_URL & KEY are set
    supabase_url = os.getenv("SUPABASE_URL") or settings.supabase_url
    supabase_key = os.getenv("SUPABASE_KEY") or settings.supabase_key

    if supabase_url and supabase_key:
        from supabase import create_client
        client = create_client(supabase_url, supabase_key)
        print("\n--- Verifying Tables via Supabase REST API ---")
        verified = []
        failed = []
        for tbl in EXPECTED_TABLES:
            try:
                # Query limit 0 to check table existence
                res = client.table(tbl).select("*").limit(0).execute()
                verified.append(tbl)
                print(f"  ✓ Table '{tbl}' verified.")
            except Exception as e:
                failed.append((tbl, str(e)))
                print(f"  ✗ Table '{tbl}' failed: {e}")
        
        if failed:
            print(f"\n[FAIL] {len(failed)} tables failed verification.")
            sys.exit(1)
        else:
            print("\n[SUCCESS] All 8 required tables exist and are accessible in live Supabase instance!")
            return

    print("[ERROR] Neither SUPABASE_DB_URL nor (SUPABASE_URL + SUPABASE_KEY) are set in .env.")
    sys.exit(1)

if __name__ == "__main__":
    verify_tables()
