import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from flask import Flask, jsonify
load_dotenv()

app = Flask(__name__)
conn = psycopg2.connect(os.getenv('DATABASE_URL'), cursor_factory=psycopg2.extras.DictCursor)
cur = conn.cursor()
cur.execute('SELECT * FROM usuarios LIMIT 1')
row = cur.fetchone()
with app.app_context():
    print(jsonify(dict(row)).get_data(as_text=True))

