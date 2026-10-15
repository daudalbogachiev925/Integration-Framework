from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

@dataclass
class Metric:
    name: str
    value: float
    labels: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class Monitor:
    def __init__(self):
        self.metrics = []
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)

    def increment(self, name, labels=None):
        key = f"{name}:{labels}" if labels else name
        self.counters[key] += 1
        self.metrics.append(Metric(name, 1, labels or {}))

    def observe(self, name, value, labels=None):
        key = f"{name}:{labels}" if labels else name
        self.timers[key].append(value)
        self.metrics.append(Metric(name, value, labels or {}))

    def summary(self):
        timer_stats = {}
        for key, values in self.timers.items():
            if not values:
                continue
            timer_stats[key] = {
                "count": len(values),
                "avg": round(sum(values) / len(values), 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "p95": round(sorted(values)[int(len(values) * 0.95)] if len(values) > 1 else values[0], 2),
            }
        return {
            "counters": dict(self.counters),
            "timers": timer_stats,
            "total_metrics": len(self.metrics),
        }
