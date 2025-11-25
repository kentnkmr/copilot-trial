from typing import Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.timer.core import TimerCore

router = APIRouter()


class SessionCreate(BaseModel):
    duration_ms: int
    now_ms: Optional[int] = None


class SessionAction(BaseModel):
    action: str  # pause/resume/stop/skip
    now_ms: Optional[int] = None


class SessionInfo(BaseModel):
    id: str
    status: str
    duration_ms: int
    remaining_ms: int
    start_ts: Optional[int]
    paused_accum_ms: int


# simple in-memory store: session_id -> TimerCore
_sessions: Dict[str, TimerCore] = {}


@router.post("/sessions", response_model=SessionInfo)
def create_session(body: SessionCreate):
    now = body.now_ms if body.now_ms is not None else 0
    if body.duration_ms <= 0:
        raise HTTPException(status_code=400, detail="duration_ms must be positive")
    tid = str(uuid4())
    timer = TimerCore()
    timer.start(duration_ms=body.duration_ms, now_ms=now)
    _sessions[tid] = timer
    return SessionInfo(
        id=tid,
        status=timer.s.status,
        duration_ms=timer.s.duration_ms,
        remaining_ms=timer.get_remaining(now),
        start_ts=timer.s.start_ts,
        paused_accum_ms=timer.s.paused_accum_ms,
    )


@router.get("/sessions/{sid}", response_model=SessionInfo)
def get_session(sid: str, now_ms: Optional[int] = None):
    if sid not in _sessions:
        raise HTTPException(status_code=404, detail="session not found")
    timer = _sessions[sid]
    now = now_ms if now_ms is not None else 0
    remaining = timer.get_remaining(now)
    # lazily mark complete
    timer.check_complete(now)
    return SessionInfo(
        id=sid,
        status=timer.s.status,
        duration_ms=timer.s.duration_ms,
        remaining_ms=remaining,
        start_ts=timer.s.start_ts,
        paused_accum_ms=timer.s.paused_accum_ms,
    )


@router.patch("/sessions/{sid}", response_model=SessionInfo)
def action_session(sid: str, body: SessionAction):
    if sid not in _sessions:
        raise HTTPException(status_code=404, detail="session not found")
    timer = _sessions[sid]
    now = body.now_ms if body.now_ms is not None else 0
    act = body.action.lower()
    if act == "pause":
        timer.pause(now)
    elif act == "resume":
        timer.resume(now)
    elif act == "stop":
        timer.stop(now)
    elif act == "skip":
        timer.skip(now)
    else:
        raise HTTPException(status_code=400, detail="unknown action")

    remaining = timer.get_remaining(now)
    timer.check_complete(now)
    return SessionInfo(
        id=sid,
        status=timer.s.status,
        duration_ms=timer.s.duration_ms,
        remaining_ms=remaining,
        start_ts=timer.s.start_ts,
        paused_accum_ms=timer.s.paused_accum_ms,
    )

