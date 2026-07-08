import urllib.request
from bs4 import BeautifulSoup
import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL')
if not db_url or '[YOUR-PASSWORD]' in db_url:
    print("ERROR: DATABASE_URL no está configurada correctamente en el .env.")
    exit(1)

html_content = urllib.request.urlopen('https://www.4mnature.com/productos').read().decode('latin1')
soup = BeautifulSoup(html_content, 'html.parser')

products_data = []
for card in soup.find_all('div', class_='product-card'):
    name = card.get('data-fav-name', '').strip()
    img = card.get('data-fav-img', '').strip()
    meta = card.get('data-fav-meta', '').strip()

    if not name or not img:
        continue

    # Fix spaces and weird dashes in category
    category = meta.replace('\x80\x93', '-').replace('\x96', '-').replace('\x80', '-').replace('  ', ' - ').strip()
    # If the dash is weird, just replace with standard dash
    category = category.replace(' – ', ' - ').replace(' –', ' -')

    full_img_url = f"https://www.4mnature.com/{img}"
    products_data.append((name, category, full_img_url))

print(f"Encontrados {len(products_data)} productos.")

# 1. Update SQLite
sqlite_db_path = os.path.join(os.path.dirname(__file__), 'natura.db')
sqlite_conn = sqlite3.connect(sqlite_db_path)
sqlite_cur = sqlite_conn.cursor()
sqlite_updated = 0

for name, category, img_url in products_data:
    sqlite_cur.execute("UPDATE productos SET nombre=?, categoria=? WHERE imagen=?", (name, category, img_url))
    sqlite_updated += sqlite_cur.rowcount

sqlite_conn.commit()
sqlite_conn.close()
print(f"SQLite: {sqlite_updated} filas actualizadas.")

# 2. Update Supabase
pg_conn = psycopg2.connect(db_url)
pg_cur = pg_conn.cursor()
pg_updated = 0

for name, category, img_url in products_data:
    pg_cur.execute("UPDATE productos SET nombre=%s, categoria=%s WHERE imagen=%s", (name, category, img_url))
    pg_updated += pg_cur.rowcount

pg_conn.commit()
pg_conn.close()
print(f"Supabase: {pg_updated} filas actualizadas.")
