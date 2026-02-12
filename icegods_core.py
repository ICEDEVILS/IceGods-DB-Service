import json
import os
import time
from datetime import datetime

DB_FILE = "icegods_intel_core.json"

class IceGodsCore:
    def __init__(self):
        self.core_data = {"intel": [], "bots": {}, "invites": []}
        self.load_core()

    def load_core(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r') as f:
                    loaded = json.load(f)
                    # AUTO-REPAIR: If old data was a list, migrate it to the new format
                    if isinstance(loaded, list):
                        self.core_data["intel"] = loaded
                    else:
                        self.core_data = loaded
            except Exception as e:
                print(f"📡 CORE REPAIR ACTIVE: {e}")
        self.save_core()

    def save_core(self):
        with open(DB_FILE, 'w') as f:
            json.dump(self.core_data, f, indent=4)

    def ingest_intel(self, bot_name, target, raw_intel):
        # Update Bot Detector
        self.core_data["bots"][bot_name] = {
            "last_seen": datetime.now().strftime('%H:%M:%S'),
            "status": "OPERATIONAL",
            "hits": self.core_data["bots"].get(bot_name, {}).get("hits", 0) + 1
        }

        # AI OMEGA Detection
        entropy = sum(ord(c) for c in target) % 100
        is_omega = entropy > 85 or "0x" in target.lower()

        entry = {
            "id": f"IG-{int(time.time())}",
            "source": bot_name,
            "target": target,
            "threat": "OMEGA" if is_omega else "CRITICAL",
            "valuation": f"${raw_intel.get('cost', 500) * (2.8 if is_omega else 1.3):,.2f}",
            "timestamp": datetime.now().strftime('%H:%M:%S')
        }

        self.core_data["intel"].insert(0, entry)
        self.core_data["intel"] = self.core_data["intel"][:50]
        self.save_core()
        return entry

    def check_health(self):
        anomalies = []
        # Ensure 'bots' key exists
        bots = self.core_data.get("bots", {})
        for name, info in bots.items():
            if info.get("status") == "CRITICAL_ISSUE":
                anomalies.append(f"SYSTEM FAILURE: {name} offline.")
        return anomalies
