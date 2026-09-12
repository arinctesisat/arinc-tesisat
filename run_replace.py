import os
import re
import sqlite3

target_dir = os.path.dirname(os.path.abspath(__file__))
search_pattern = re.compile(r"Silivri Su Kaçağı Tespiti\s*tesisat|Silivri Su Kaçağı Tespiti|Silivri Su Kaçağı Tespiti\s*tesisat|Silivri Su Kaçağı Tespiti", re.IGNORECASE)
replacement = "Silivri Su Kaçağı Tespit"

# Extensions to process for text search-and-replace
valid_extensions = {'.html', '.py', '.js', '.css', '.txt', '.env', '.json'}

def process_text_file(file_path):
    # Avoid modifying the script itself
    if "run_replace.py" in file_path:
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except:
            return
    except:
        return
    
    if search_pattern.search(content):
        new_content = search_pattern.sub(replacement, content)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"[TEXT] Güncellendi: {file_path}")
        except Exception as e:
            print(f"[TEXT] Hata oluştu: {file_path}: {e}")

def process_sqlite_db(db_path):
    print(f"[DB] Veritabanı kontrol ediliyor: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            if table.startswith('sqlite_'):
                continue
            
            # Get table columns and primary key information
            cursor.execute(f"PRAGMA table_info(\"{table}\");")
            columns_info = cursor.fetchall()
            columns = [c[1] for c in columns_info]
            pk_cols = [c[1] for c in columns_info if c[5] > 0]
            
            # Use rowid if there is no explicit primary key
            pk_str = ", ".join([f"\"{c}\"" for c in pk_cols]) if pk_cols else "rowid"
            
            select_query = f"SELECT {pk_str}, * FROM \"{table}\""
            try:
                cursor.execute(select_query)
                rows = cursor.fetchall()
            except Exception as e:
                print(f"[DB] Hata oluştu: {table} ({db_path}): {e}")
                continue
            
            for row in rows:
                pk_val_count = len(pk_cols) if pk_cols else 1
                pk_vals = row[:pk_val_count]
                actual_row_vals = row[pk_val_count:]
                
                updates = []
                params = []
                for col_name, val in zip(columns, actual_row_vals):
                    if isinstance(val, str) and search_pattern.search(val):
                        new_val = search_pattern.sub(replacement, val)
                        updates.append(f"\"{col_name}\" = ?")
                        params.append(new_val)
                
                if updates:
                    if pk_cols:
                        where_clause = " AND ".join([f"\"{c}\" = ?" for c in pk_cols])
                    else:
                        where_clause = "rowid = ?"
                    
                    update_query = f"UPDATE \"{table}\" SET {', '.join(updates)} WHERE {where_clause}"
                    cursor.execute(update_query, params + list(pk_vals))
                    
        conn.commit()
        conn.close()
        print(f"[DB] Veritabanı başarıyla güncellendi: {db_path}")
    except Exception as e:
        print(f"[DB] Hata oluştu: {db_path}: {e}")

# Walk through directory
for root, dirs, files in os.walk(target_dir):
    # Exclude directories
    if any(p in root for p in ['venv', '.git', '.gemini', '__pycache__']):
        continue
    for file in files:
        file_path = os.path.join(root, file)
        ext = os.path.splitext(file)[1].lower()
        if ext in valid_extensions:
            process_text_file(file_path)
        elif ext == '.db':
            process_sqlite_db(file_path)

print("İşlem tamamlandı.")
