import sqlite3
import os

db_path = 'c:/Users/MUHAMMED ASAF BUDAK/Desktop/tesisat/tesisat/kurumsal_vFinal.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    # Hatalı/broken resimleri temizle
    broken_imgs = ['Ekran_goruntusu_2025-07-17_214953.png', 'Ekran_goruntusu_2025-07-17_221422.png', 'Ekran_goruntusu_2025-09-21_180211.png']
    for img in broken_imgs:
        conn.execute('UPDATE services SET img = NULL WHERE img = ?', (img,))
        conn.execute('UPDATE settings SET popup_img = NULL WHERE popup_img = ?', (img,))
        conn.execute('UPDATE settings SET logo = NULL WHERE logo = ?', (img,))
    conn.commit()
    conn.close()
    print("Broken image references cleaned.")
else:
    print("DB not found")
