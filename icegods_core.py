import json
import os
import time
from datetime import datetime, timedelta

DB_FILE = "icegods_intel_core.json"

class IceGodsCore:
    def __init__(self):
        self.load_core()

    def load_core(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r') as f:
                    self.core_data = json.load(f)
            except:
                self.core_data = {"intel": [], "bots": {}, "invites": []}
        else:
            self.core_data = {"intel": [], "bots": {}, "invites": []}

    def save_core(self):
        with open(DB_FILE, 'w') as f:
            json.dump(self.core_data, f, indent=4)

    def ingest_intel(self, bot_name, target, raw_intel):
        # Update Bot Health (The Detector)
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
        self.core_data["intel"] = self.core_data["intel"][:50] # Keep last 50
        self.save_core()
        return entry

    def check_health(self):
        """The Detector: Monitors for bot failure"""
        anomalies = []
        for name, info in self.core_data["bots"].items():
            # If status was manually set to CRITICAL or hasn't updated
            if info["status"] == "CRITICAL_ISSUE":
                anomalies.append(f"SYSTEM FAILURE: {name} offline.")
        return anomalies
