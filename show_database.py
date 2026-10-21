import sqlite3
import os

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

def format_grid_table(headers, rows, max_col_width=25):
    if not headers:
        return ""
    
    # Format each cell
    str_rows = []
    for r in rows:
        formatted_row = []
        for val in r:
            if val is None:
                s = "NULL"
            else:
                s = str(val).replace("\n", " ").strip()
                s = s.encode('ascii', 'ignore').decode('ascii')
                if len(s) > max_col_width:
                    s = s[:max_col_width - 3] + "..."
            formatted_row.append(s)
        str_rows.append(formatted_row)

    # Compute column widths
    col_widths = [len(h) for h in headers]
    for r in str_rows:
        for i, val in enumerate(r):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(val))

    # Build ASCII grid
    sep_line = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_line = "|" + "|".join(f" {h.ljust(col_widths[i])} " for i, h in enumerate(headers)) + "|"
    
    lines = [sep_line, header_line, sep_line]
    for r in str_rows:
        row_line = "|" + "|".join(f" {r[i].ljust(col_widths[i])} " if i < len(r) else f" {' '.ljust(col_widths[i])} " for i in range(len(headers))) + "|"
        lines.append(row_line)
    lines.append(sep_line)
    return "\n".join(lines)

def display_table_contents():
    if not DB_PATH or not os.path.exists(DB_PATH):
        print(f"Error: Database file nexus.db not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*85)
    print("                NEXUS 3NF RELATIONAL DATABASE INSPECTOR")
    print("="*85)

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cursor.fetchall() if not r[0].startswith("sqlite_")]

    print(f"\nTotal Registered Tables: {len(tables)}\n")

    for idx, table in enumerate(tables, 1):
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        row_count = cursor.fetchone()[0]

        cursor.execute(f"PRAGMA table_info({table});")
        columns = [col[1] for col in cursor.fetchall()]

        print(f"[{idx}] TABLE: {table}  |  Total Rows: {row_count}")

        cursor.execute(f"SELECT * FROM {table} LIMIT 4;")
        rows = cursor.fetchall()
        if rows:
            print(format_grid_table(columns, rows))
        else:
            print("      (Table is currently empty / Awaiting records)")
        print()

    conn.close()

if __name__ == "__main__":
    display_table_contents()

