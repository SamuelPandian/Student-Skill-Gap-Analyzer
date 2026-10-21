import sqlite3
import os

# Locate nexus.db in backend or current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
possible_paths = [
    os.path.join(current_dir, "nexus.db"),
    os.path.join(current_dir, "backend", "nexus.db"),
    os.path.join(os.path.dirname(current_dir), "backend", "nexus.db")
]

DB_PATH = None
for p in possible_paths:
    if os.path.exists(p):
        DB_PATH = p
        break

def display_table_contents():
    if not DB_PATH or not os.path.exists(DB_PATH):
        print(f"Error: Database file nexus.db not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("                NEXUS RELATIONAL DATABASE INSPECTOR (3NF)")
    print("="*80)

    # 1. List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cursor.fetchall() if not r[0].startswith("sqlite_")]

    print(f"\nTotal Registered Tables: {len(tables)}\n")

    for idx, table in enumerate(tables, 1):
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        row_count = cursor.fetchone()[0]

        cursor.execute(f"PRAGMA table_info({table});")
        columns = [col[1] for col in cursor.fetchall()]

        print(f"[{idx}] TABLE: {table} ({row_count} rows)")
        print(f"    Schema Columns: {', '.join(columns)}")

        # Print top 3 sample rows
        cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
        rows = cursor.fetchall()
        if rows:
            print("    Sample Records:")
            for r in rows:
                safe_row = tuple(
                    str(val).encode('ascii', 'ignore').decode('ascii')[:40] + ("..." if len(str(val)) > 40 else "")
                    for val in r
                )
                print(f"      -> {safe_row}")
        else:
            print("      -> (Empty / Awaiting new transactions)")
        print("-" * 80)

    conn.close()

if __name__ == "__main__":
    display_table_contents()
