import sqlite3
db_path = 'c:/Users/MUHAMMED ASAF BUDAK/Desktop/tesisat/tesisat/database.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(settings)")
for col in cursor.fetchall():
    print(col)
conn.close()
