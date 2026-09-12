import os, sqlite3, functools, uuid, secrets
import psycopg2
from psycopg2.extras import DictCursor
import cloudinary
import cloudinary.uploader

from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, abort, send_file, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv() # .env dosyasını yükle

IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'


app = Flask(__name__)

# Cloudinary Setup
if os.environ.get('CLOUDINARY_URL'):
    import cloudinary
    # Cloudinary parses the CLOUDINARY_URL environment variable automatically

app.secret_key = os.environ.get('SECRET_KEY', 'harun_ultra_pro_2026_secure_key_8822')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'webp', 'ico'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Güvenlik Konfigürasyonları
csrf = CSRFProtect(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Content Security Policy (CSP)
csp = {
    'default-src': ['\'self\''],
    'script-src': [
        '\'self\'',
        'https://cdn.tailwindcss.com',
        'https://unpkg.com',
        'https://cdn.jsdelivr.net',
        'https://kit.fontawesome.com',
        '\'unsafe-inline\'',
        '\'unsafe-eval\''
    ],
    'style-src': [
        '\'self\'',
        'https://fonts.googleapis.com',
        'https://cdn.jsdelivr.net',
        'https://cdnjs.cloudflare.com',
        '\'unsafe-inline\''
    ],
    'font-src': [
        '\'self\'',
        'https://fonts.gstatic.com',
        'https://cdnjs.cloudflare.com',
        'https://ka-f.fontawesome.com'
    ],
    'img-src': ['\'self\'', 'data:', 'https://images.unsplash.com', 'https://*.google.com', 'https://*.gstatic.com', 'https://*.mirror-media.xyz'],
    'frame-src': ['\'self\'', 'https://www.google.com', 'https://www.youtube.com', 'https://*.google.com'],
    'connect-src': ['\'self\'', 'https://cdn.jsdelivr.net', 'https://ka-f.fontawesome.com', 'https://cdn.tailwindcss.com', 'https://*.google.com', 'https://unpkg.com']
}


Talisman(app, content_security_policy=csp, force_https=IS_PRODUCTION, strict_transport_security=IS_PRODUCTION) # Localde False, Canlıda True

# Session Güvenliği
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=IS_PRODUCTION,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600 # 1 saat
)

def log_action(action):
    try:
        db = get_db()
        db.execute('INSERT INTO logs (action, username, ip) VALUES (?, ?, ?)', 
                   (action, session.get('user', 'admin') if session.get('admin') else 'guest', request.remote_addr))
        db.commit()
    except: pass

def validate_password(password):
    # En az 8 karakter, bir büyük harf, bir küçük harf ve bir rakam
    if len(password) < 8: return False
    if not any(c.isupper() for c in password): return False
    if not any(c.islower() for c in password): return False
    if not any(c.isdigit() for c in password): return False
    return True

def save_file(f, filename):
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



def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

class DbWrapper:
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

