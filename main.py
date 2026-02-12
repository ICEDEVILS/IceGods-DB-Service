import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from flask import Flask, request, jsonify, render_template
from brain import AlienBrain
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# --- CONFIG ---
DB_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
MASTER_KEY = os.getenv("ICEGODS_MASTER_KEY", "ICEGODS_VGD_838")

def get_db():
    return psycopg2.connect(DB_URL, sslmode='require')

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS icegods_intel_hub (
            id SERIAL PRIMARY KEY,
            bot_source TEXT,
            target TEXT,
            ai_classification TEXT,
            valuation TEXT,
            raw_intel JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close(); conn.close()

# --- API ENDPOINTS ---

@app.route('/api/ingest', methods=['POST'])
def ingest():
    # Authentication
    key = request.headers.get("X-ICEGODS-KEY")
    if key != MASTER_KEY:
        return jsonify({"status": "DENIED", "msg": "Invalid Master Key"}), 403

    data = request.json
    bot_source = data.get("bot_name")
    target = data.get("target")
    raw_intel = data.get("intel_data")

    # PROCESS VIA ALIEN BRAIN
    ai_analysis = AlienBrain.analyze_intelligence(bot_source, target, raw_intel)

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO icegods_intel_hub (bot_source, target, ai_classification, valuation, raw_intel)
            VALUES (%s, %s, %s, %s, %s)
        """, (bot_source, target, ai_analysis['classification'], ai_analysis['exposure_valuation'], Json(raw_intel)))
        conn.commit()
        cur.close(); conn.close()
        return jsonify({"status": "SUCCESS", "analysis": ai_analysis}), 200
    except Exception as e:
        return jsonify({"status": "DB_ERROR", "msg": str(e)}), 500

@app.route('/')
def dashboard():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM icegods_intel_hub ORDER BY created_at DESC LIMIT 50")
        intel_feed = cur.fetchall()
        cur.close(); conn.close()
        return render_template('dashboard.html', feed=intel_feed)
    except Exception as e:
        return f"BRAIN OFFLINE: {str(e)}"

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
