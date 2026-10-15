import json
from pathlib import Path
from datetime import datetime
from collections import deque
from enum import Enum

class MessageStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"

class FileQueue:
    def __init__(self, path="queue.json"):
        self.path = Path(path)
        self.messages = deque()
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self.messages = deque(data)
            except Exception:
                self.messages = deque()

    def _save(self):
        self.path.write_text(
            json.dumps(list(self.messages), ensure_ascii=False, indent=2),
            encoding="utf-8")

    def enqueue(self, payload, topic="default"):
        msg = {
            "id": f"msg_{len(self.messages) + 1}",
            "topic": topic,
            "payload": payload,
            "status": MessageStatus.PENDING.value,
            "created_at": datetime.utcnow().isoformat(),
            "attempts": 0,
        }
        self.messages.append(msg)
        self._save()
        return msg

    def dequeue(self, topic=None):
        for m in list(self.messages):
            if m["status"] != MessageStatus.PENDING.value:
                continue
            if topic and m["topic"] != topic:
                continue
            m["status"] = MessageStatus.PROCESSING.value
            m["attempts"] += 1
            self._save()
            return m
        return None

    def ack(self, msg_id):
        for m in self.messages:
            if m["id"] == msg_id:
                m["status"] = MessageStatus.DONE.value
                m["completed_at"] = datetime.utcnow().isoformat()
                self._save()
                return True
        return False

    def nack(self, msg_id, retry=True):
        for m in self.messages:
            if m["id"] == msg_id:
                m["status"] = MessageStatus.PENDING.value if retry \
                    else MessageStatus.FAILED.value
                m["last_error_at"] = datetime.utcnow().isoformat()
                self._save()
                return True
        return False

    def stats(self):
        s = {}
        for m in self.messages:
            s[m["status"]] = s.get(m["status"], 0) + 1
        return s
