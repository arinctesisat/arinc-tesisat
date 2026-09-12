import sqlite3
import os

db_path = 'c:/Users/MUHAMMED ASAF BUDAK/Desktop/tesisat/tesisat/kurumsal_vFinal.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT id, name, img FROM services').fetchall()
    for row in rows:
        print(f"ID: {row['id']}, NAME: {row['name']}, IMG: |{row['img']}|")
    conn.close()
else:
    print("DB not found")
