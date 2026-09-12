import os
import re

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add imports
imports = '''import os, sqlite3, functools, uuid, secrets
import psycopg2
from psycopg2.extras import DictCursor
import cloudinary
import cloudinary.uploader
'''
code = code.replace('import os, sqlite3, functools, uuid, secrets', imports)

# 2. Cloudinary config
cloud_conf = '''
app = Flask(__name__)

# Cloudinary Setup
if os.environ.get('CLOUDINARY_URL'):
    import cloudinary
    # Cloudinary parses the CLOUDINARY_URL environment variable automatically
'''
code = code.replace('app = Flask(__name__)', cloud_conf)

# 3. DbWrapper and get_db
db_wrapper = '''class DbWrapper:
    def __init__(self, conn_str):
        self.conn = psycopg2.connect(conn_str)
        self.conn.autocommit = True

    def execute(self, query, params=()):
        pg_query = query.replace('?', '%s')
        cur = self.conn.cursor(cursor_factory=DictCursor)
        cur.execute(pg_query, params)
        return cur

    def executemany(self, query, params_list):
        pg_query = query.replace('?', '%s')
        cur = self.conn.cursor()
        cur.executemany(pg_query, params_list)
        return cur

    def commit(self):
        pass

    def close(self):
        self.conn.close()

# Veritabanı Bağlantısı
def get_db():
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        return DbWrapper(db_url)
    conn = sqlite3.connect('kurumsal_vFinal.db')
    conn.row_factory = sqlite3.Row
    return conn
'''
code = re.sub(r'# Veritabanı Bağlantısı\s*def get_db\(\):.*?return conn\s+', db_wrapper + '\n', code, flags=re.DOTALL)

# 4. init_db fix for PostgreSQL
init_db_func = '''def init_db():
    if not os.path.exists(app.config['UPLOAD_FOLDER']): os.makedirs(app.config['UPLOAD_FOLDER'])
    db = get_db()
    is_pg = os.environ.get('DATABASE_URL') is not None
    pk_type = 'SERIAL PRIMARY KEY' if is_pg else 'INTEGER PRIMARY KEY'
    
    db.execute(f\'\'\'CREATE TABLE IF NOT EXISTS settings (
        id {pk_type}, title TEXT, phone TEXT, whatsapp TEXT, about TEXT, address TEXT, email TEXT, 
        color_primary TEXT DEFAULT "#001d3d", color_secondary TEXT DEFAULT "#ffc300", 
        hero_title TEXT, hero_subtitle TEXT, hero_img TEXT, 
        about_img TEXT, about_hero_img TEXT, footer_text TEXT,
        meta_desc TEXT, meta_keys TEXT,
        stat1_title TEXT DEFAULT "Yıllık Tecrübe", stat1_value TEXT DEFAULT "21+",
        stat2_title TEXT DEFAULT "Profesyonel Ekip", stat2_value TEXT DEFAULT "12+",
        stat3_title TEXT DEFAULT "Mutlu Müşteri", stat3_value TEXT DEFAULT "5000+",
        stat4_title TEXT DEFAULT "Şehir Dışı Hizmet", stat4_value TEXT DEFAULT "15+",
        logo TEXT, popup_img TEXT, popup_link TEXT, popup_active INTEGER DEFAULT 0,
        about_text2 TEXT, vision_text TEXT, mission_text TEXT, values_text TEXT,
        gallery_hero_img TEXT, gallery_hero_text TEXT,
        services_hero_img TEXT, services_hero_text TEXT,
        contact_hero_img TEXT, contact_hero_text TEXT,
        h_badge TEXT, h_btn1 TEXT, h_btn2 TEXT,
        s_title TEXT, s_subtitle TEXT,
        cta_title TEXT, cta_subtitle TEXT, cta_btn TEXT,
        t_title TEXT, f_title TEXT,
        about_title TEXT, about_subtitle TEXT,
        gallery_title TEXT, contact_title TEXT, contact_subtitle TEXT,
        instagram TEXT, facebook TEXT, linkedin TEXT,
        city TEXT, district TEXT, map_embed TEXT, site_url TEXT, business_type TEXT DEFAULT "Plumber",
        seo_home_title TEXT, seo_home_desc TEXT, seo_home_keys TEXT,
        seo_about_title TEXT, seo_about_desc TEXT, seo_about_keys TEXT,
        seo_services_title TEXT, seo_services_desc TEXT, seo_services_keys TEXT,
        seo_gallery_title TEXT, seo_gallery_desc TEXT, seo_gallery_keys TEXT,
        seo_contact_title TEXT, seo_contact_desc TEXT, seo_contact_keys TEXT
    )\'\'\')
    db.execute(f'CREATE TABLE IF NOT EXISTS faq (id {pk_type}, question TEXT, answer TEXT)')
    db.execute(f'CREATE TABLE IF NOT EXISTS services (id {pk_type}, name TEXT, desc TEXT, icon TEXT, img TEXT, video TEXT)')
    db.execute(f'CREATE TABLE IF NOT EXISTS gallery (id {pk_type}, img TEXT, title TEXT, desc TEXT)')
    db.execute(f'CREATE TABLE IF NOT EXISTS videos (id {pk_type}, vid_path TEXT, title TEXT, desc TEXT)')
    db.execute(f'CREATE TABLE IF NOT EXISTS messages (id {pk_type}, name TEXT, phone TEXT, service TEXT, msg TEXT, is_read INTEGER DEFAULT 0, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    db.execute(f'CREATE TABLE IF NOT EXISTS logs (id {pk_type}, action TEXT, "user" TEXT, ip TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    db.execute(f'CREATE TABLE IF NOT EXISTS testimonials (id {pk_type}, name TEXT, content TEXT, stars INTEGER)')
    db.execute(f'CREATE TABLE IF NOT EXISTS timeline (id {pk_type}, year TEXT, title TEXT, content TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS admin ("user" TEXT PRIMARY KEY, pass TEXT)')
'''
code = re.sub(r'def init_db\(\):.*?db\.execute\(\'CREATE TABLE IF NOT EXISTS admin \("user" TEXT PRIMARY KEY, pass TEXT\)\'\)', init_db_func, code, flags=re.DOTALL)

# 5. Fix file uploads (save function wrapper)
upload_fix = '''def save_file(f, filename):
    if os.environ.get('CLOUDINARY_URL'):
        res = cloudinary.uploader.upload(f, public_id=filename.split('.')[0])
        return res['secure_url']
    else:
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename

def delete_file(filename):
    if not filename: return
    if os.environ.get('CLOUDINARY_URL') and filename.startswith('http'):
        # Extract public_id from url
        public_id = filename.split('/')[-1].split('.')[0]
        try: cloudinary.uploader.destroy(public_id)
        except: pass
    else:
        secure_name = os.path.basename(filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
        if os.path.exists(path):
            try: os.remove(path)
            except: pass
'''
code = re.sub(r'def delete_file\(filename\):.*?except: pass', upload_fix, code, flags=re.DOTALL)

# Replace f.save with save_file
code = code.replace('f.save(os.path.join(app.config[\'UPLOAD_FOLDER\'], fn))', 'fn = save_file(f, fn)')
code = code.replace('f.save(os.path.join(app.config[\'UPLOAD_FOLDER\'], vn))', 'vn = save_file(f, vn)')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Refactoring complete')
