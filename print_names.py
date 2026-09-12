import sqlite3
db_path = 'c:/Users/MUHAMMED ASAF BUDAK/Desktop/tesisat/tesisat/kurumsal_vFinal.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
for table in ['services', 'settings']:
    print(f"--- {table} ---")
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [col[1] for col in cursor.fetchall()]
    print(", ".join(cols))
conn.close()
