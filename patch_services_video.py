import sqlite3
db_path = 'c:/Users/MUHAMMED ASAF BUDAK/Desktop/tesisat/tesisat/kurumsal_vFinal.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE services ADD COLUMN video TEXT")
    print("Added video column to services table.")
except sqlite3.OperationalError:
    print("Video column already exists or error.")
conn.commit()
conn.close()
