import sqlite3

def patch_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Settings Tablosu Eksik Kolonlar
    settings_cols = [
        ('title', 'TEXT'), ('whatsapp', 'TEXT'), ('address', 'TEXT'),
        ('color_primary', 'TEXT'), ('color_secondary', 'TEXT'),
        ('hero_title', 'TEXT'), ('hero_subtitle', 'TEXT'), ('h_badge', 'TEXT'),
        ('h_btn1', 'TEXT'), ('h_btn2', 'TEXT'),
        ('about', 'TEXT'), ('about_text2', 'TEXT'), ('about_title', 'TEXT'), ('about_subtitle', 'TEXT'),
        ('vision_text', 'TEXT'), ('mission_text', 'TEXT'), ('values_text', 'TEXT'),
        ('s_title', 'TEXT'), ('s_subtitle', 'TEXT'),
        ('cta_title', 'TEXT'), ('cta_subtitle', 'TEXT'), ('cta_btn', 'TEXT'),
        ('t_title', 'TEXT'), ('f_title', 'TEXT'),
        ('gallery_title', 'TEXT'), ('gallery_hero_text', 'TEXT'),
        ('contact_title', 'TEXT'), ('contact_subtitle', 'TEXT'), ('contact_hero_text', 'TEXT'),
        ('meta_desc', 'TEXT'), ('meta_keys', 'TEXT'), ('footer_text', 'TEXT'),
        ('stat1_title', 'TEXT'), ('stat1_value', 'TEXT'),
        ('stat2_title', 'TEXT'), ('stat2_value', 'TEXT'),
        ('stat3_title', 'TEXT'), ('stat3_value', 'TEXT'),
        ('stat4_title', 'TEXT'), ('stat4_value', 'TEXT'),
        ('popup_link', 'TEXT'), ('popup_active', 'INTEGER DEFAULT 0'),
        ('popup_img', 'TEXT'), ('hero_img', 'TEXT'), ('logo', 'TEXT'),
        ('about_hero_img', 'TEXT'), ('about_img', 'TEXT'),
        ('services_hero_img', 'TEXT'), ('gallery_hero_img', 'TEXT'), ('contact_hero_img', 'TEXT'),
        ('instagram', 'TEXT'), ('facebook', 'TEXT'), ('linkedin', 'TEXT'),
        ('city', 'TEXT'), ('district', 'TEXT'), ('site_url', 'TEXT'), ('map_embed', 'TEXT'),
        ('business_type', 'TEXT DEFAULT "Plumber"'),
        ('seo_home_title', 'TEXT'), ('seo_home_desc', 'TEXT'), ('seo_home_keys', 'TEXT'),
        ('seo_about_title', 'TEXT'), ('seo_about_desc', 'TEXT'), ('seo_about_keys', 'TEXT'),
        ('seo_services_title', 'TEXT'), ('seo_services_desc', 'TEXT'), ('seo_services_keys', 'TEXT'),
        ('seo_gallery_title', 'TEXT'), ('seo_gallery_desc', 'TEXT'), ('seo_gallery_keys', 'TEXT'),
        ('seo_contact_title', 'TEXT'), ('seo_contact_desc', 'TEXT'), ('seo_contact_keys', 'TEXT')
    ]
    
    for col_name, col_type in settings_cols:
        try:
            c.execute(f"ALTER TABLE settings ADD COLUMN {col_name} {col_type}")
            print(f"Added {col_name} to settings")
        except sqlite3.OperationalError:
            pass # Already exists
            
    # Services Tablosu Eksik Kolonlar
    services_cols = [
        ('img', 'TEXT')
    ]
    for col_name, col_type in services_cols:
        try:
            c.execute(f"ALTER TABLE services ADD COLUMN {col_name} {col_type}")
            print(f"Added {col_name} to services")
        except sqlite3.OperationalError:
            pass
            
    # Messages Tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        name TEXT,
        phone TEXT,
        service TEXT,
        msg TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_read INTEGER DEFAULT 0
    )''')
    
    # FAQ Tablosu
    c.execute('CREATE TABLE IF NOT EXISTS faq (id INTEGER PRIMARY KEY, question TEXT, answer TEXT)')
    
    # Timeline
    c.execute('CREATE TABLE IF NOT EXISTS timeline (id INTEGER PRIMARY KEY, year TEXT, title TEXT, content TEXT)')

    # Videos
    c.execute('CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY, title TEXT, vid_path TEXT, desc TEXT)')

    conn.commit()
    conn.close()
    print("Patch complete.")

if __name__ == '__main__':
    patch_db()
