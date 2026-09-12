import sqlite3
import os

db_path = 'c:/Users/MUHAMMED ASAF BUDAK/Desktop/tesisat/tesisat/kurumsal_vFinal.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT popup_img FROM settings WHERE id=1').fetchone()
    if row:
        print(f"POPUP_IMG: {row['popup_img']}")
    conn.close()
else:
    print("DB not found")
