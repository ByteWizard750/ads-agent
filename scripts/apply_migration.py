import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings

def apply_migration():
    db_url = os.getenv("SUPABASE_DB_URL") or settings.supabase_db_url
    if not db_url or "YOUR-PASSWORD" in db_url:
        print("[ERROR] SUPABASE_DB_URL is missing or contains template placeholder.")
        print("Please set SUPABASE_DB_URL in .env or run 20260731000000_init_schema.sql directly in the Supabase Dashboard SQL Editor.")
        sys.exit(1)

    import psycopg2
    migration_file = Path(__file__).parent.parent / "supabase" / "migrations" / "20260731000000_init_schema.sql"
    sql = migration_file.read_text(encoding="utf-8")

    print(f"Connecting to database...")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    print("Executing 20260731000000_init_schema.sql...")
    cur.execute(sql)
    print("Migration executed successfully!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    apply_migration()
