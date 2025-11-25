from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class TimeProvider:
    """Abstract time provider returning epoch milliseconds."""

    def now_ms(self) -> int:
        raise NotImplementedError()


class RealClock(TimeProvider):
    import time

    def now_ms(self) -> int:  # pragma: no cover - tiny wrapper
        return int(self.time.time() * 1000)


@dataclass
class TimerState:
    status: str = "idle"  # idle | running | paused | completed | canceled | skipped
    start_ts: Optional[int] = None
    duration_ms: int = 0
    paused_since: Optional[int] = None
    paused_accum_ms: int = 0
    end_ts: Optional[int] = None


class TimerCore:
    """Pure timer logic.

    - All timestamps are epoch milliseconds (int).
    - Uses injected TimeProvider in external code/tests to control time.

    Public API:
      start(duration_ms, now_ms)
      pause(now_ms)
      resume(now_ms)
      stop(now_ms)
      skip(now_ms)
      get_remaining(now_ms)
      get_elapsed(now_ms)
      check_complete(now_ms)
    """

    def __init__(self) -> None:
        self.s = TimerState()

    def start(self, duration_ms: int, now_ms: int) -> None:
        if self.s.status in ("running", "paused"):
            raise RuntimeError("Timer already running or paused")
        if duration_ms <= 0:
            raise ValueError("duration_ms must be positive")
        self.s = TimerState(
            status="running",
            start_ts=now_ms,
            duration_ms=int(duration_ms),
            paused_since=None,
            paused_accum_ms=0,
            end_ts=None,
        )

    def pause(self, now_ms: int) -> None:
        if self.s.status != "running":
            raise RuntimeError("Can only pause when running")
        self.s.paused_since = now_ms
        self.s.status = "paused"

    def resume(self, now_ms: int) -> None:
        if self.s.status != "paused":
            raise RuntimeError("Can only resume when paused")
        assert self.s.paused_since is not None
        paused_interval = now_ms - self.s.paused_since
        if paused_interval < 0:
            raise ValueError("now_ms earlier than paused_since")
        self.s.paused_accum_ms += paused_interval
        self.s.paused_since = None
        self.s.status = "running"

    def stop(self, now_ms: int) -> None:
        # Stop will mark as canceled unless already completed
        if self.s.status == "idle":
            return
        if self.s.status == "paused":
            # finalize paused interval
            assert self.s.paused_since is not None
            self.s.paused_accum_ms += now_ms - self.s.paused_since
            self.s.paused_since = None
        # if already completed, keep end_ts
        if self.get_remaining(now_ms) <= 0:
            self.s.status = "completed"
            # if end_ts not set, set it to start_ts + duration
            if self.s.start_ts is not None:
                self.s.end_ts = self.s.start_ts + self.s.duration_ms
        else:
            self.s.status = "canceled"
            self.s.end_ts = now_ms

    def skip(self, now_ms: int) -> None:
        # Skip means jump to end and mark skipped
        if self.s.status in ("idle", "completed"):
            return
        self.s.paused_since = None
        self.s.paused_accum_ms = self.s.paused_accum_ms
        self.s.end_ts = now_ms
        self.s.status = "skipped"

    def get_elapsed(self, now_ms: int) -> int:
        if self.s.status == "idle" or self.s.start_ts is None:
            return 0
        total = now_ms - self.s.start_ts
        # subtract all pauses (accumulated + current one if paused)
        paused = self.s.paused_accum_ms
        if self.s.status == "paused" and self.s.paused_since is not None:
            paused += now_ms - self.s.paused_since
        elapsed = total - paused
        return max(0, elapsed)

    def get_remaining(self, now_ms: int) -> int:
        if self.s.status == "idle" or self.s.start_ts is None:
            return 0
        remaining = self.s.duration_ms - self.get_elapsed(now_ms)
        return max(0, remaining)

    def check_complete(self, now_ms: int) -> bool:
        """Check if timer reached or passed end and update status.

        Returns True if the timer is now marked as completed.
        """
        if self.s.status in ("completed", "idle"):
            return self.s.status == "completed"
        if self.get_remaining(now_ms) <= 0:
            self.s.status = "completed"
            if self.s.start_ts is not None:
                self.s.end_ts = self.s.start_ts + self.s.duration_ms
            return True
        return False

    # convenience helpers for tests / UI
    def to_dict(self) -> dict:
        return {
            "status": self.s.status,
            "start_ts": self.s.start_ts,
            "duration_ms": self.s.duration_ms,
            "paused_since": self.s.paused_since,
            "paused_accum_ms": self.s.paused_accum_ms,
            "end_ts": self.s.end_ts,
        }
