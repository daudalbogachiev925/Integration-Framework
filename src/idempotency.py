import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta

class IdempotencyStore:
    def __init__(self, path="idempotency.json", ttl_hours=24):
        self.path = Path(path)
        self.ttl = timedelta(hours=ttl_hours)
        self.data = self._load()

    def _load(self):
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self):
        self.path.write_text(json.dumps(self.data, indent=2),
                             encoding="utf-8")

    def _cleanup(self):
        now = datetime.utcnow()
        expired = []
        for key, entry in self.data.items():
            ts = datetime.fromisoformat(entry["timestamp"])
            if now - ts > self.ttl:
                expired.append(key)
        for k in expired:
            del self.data[k]

    @staticmethod
    def make_key(payload):
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def get(self, key):
        self._cleanup()
        return self.data.get(key)

    def set(self, key, result):
        self.data[key] = {
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._save()

    def execute_once(self, key, func, *args, **kwargs):
        cached = self.get(key)
        if cached:
            return cached["result"]
        result = func(*args, **kwargs)
        self.set(key, result)
        return result
