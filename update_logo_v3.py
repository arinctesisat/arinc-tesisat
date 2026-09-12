import sqlite3

def update_logo():
    conn = sqlite3.connect('kurumsal_vFinal.db')
    cursor = conn.cursor()
    new_logo = 'Yıltek Mühendislik ve Yapı Market_logo_v3.png'
    cursor.execute('UPDATE settings SET logo = ? WHERE id = 1', (new_logo,))
    conn.commit()
    conn.close()
    print("Logo updated to Yıltek Mühendislik ve Yapı Market_logo_v3.png successfully.")

if __name__ == "__main__":
    update_logo()
