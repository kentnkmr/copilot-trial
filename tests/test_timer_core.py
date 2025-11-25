from app.timer.core import TimerCore


class FakeClock:
    def __init__(self, start_ms: int = 0):
        self._t = int(start_ms)

    def now_ms(self) -> int:
        return self._t

    def advance(self, ms: int) -> None:
        if ms < 0:
            raise ValueError("ms must be non-negative")
        self._t += int(ms)


def test_start_and_remaining():
    clock = FakeClock(start_ms=1_000_000)
    t = TimerCore()
    duration_ms = 150_000  # 150s
    t.start(duration_ms=duration_ms, now_ms=clock.now_ms())

    assert t.get_remaining(clock.now_ms()) == duration_ms

    clock.advance(10_000)
    remaining = t.get_remaining(clock.now_ms())
    assert remaining == duration_ms - 10_000


def test_pause_and_resume():
    clock = FakeClock(0)
    t = TimerCore()
    t.start(duration_ms=60_000, now_ms=clock.now_ms())

    clock.advance(30_000)
    # pause at 30s
    t.pause(clock.now_ms())

    # advancing while paused should not reduce remaining
    clock.advance(40_000)
    remaining_while_paused = t.get_remaining(clock.now_ms())
    assert remaining_while_paused == 30_000

    # resume and advance 20s
    t.resume(clock.now_ms())
    clock.advance(20_000)
    remaining_after_resume = t.get_remaining(clock.now_ms())
    assert remaining_after_resume == 10_000


def test_multiple_pauses_and_completion():
    clock = FakeClock(0)
    t = TimerCore()
    t.start(duration_ms=5_000, now_ms=clock.now_ms())

    # advance 1s
    clock.advance(1_000)
    t.pause(clock.now_ms())
    clock.advance(500)
    t.resume(clock.now_ms())

    clock.advance(1_000)
    t.pause(clock.now_ms())
    clock.advance(1_000)
    # still paused, remaining should reflect only running time
    remaining = t.get_remaining(clock.now_ms())
    # elapsed should be 1s + 1s = 2s => remaining 3s
    assert remaining == 3_000

    # resume and finish
    t.resume(clock.now_ms())
    clock.advance(3_000)
    assert t.get_remaining(clock.now_ms()) == 0
    completed = t.check_complete(clock.now_ms())
    assert completed is True
    assert t.to_dict()["status"] == "completed"


def test_invalid_transitions_and_errors():
    clock = FakeClock(0)
    t = TimerCore()

    # invalid duration
    try:
        t.start(duration_ms=0, now_ms=clock.now_ms())
        assert False, "expected ValueError for zero duration"
    except ValueError:
        pass

    # start properly
    t.start(duration_ms=1000, now_ms=clock.now_ms())

    # can't start while running
    try:
        t.start(duration_ms=1000, now_ms=clock.now_ms())
        assert False, "expected RuntimeError when starting while running"
    except RuntimeError:
        pass

    # pause and invalid resume
    t.pause(clock.now_ms())
    # resume ok
    t.resume(clock.now_ms())

    # can't resume while running
    try:
        t.resume(clock.now_ms())
        assert False, "expected RuntimeError when resuming while running"
    except RuntimeError:
        pass
