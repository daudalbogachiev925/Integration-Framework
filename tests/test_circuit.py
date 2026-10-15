from src.circuit_breaker import CircuitBreaker, State

def test_circuit_opens_after_threshold():
    cb = CircuitBreaker("t", failure_threshold=3)
    for _ in range(3):
        try:
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("x")))
        except RuntimeError:
            pass
    assert cb.state == State.OPEN

def test_circuit_success_resets():
    cb = CircuitBreaker("t", failure_threshold=5)
    cb.call(lambda: "ok")
    assert cb.failures == 0
    assert cb.state == State.CLOSED

def test_circuit_blocks_when_open():
    cb = CircuitBreaker("t", failure_threshold=2, recovery_timeout=3600)
    for _ in range(2):
        try:
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("x")))
        except RuntimeError:
            pass
    try:
        cb.call(lambda: "ok")
        assert False
    except RuntimeError as e:
        assert "OPEN" in str(e)
