import os
import threading
from flask import Flask, request, jsonify, render_template
from icegods_core import IceGodsCore
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
core = IceGodsCore()

MASTER_KEY = os.getenv("ICEGODS_MASTER_KEY", "ICEGODS_838_SECRET")

@app.route('/api/ingest', methods=['POST'])
def ingest():
    if request.headers.get("X-ICEGODS-KEY") != MASTER_KEY:
        return jsonify({"status": "DENIED"}), 403
    content = request.json
    entry = core.ingest_intel(content.get("bot_name"), content.get("target"), content.get("intel_data"))
    return jsonify({"status": "SUCCESS", "analysis": entry})

@app.route('/')
def dashboard():
    return render_template('dashboard.html',
                           feed=core.core_data["intel"], 
                           bots=core.core_data["bots"],
                           anomalies=core.check_health())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
