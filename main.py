import os
from flask import Flask, request, jsonify, render_template
from icegods_core import IceGodsCore
from dotenv import load_dotenv

load_dotenv()

# Gunicorn looks for this exact variable 'app'
app = Flask(__name__)
core = IceGodsCore()

MASTER_KEY = os.getenv("ICEGODS_MASTER_KEY", "ICEGODS_838_SECRET")

@app.route('/api/ingest', methods=['POST'])
def ingest():
    key = request.headers.get("X-ICEGODS-KEY")
    if key != MASTER_KEY:
        return jsonify({"status": "UNAUTHORIZED"}), 403

    content = request.json
    if not content:
        return jsonify({"status": "ERROR", "msg": "No data received"}), 400

    entry = core.ingest_intel(
        bot_source=content.get("bot_name"),
        target=content.get("target"),
        raw_intel=content.get("intel_data")
    )
    return jsonify({"status": "SUCCESS", "entry": entry})

@app.route('/')
def dashboard():
    try:
        intel_feed = core.get_all_intel()
        return render_template('dashboard.html', feed=intel_feed)
    except Exception as e:
        return f"DASHBOARD ERROR: {str(e)}"

if __name__ == "__main__":
    # This runs only when testing locally
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
