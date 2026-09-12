import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Site Ayarları Tablosu (Telefon, Hakkımızda vs.)
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    phone TEXT,
                    email TEXT,
                    about_text TEXT
                )''')

    # Hizmetler Tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    icon TEXT
                )''')

    # Galeri Tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS gallery (
                    id INTEGER PRIMARY KEY,
                    filename TEXT
                )''')

    # Admin Kullanıcıları Tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    password TEXT
                )''')

    # Varsayılan Verileri Ekle (Eğer boşsa)
    c.execute('SELECT count(*) FROM settings')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO settings (phone, email, about_text) VALUES (?, ?, ?)",
                  ("0536 491 58 91", "info@tesisat.com", "15 yıllık tecrübemizle hizmetinizdeyiz."))
        
        # Varsayılan Admin (Kullanıcı: admin, Şifre: 1234)
        hashed_pw = generate_password_hash("1234")
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", hashed_pw))
        
        # Örnek Hizmetler
        c.execute("INSERT INTO services (title, description, icon) VALUES (?, ?, ?)", ("Su Kaçağı", "Kırmadan tespit.", "fa-search"))
        c.execute("INSERT INTO services (title, description, icon) VALUES (?, ?, ?)", ("Montaj", "Musluk batarya montajı.", "fa-tools"))

    conn.commit()
    conn.close()
    print("Veritabanı ve tablolar başarıyla oluşturuldu!")

if __name__ == '__main__':
    init_db()