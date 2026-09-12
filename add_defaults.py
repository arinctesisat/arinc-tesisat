import sqlite3

def add_default_services():
    conn = sqlite3.connect('kurumsal_vFinal.db')
    c = conn.cursor()
    
    # Varsayılan Hizmetler
    services = [
        ('Su Kaçağı Tespiti', 'Akustik dinleme cihazları ve termal kameralar ile kırmadan su kaçağı tespiti yapıyoruz.', 'fa-water'),
        ('Tıkanıklık Açma', 'Robot cihazlar ile pimaş, mutfak ve banyo tıkanıklıklarını kırmadan açıyoruz.', 'fa-sink'),
        ('Petek Temizliği', 'Isınma sorunlarınızı gidermek için peteklerinizi ilaçlı ve makineli sistemle temizliyoruz.', 'fa-fire-extinguisher'),
        ('Sıhhi Tesisat', 'Musluk tamiri, batarya değişimi ve tüm sıhhi tesisat yenileme işlerinizde yanınızdayız.', 'fa-tools')
    ]
    
    for name, desc, icon in services:
        c.execute("INSERT INTO services (name, desc, icon) VALUES (?, ?, ?)", (name, desc, icon))
        
    conn.commit()
    conn.close()
    print("Added default services.")

if __name__ == '__main__':
    add_default_services()