# Veritabanı Kurulumu
def init_db():
    if not os.path.exists(app.config['UPLOAD_FOLDER']): os.makedirs(app.config['UPLOAD_FOLDER'])
    db = get_db()
    is_pg = os.environ.get('DATABASE_URL') is not None
    pk_type = 'SERIAL PRIMARY KEY' if is_pg else 'INTEGER PRIMARY KEY'
    
    db.execute(f'''CREATE TABLE IF NOT EXISTS settings (
        id {pk_type}, title TEXT, phone TEXT, whatsapp TEXT, about TEXT, address TEXT, email TEXT, 
        color_primary TEXT DEFAULT '#001d3d', color_secondary TEXT DEFAULT '#ffc300', 
        hero_title TEXT, hero_subtitle TEXT, hero_img TEXT, 
        about_img TEXT, about_hero_img TEXT, footer_text TEXT,
        meta_desc TEXT, meta_keys TEXT,
        stat1_title TEXT DEFAULT 'Yıllık Tecrübe', stat1_value TEXT DEFAULT '21+',
        stat2_title TEXT DEFAULT 'Profesyonel Ekip', stat2_value TEXT DEFAULT '12+',
        stat3_title TEXT DEFAULT 'Mutlu Müşteri', stat3_value TEXT DEFAULT '5000+',
        stat4_title TEXT DEFAULT 'Şehir Dışı Hizmet', stat4_value TEXT DEFAULT '15+',
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
        city TEXT, district TEXT, map_embed TEXT, site_url TEXT, business_type TEXT DEFAULT 'Plumber',
        seo_home_title TEXT, seo_home_desc TEXT, seo_home_keys TEXT,
        seo_about_title TEXT, seo_about_desc TEXT, seo_about_keys TEXT,
        seo_services_title TEXT, seo_services_desc TEXT, seo_services_keys TEXT,
        seo_gallery_title TEXT, seo_gallery_desc TEXT, seo_gallery_keys TEXT,
        seo_contact_title TEXT, seo_contact_desc TEXT, seo_contact_keys TEXT
    )''')
    db.execute(f'CREATE TABLE IF NOT EXISTS faq (id {pk_type}, question TEXT, answer TEXT)')
    db.execute(f'CREATE TABLE IF NOT EXISTS services (id {pk_type}, name TEXT, "desc" TEXT, icon TEXT, img TEXT, video TEXT)')
    db.execute(f'CREATE TABLE IF NOT EXISTS gallery (id {pk_type}, img TEXT, title TEXT, "desc" TEXT)')
    db.execute(f'CREATE TABLE IF NOT EXISTS videos (id {pk_type}, vid_path TEXT, title TEXT, "desc" TEXT)')
    db.execute(f'CREATE TABLE IF NOT EXISTS messages (id {pk_type}, name TEXT, phone TEXT, service TEXT, msg TEXT, is_read INTEGER DEFAULT 0, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    db.execute(f'CREATE TABLE IF NOT EXISTS logs (id {pk_type}, action TEXT, username TEXT, ip TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    db.execute(f'CREATE TABLE IF NOT EXISTS testimonials (id {pk_type}, name TEXT, content TEXT, stars INTEGER)')
    db.execute(f'CREATE TABLE IF NOT EXISTS timeline (id {pk_type}, year TEXT, title TEXT, content TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS admin (username TEXT PRIMARY KEY, pass TEXT)')

    
    setting_row = db.execute('SELECT * FROM settings WHERE id=1').fetchone()
    if not setting_row or not setting_row['logo']:
        if setting_row:
            db.execute('DELETE FROM settings WHERE id=1')
            db.execute('DELETE FROM services')
            db.execute('DELETE FROM videos')
        try:
            from seed_data import SETTINGS, SERVICES, VIDEOS
            
            # Insert settings
            cols = ', '.join(SETTINGS.keys())
            placeholders = ', '.join(['?'] * len(SETTINGS))
            db.execute(f"INSERT INTO settings ({cols}) VALUES ({placeholders})", tuple(SETTINGS.values()))
            
            # Insert services
            for s in SERVICES:
                cols = ', '.join([f'"{k}"' if k=='desc' else k for k in s.keys()])
                placeholders = ', '.join(['?'] * len(s))
                db.execute(f"INSERT INTO services ({cols}) VALUES ({placeholders})", tuple(s.values()))
                
            # Insert videos
            for v in VIDEOS:
                cols = ', '.join([f'"{k}"' if k=='desc' else k for k in v.keys()])
                placeholders = ', '.join(['?'] * len(v))
                db.execute(f"INSERT INTO videos ({cols}) VALUES ({placeholders})", tuple(v.values()))
                
        except Exception as e:
            print(f"Seed error: {e}")
            db.execute("INSERT INTO settings (id, title, phone, whatsapp, about, address, email) VALUES (1, 'Silivri Su Kaçağı Tespit', '0536 491 5891', '905364915891', 'Profesyonel hizmet...', 'Silivri', 'iletisim@site.com')")
    
    # Varsayılan FAQ'lar (Eğer boşsa)
    if not db.execute('SELECT * FROM faq').fetchone():
        faqs = [
          ('Su kaçağı tespiti kırmadan yapılıyor mu?', 'Evet, son teknoloji termal kameralar ve akustik dinleme cihazları ile sızıntının yerini tek bir seramikte tespit ediyoruz.'),
          ('Servis süreniz nedir?', 'İstanbul genelinde acil durumlarda ortalama 30-45 dakika içinde adresinizde oluyoruz.'),
          ('Yaptığınız işlemler garantili mi?', 'Tüm onarım ve tıkanıklık açma işlemlerimiz firmamızın garanti kapsamı altındadır.'),
          ('Hangi bölgelere hizmet veriyorsunuz?', 'Başta Silivri, Çatalca ve Büyükçekmece olmak üzere tüm İstanbul ve Trakya bölgesine hizmet sunuyoruz.')
        ]
        db.executemany('INSERT INTO faq (question, answer) VALUES (?, ?)', faqs)
    
    if not db.execute('SELECT * FROM admin WHERE username=?', ('admin',)).fetchone():
        default_pass = os.environ.get('ADMIN_PASSWORD')
        if not default_pass:
            default_pass = secrets.token_urlsafe(12)
            print(f"\n\n=======================================================")
            print(f"!!! GÜVENLİK UYARISI: Admin kullanıcısı oluşturuldu !!!")
            print(f"Kullanıcı: admin")
            print(f"Şifre: {default_pass}")
            print(f"Lütfen bu şifreyi kaydedin. (Daha sonra panelden değiştirebilirsiniz)")
            print(f"=======================================================\n\n")
        db.execute("INSERT INTO admin VALUES ('admin', ?)", (generate_password_hash(default_pass),))
    db.commit()
    db.close()

init_db()

@app.context_processor
def inject_data():
    db = get_db()
    s = db.execute('SELECT * FROM settings WHERE id=1').fetchone()
    # Footer için hizmetleri çek
    footer_services = db.execute('SELECT name FROM services LIMIT 4').fetchall()
    return dict(s=s, footer_services=footer_services)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


# --- FRONTEND ROTALARI ---
@app.route('/')
def index():
    db = get_db()
    gallery = db.execute('SELECT * FROM gallery LIMIT 6').fetchall()
    services = db.execute('SELECT * FROM services').fetchall()
    testimonials = db.execute('SELECT * FROM testimonials').fetchall()
    timeline = db.execute('SELECT * FROM timeline ORDER BY id ASC').fetchall()
    faqs = db.execute('SELECT * FROM faq').fetchall()
    return render_template('index.html', gallery=gallery, services=services, testimonials=testimonials, faqs=faqs, timeline=timeline,
        page_title=None, page_desc=None, page_keys=None, canonical='/')

@app.route('/hakkimizda')
def hakkimizda():
    db = get_db()
    timeline = db.execute('SELECT * FROM timeline ORDER BY id ASC').fetchall()
    return render_template('hakkimizda.html', timeline=timeline,
        page_title='about', page_desc=None, page_keys=None, canonical='/hakkimizda')

@app.route('/hizmetler')
def hizmetler():
    db = get_db()
    services = db.execute('SELECT * FROM services').fetchall()
    return render_template('hizmetler.html', services=services,
        page_title='services', page_desc=None, page_keys=None, canonical='/hizmetler')

@app.route('/galeri')
def galeri():
    db = get_db()
    gallery = db.execute('SELECT * FROM gallery ORDER BY id DESC').fetchall()
    videos = db.execute('SELECT * FROM videos ORDER BY id DESC').fetchall()
    return render_template('galeri.html', gallery=gallery, videos=videos,
        page_title='gallery', page_desc=None, page_keys=None, canonical='/galeri')

@app.route('/iletisim')
def iletisim():
    db = get_db()
    services = db.execute('SELECT * FROM services').fetchall()
    return render_template('iletisim.html', services=services,
        page_title='contact', page_desc=None, page_keys=None, canonical='/iletisim')

# --- sitemap.xml ---
@app.route('/sitemap.xml')
def sitemap():
    db = get_db()
    s = db.execute('SELECT * FROM settings WHERE id=1').fetchone()
    base_url = (s['site_url'] or 'https://example.com').rstrip('/')
    pages = [
        {'loc': base_url + '/', 'priority': '1.0', 'changefreq': 'weekly'},
        {'loc': base_url + '/hakkimizda', 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': base_url + '/hizmetler', 'priority': '0.9', 'changefreq': 'weekly'},
        {'loc': base_url + '/galeri', 'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': base_url + '/iletisim', 'priority': '0.8', 'changefreq': 'monthly'},
    ]
    today = datetime.now().strftime('%Y-%m-%d')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p in pages:
        xml += f'  <url>\n    <loc>{p["loc"]}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>{p["changefreq"]}</changefreq>\n    <priority>{p["priority"]}</priority>\n  </url>\n'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')

# --- robots.txt ---
@app.route('/robots.txt')
def robots():
    db = get_db()
    s = db.execute('SELECT * FROM settings WHERE id=1').fetchone()
    base_url = (s['site_url'] or 'https://example.com').rstrip('/')
    txt = f"User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /panel\nSitemap: {base_url}/sitemap.xml\n"
    return Response(txt, mimetype='text/plain')

# --- YÖNETİM PANELİ ---
@app.route('/admin', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        admin_user = get_db().execute('SELECT * FROM admin WHERE username=?', (request.form['u'],)).fetchone()
        if admin_user and check_password_hash(admin_user['pass'], request.form['p']):
            session.permanent = True
            session['admin'] = True
            session['user'] = admin_user['username']
            log_action("Başarılı giriş yapıldı")
            return redirect('/panel')
        log_action(f"Hatalı giriş denemesi: {request.form['u']}")
        flash('Geçersiz kullanıcı adı veya şifre.', 'danger')

    return render_template('login.html')

@app.route('/panel')
@admin_required
def panel():
    db = get_db()
    
    # İstatistikleri hesapla
    stats = {
        'service_count': db.execute('SELECT COUNT(*) FROM services').fetchone()[0],
        'gallery_count': db.execute('SELECT COUNT(*) FROM gallery').fetchone()[0],
        'message_count': db.execute('SELECT COUNT(*) FROM messages').fetchone()[0],
        'unread_count': db.execute('SELECT COUNT(*) FROM messages WHERE is_read=0').fetchone()[0],
        'testimonial_count': db.execute('SELECT COUNT(*) FROM testimonials').fetchone()[0]
    }
    
    # Verileri çek
    services = db.execute('SELECT * FROM services').fetchall()
    gallery = db.execute('SELECT * FROM gallery ORDER BY id DESC').fetchall()
    videos = db.execute('SELECT * FROM videos ORDER BY id DESC').fetchall()
    messages = db.execute('SELECT * FROM messages ORDER BY id DESC').fetchall()
    testimonials = db.execute('SELECT * FROM testimonials').fetchall()
    faqs = db.execute('SELECT * FROM faq').fetchall()
    timeline = db.execute('SELECT * FROM timeline ORDER BY id ASC').fetchall()
    settings = db.execute('SELECT * FROM settings WHERE id=1').fetchone()
    logs = db.execute('SELECT * FROM logs ORDER BY id DESC LIMIT 50').fetchall()
    
    return render_template('panel.html', 
                           stats=stats, 
                           gallery=gallery, 
                           services=services, 
                           videos=videos,
                           messages=messages,
                           testimonials=testimonials,
                           faqs=faqs,
                           timeline=timeline,
                           settings=settings,
                           logs=logs)


# --- İŞLEMLER ---
@app.route('/add_service', methods=['POST'])
@admin_required
def add_service():
    fn = None
    if 'img' in request.files:
        f = request.files['img']
        if f and f.filename and allowed_file(f.filename):
            fn = secure_filename(f.filename)
            ext = fn.rsplit('.', 1)[1] if '.' in fn else ''
            fn = f"{uuid.uuid4().hex}.{ext}"
            fn = save_file(f, fn)
    
    vn = None
    if 'video' in request.files:
        f = request.files['video']
        if f and f.filename and allowed_file(f.filename):
            vn = secure_filename(f.filename)
            ext = vn.rsplit('.', 1)[1] if '.' in vn else ''
            vn = f"{uuid.uuid4().hex}.{ext}"
            vn = save_file(f, vn)
    
    db = get_db()
    db.execute('INSERT INTO services (name, "desc", icon, img, video) VALUES (?, ?, ?, ?, ?)', 
               (request.form['n'], request.form['d'], request.form['i'], fn, vn))
    db.commit()
    log_action(f"Hizmet eklendi: {request.form['n']}")
    return redirect('/panel')


@app.route('/update_service', methods=['POST'])
@admin_required
def update_service():
    id = request.form['id']
    db = get_db()
    
    if 'img' in request.files:
        f = request.files['img']
        if f and f.filename and allowed_file(f.filename):
            fn = secure_filename(f.filename)
            ext = fn.rsplit('.', 1)[1] if '.' in fn else ''
            fn = f"{uuid.uuid4().hex}.{ext}"
            fn = save_file(f, fn)
            # Eski resmi sil
            old_img = db.execute('SELECT img FROM services WHERE id=?', (id,)).fetchone()
            if old_img and old_img['img']: delete_file(old_img['img'])
            db.execute('UPDATE services SET img=? WHERE id=?', (fn, id))
            
    if 'video' in request.files:
        f = request.files['video']
        if f and f.filename and allowed_file(f.filename):
            vn = secure_filename(f.filename)
            ext = vn.rsplit('.', 1)[1] if '.' in vn else ''
            vn = f"{uuid.uuid4().hex}.{ext}"
            vn = save_file(f, vn)
            # Eski videoyu sil
            old_vid = db.execute('SELECT video FROM services WHERE id=?', (id,)).fetchone()
            if old_vid: delete_file(old_vid['video'])
            db.execute('UPDATE services SET video=? WHERE id=?', (vn, id))

            
    db.execute('UPDATE services SET name=?, "desc"=?, icon=? WHERE id=?', 
               (request.form['n'], request.form['d'], request.form['i'], id))
    db.commit()
    log_action(f"Hizmet güncellendi ID: {id}")
    return redirect('/panel')


@app.route('/remove_service_video/<int:id>', methods=['POST'])
@admin_required
def remove_service_video(id):
    db = get_db()
    s = db.execute('SELECT video FROM services WHERE id=?', (id,)).fetchone()
    if s and s['video']:
        delete_file(s['video'])
        db.execute('UPDATE services SET video=NULL WHERE id=?', (id,))
        db.commit()
        log_action(f"Hizmet videosu kaldırıldı ID: {id}")
    return redirect('/panel')


@app.route('/delete_service/<int:id>', methods=['POST'])
@admin_required
def delete_service(id):
    db = get_db()
    # Dosyaları sil
    s = db.execute('SELECT img, video FROM services WHERE id=?', (id,)).fetchone()
    if s:
        delete_file(s['img'])
        delete_file(s['video'])
    db.execute('DELETE FROM services WHERE id=?', (id,))
    db.commit()
    log_action(f"Hizmet silindi ID: {id}")
    return redirect('/panel')


@app.route('/upload_img', methods=['POST'])
@admin_required
def upload_img():
    f = request.files['file']
    if f and f.filename and allowed_file(f.filename):
        fn = secure_filename(f.filename)
        fn = save_file(f, fn)
        db = get_db()
        db.execute('INSERT INTO gallery (img, title, "desc") VALUES (?, ?, ?)', (fn, request.form.get('t', ''), request.form.get('d', '')))
        db.commit()
    return redirect('/panel')

@app.route('/update_img_info', methods=['POST'])
@admin_required
def update_img_info():
    db = get_db()
    db.execute('UPDATE gallery SET title=?, "desc"=? WHERE id=?', (request.form['t'], request.form['d'], request.form['id']))
    db.commit()
    return redirect('/panel')

@app.route('/delete_img/<int:id>', methods=['POST'])
@admin_required
def delete_img(id):
    db = get_db()
    img = db.execute('SELECT img FROM gallery WHERE id=?', (id,)).fetchone()
    if img: delete_file(img['img'])
    db.execute('DELETE FROM gallery WHERE id=?', (id,))
    db.commit()
    log_action(f"Galeri resmi silindi ID: {id}")
    return redirect('/panel')


@app.route('/upload_video', methods=['POST'])
@admin_required
def upload_video():
    f = request.files['video_file']
    if f and f.filename and allowed_file(f.filename):
        fn = secure_filename(f.filename)
        fn = save_file(f, fn)
        db = get_db()
        db.execute('INSERT INTO videos (vid_path, title, "desc") VALUES (?, ?, ?)', (fn, request.form['t'], request.form.get('d', '')))
        db.commit()
    return redirect('/panel')

@app.route('/update_video_info', methods=['POST'])
@admin_required
def update_video_info():
    db = get_db()
    db.execute('UPDATE videos SET title=?, "desc"=? WHERE id=?', (request.form['t'], request.form['d'], request.form['id']))
    db.commit()
    return redirect('/panel')

@app.route('/delete_video/<int:id>', methods=['POST'])
@admin_required
def delete_video(id):
    db = get_db()
    vid = db.execute('SELECT vid_path FROM videos WHERE id=?', (id,)).fetchone()
    if vid: delete_file(vid['vid_path'])
    db.execute('DELETE FROM videos WHERE id=?', (id,))
    db.commit()
    log_action(f"Video silindi ID: {id}")
    return redirect('/panel')


@app.route('/update_settings', methods=['POST'])
@admin_required
def update_settings():
    db = get_db()
    
    files_to_update = {
        'hero_file': 'hero_img',
        'about_file': 'about_img',
        'about_hero_file': 'about_hero_img',
        'logo_file': 'logo',
        'popup_file': 'popup_img',
        'gallery_hero_file': 'gallery_hero_img',
        'services_hero_file': 'services_hero_img',
        'contact_hero_file': 'contact_hero_img'
    }
    
    for field, col in files_to_update.items():
        if field in request.files:
            f = request.files[field]
            if f and f.filename and allowed_file(f.filename):
                fn = secure_filename(f.filename)
                fn = save_file(f, fn)
                # Eski dosyayı sil
                old = db.execute(f'SELECT {col} FROM settings WHERE id=1').fetchone()
                if old and old[col]: delete_file(old[col])
                db.execute(f'UPDATE settings SET {col}=? WHERE id=1', (fn,))


    db.execute('''UPDATE settings SET 
        title=?, phone=?, whatsapp=?, address=?, email=?, 
        color_primary=?, color_secondary=?, hero_title=?, hero_subtitle=?, h_badge=?, h_btn1=?, h_btn2=?,
        about=?, about_text2=?, about_title=?, about_subtitle=?,
        vision_text=?, mission_text=?, values_text=?,
        s_title=?, s_subtitle=?,
        cta_title=?, cta_subtitle=?, cta_btn=?,
        t_title=?, f_title=?,
        gallery_title=?, gallery_hero_text=?,
        contact_title=?, contact_subtitle=?, contact_hero_text=?,
        meta_desc=?, meta_keys=?, footer_text=?, 
        stat1_title=?, stat1_value=?, stat2_title=?, stat2_value=?, 
        stat3_title=?, stat3_value=?, stat4_title=?, stat4_value=?, 
        popup_link=?, popup_active=?, instagram=?, facebook=?, linkedin=?,
        city=?, district=?, site_url=?, map_embed=?,
        seo_home_title=?, seo_home_desc=?, seo_home_keys=?,
        seo_about_title=?, seo_about_desc=?, seo_about_keys=?,
        seo_services_title=?, seo_services_desc=?, seo_services_keys=?,
        seo_gallery_title=?, seo_gallery_desc=?, seo_gallery_keys=?,
        seo_contact_title=?, seo_contact_desc=?, seo_contact_keys=?
        WHERE id=1''', 
               (request.form.get('t'), request.form.get('p'), request.form.get('w'), request.form.get('addr'), request.form.get('e'), 
                request.form.get('cp', '#001d3d'), request.form.get('cs', '#ffc300'), request.form.get('ht'), request.form.get('hs'), request.form.get('hb'), request.form.get('hb1'), request.form.get('hb2'),
                request.form.get('a'), request.form.get('a2'), request.form.get('at'), request.form.get('asub'),
                request.form.get('vt'), request.form.get('mt'), request.form.get('vlt'),
                request.form.get('st'), request.form.get('ssub'),
                request.form.get('ctat'), request.form.get('ctas'), request.form.get('ctab'),
                request.form.get('tt'), request.form.get('ftit'),
                request.form.get('gt'), request.form.get('ght'),
                request.form.get('ct'), request.form.get('csub'), request.form.get('cht'),
                request.form.get('md'), request.form.get('mk'), request.form.get('ft'),
                request.form.get('s1t'), request.form.get('s1v'),
                request.form.get('s2t'), request.form.get('s2v'),
                request.form.get('s3t'), request.form.get('s3v'),
                request.form.get('s4t'), request.form.get('s4v'),
                request.form.get('pl'), int(request.form.get('pa', 0)),
                request.form.get('insta'), request.form.get('face'), request.form.get('link'),
                request.form.get('city'), request.form.get('district'), request.form.get('site_url'), request.form.get('map_embed'),
                request.form.get('seo_home_title'), request.form.get('seo_home_desc'), request.form.get('seo_home_keys'),
                request.form.get('seo_about_title'), request.form.get('seo_about_desc'), request.form.get('seo_about_keys'),
                request.form.get('seo_services_title'), request.form.get('seo_services_desc'), request.form.get('seo_services_keys'),
                request.form.get('seo_gallery_title'), request.form.get('seo_gallery_desc'), request.form.get('seo_gallery_keys'),
                request.form.get('seo_contact_title'), request.form.get('seo_contact_desc'), request.form.get('seo_contact_keys')))
    
    # Şifre güncelleme (Settings içinden)
    new_pass = request.form.get('new_pass')
    if new_pass:
        if validate_password(new_pass):
            db.execute('UPDATE admin SET pass=? WHERE username=?', (generate_password_hash(new_pass), 'admin'))
            log_action("Admin şifresi güncellendi")
        else:
            flash('Yeni şifre yeterince güçlü değil! (En az 8 karakter, büyük/küçük harf ve rakam içermeli)', 'danger')
            return redirect('/panel')
        
    db.commit()
    log_action("Site ayarları güncellendi")
    flash('Ayarlar ve tasarım başarıyla güncellendi.', 'success')
    return redirect('/panel')


@app.route('/update_password', methods=['POST'])
@admin_required
def update_password():
    pw = request.form['p']
    if pw:
        if validate_password(pw):
            db = get_db()
            db.execute('UPDATE admin SET pass=? WHERE username=?', (generate_password_hash(pw), 'admin'))
            db.commit()
            log_action("Admin şifresi güncellendi (Bağımsız rota)")
            flash('Şifre başarıyla güncellendi.', 'success')
        else:
            flash('Şifre yeterince güçlü değil!', 'danger')
    return redirect('/panel')


@app.route('/submit_contact', methods=['POST'])
@limiter.limit("3 per minute")
def submit_contact():
    db = get_db()
    db.execute('INSERT INTO messages (name, phone, service, msg) VALUES (?, ?, ?, ?)', (request.form['n'], request.form['p'], request.form['s'], request.form['m']))
    db.commit()
    # log_action eklemiyoruz çünkü anonim kullanıcılar dolduruyor, ama isterseniz loglayabilirsiniz.
    flash('Mesajınız başarıyla gönderildi. En kısa sürede size döneceğiz.', 'success')
    return redirect(url_for('iletisim'))


@app.route('/delete_message/<int:id>', methods=['POST'])
@admin_required
def delete_message(id):
    db = get_db(); db.execute('DELETE FROM messages WHERE id=?', (id,)); db.commit()
    return redirect('/panel')

@app.route('/read_message/<int:id>', methods=['POST'])
@admin_required
def read_message(id):
    db = get_db(); db.execute('UPDATE messages SET is_read=1 WHERE id=?', (id,)); db.commit()
    return redirect('/panel')

@app.route('/add_testimonial', methods=['POST'])
@admin_required
def add_testimonial():
    db = get_db(); db.execute('INSERT INTO testimonials (name, content, stars) VALUES (?, ?, ?)', (request.form['n'], request.form['c'], request.form['s'])); db.commit()
    return redirect('/panel')

@app.route('/update_testimonial', methods=['POST'])
@admin_required
def update_testimonial():
    id = request.form['id']
    db = get_db()
    db.execute('UPDATE testimonials SET name=?, content=?, stars=? WHERE id=?', (request.form['n'], request.form['c'], request.form['s'], id))
    db.commit()
    return redirect('/panel')

@app.route('/delete_testimonial/<int:id>', methods=['POST'])
@admin_required
def delete_testimonial(id):
    db = get_db(); db.execute('DELETE FROM testimonials WHERE id=?', (id,)); db.commit()
    return redirect('/panel')

@app.route('/add_faq', methods=['POST'])
@admin_required
def add_faq():
    db = get_db(); db.execute('INSERT INTO faq (question, answer) VALUES (?, ?)', (request.form['q'], request.form['a'])); db.commit()
    return redirect('/panel')

@app.route('/update_faq', methods=['POST'])
@admin_required
def update_faq():
    id = request.form['id']
    db = get_db()
    db.execute('UPDATE faq SET question=?, answer=? WHERE id=?', (request.form['q'], request.form['a'], id))
    db.commit()
    return redirect('/panel')

@app.route('/delete_faq/<int:id>', methods=['POST'])
@admin_required
def delete_faq(id):
    db = get_db(); db.execute('DELETE FROM faq WHERE id=?', (id,)); db.commit()
    return redirect('/panel')

@app.route('/add_timeline', methods=['POST'])
@admin_required
def add_timeline():
    db = get_db(); db.execute('INSERT INTO timeline (year, title, content) VALUES (?, ?, ?)', (request.form['y'], request.form['t'], request.form['c'])); db.commit()
    return redirect('/panel')

@app.route('/update_timeline', methods=['POST'])
@admin_required
def update_timeline():
    id = request.form['id']
    db = get_db()
    db.execute('UPDATE timeline SET year=?, title=?, content=? WHERE id=?', (request.form['y'], request.form['t'], request.form['c'], id))
    db.commit()
    return redirect('/panel')

@app.route('/delete_timeline/<int:id>', methods=['POST'])
@admin_required
def delete_timeline(id):
    db = get_db(); db.execute('DELETE FROM timeline WHERE id=?', (id,)); db.commit()
    return redirect('/panel')

@app.route('/logout')
def logout():
    log_action("Oturum kapatıldı")
    session.clear()
    return redirect('/admin')


if __name__ == '__main__':
    app.run(debug=not IS_PRODUCTION)