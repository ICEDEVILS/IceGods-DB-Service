import json
import os
import time
from datetime import datetime

DB_FILE = "icegods_intel_core.json"

class IceGodsCore:
    def __init__(self):
        self.load_core()

    def load_core(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r') as f:
                    self.data = json.load(f)
            except:
                self.data = []
        else:
            self.data = []

    def save_core(self):
        with open(DB_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    def ingest_intel(self, bot_source, target, raw_intel):
        # --- ALIEN AI LOGIC ---
        # Detect entropy based on target string complexity
        entropy = sum(ord(c) for c in target) % 100
        base_val = raw_intel.get("cost", 500)

        # OMEGA detection
        is_omega = entropy > 85 or "0x" in target.lower()
        threat = "OMEGA" if is_omega else "CRITICAL"

        # Valuation AI
        multiplier = 2.5 if is_omega else 1.2
        final_valuation = f"${base_val * multiplier:,.2f}"

        intel_entry = {
            "id": f"IG-{int(time.time())}",
            "source": bot_source,
            "target": target,
            "valuation": final_valuation,
            "threat_level": threat,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "raw": raw_intel
        }

        self.data.insert(0, intel_entry)
        self.save_core()
        return intel_entry

    def get_all_intel(self):
        return self.data
