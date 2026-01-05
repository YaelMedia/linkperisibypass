import os
import sqlite3
import datetime
from flask import Flask, render_template, request, jsonify, send_file
from bypass_motoru import start_bypass_process

app = Flask(__name__)

DB_NAME = "history.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs 
                          (id INTEGER PRIMARY KEY, original TEXT, bypassed TEXT, date TEXT, ip TEXT)''')
        conn.commit()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/bypass', methods=['POST'])
def api_bypass():
    data = request.json
    url = data.get('url')
    
    if not url: return jsonify({"status": "error", "msg": "Link boş olamaz!"})

    # MOTORU ÇALIŞTIR
    result = start_bypass_process(url)
    
    return jsonify(result)

# 👇 YENİ EKLENEN KISIM: EKRAN GÖRÜNTÜSÜNE BAKMA 👇
@app.route('/debug')
def debug_screenshot():
    if os.path.exists("debug_screenshot.png"):
        return send_file("debug_screenshot.png", mimetype='image/png')
    else:
        return "Henüz hata ekran görüntüsü yok."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
