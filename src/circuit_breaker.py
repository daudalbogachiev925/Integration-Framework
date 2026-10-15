from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass

class State(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 2

    def __post_init__(self):
        self.state = State.CLOSED
        self.failures = 0
        self.successes = 0
        self.opened_at = None

    def can_execute(self):
        if self.state == State.CLOSED:
            return True
        if self.state == State.OPEN:
            if self.opened_at and \
               datetime.utcnow() - self.opened_at > timedelta(seconds=self.recovery_timeout):
                self.state = State.HALF_OPEN
                self.successes = 0
                return True
            return False
        return True

    def record_success(self):
        if self.state == State.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.success_threshold:
                self.state = State.CLOSED
                self.failures = 0
                self.successes = 0
        else:
            self.failures = 0

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = State.OPEN
            self.opened_at = datetime.utcnow()

    def call(self, func, *args, **kwargs):
        if not self.can_execute():
            raise RuntimeError(f"Circuit {self.name} is OPEN")
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception:
            self.record_failure()
            raise

    def stats(self):
        return {
            "name": self.name,
            "state": self.state.value,
            "failures": self.failures,
            "successes": self.successes,
        }
