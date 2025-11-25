export class TimerCore {
  constructor() {
    this.state = {
      status: 'idle',
      startTs: null,
      durationMs: 0,
      pausedSince: null,
      pausedAccumMs: 0,
      endTs: null,
    };
  }

  start(durationMs, nowMs) {
    if (this.state.status === 'running' || this.state.status === 'paused') {
      throw new Error('Timer already running or paused');
    }
    if (durationMs <= 0) throw new Error('durationMs must be positive');
    this.state = {
      status: 'running',
      startTs: Number(nowMs),
      durationMs: Number(durationMs),
      pausedSince: null,
      pausedAccumMs: 0,
      endTs: null,
    };
  }

  pause(nowMs) {
    if (this.state.status !== 'running') throw new Error('Can only pause when running');
    this.state.pausedSince = Number(nowMs);
    this.state.status = 'paused';
  }

  resume(nowMs) {
    if (this.state.status !== 'paused') throw new Error('Can only resume when paused');
    if (this.state.pausedSince === null) throw new Error('pausedSince missing');
    const pausedInterval = Number(nowMs) - Number(this.state.pausedSince);
    if (pausedInterval < 0) throw new Error('nowMs earlier than pausedSince');
    this.state.pausedAccumMs += pausedInterval;
    this.state.pausedSince = null;
    this.state.status = 'running';
  }

  stop(nowMs) {
    if (this.state.status === 'idle') return;
    if (this.state.status === 'paused') {
      if (this.state.pausedSince !== null) {
        this.state.pausedAccumMs += Number(nowMs) - this.state.pausedSince;
        this.state.pausedSince = null;
      }
    }
    const remaining = this.getRemaining(nowMs);
    if (remaining <= 0) {
      this.state.status = 'completed';
      if (this.state.startTs !== null) this.state.endTs = this.state.startTs + this.state.durationMs;
    } else {
      this.state.status = 'canceled';
      this.state.endTs = Number(nowMs);
    }
  }

  skip(nowMs) {
    if (this.state.status === 'idle' || this.state.status === 'completed') return;
    this.state.pausedSince = null;
    this.state.endTs = Number(nowMs);
    this.state.status = 'skipped';
  }

  getElapsed(nowMs) {
    if (this.state.status === 'idle' || this.state.startTs === null) return 0;
    const total = Number(nowMs) - this.state.startTs;
    let paused = this.state.pausedAccumMs;
    if (this.state.status === 'paused' && this.state.pausedSince !== null) {
      paused += Number(nowMs) - this.state.pausedSince;
    }
    const elapsed = total - paused;
    return Math.max(0, elapsed);
  }

  getRemaining(nowMs) {
    if (this.state.status === 'idle' || this.state.startTs === null) return 0;
    const remaining = this.state.durationMs - this.getElapsed(nowMs);
    return Math.max(0, remaining);
  }

  checkComplete(nowMs) {
    if (this.state.status === 'completed' || this.state.status === 'idle') return this.state.status === 'completed';
    if (this.getRemaining(nowMs) <= 0) {
      this.state.status = 'completed';
      if (this.state.startTs !== null) this.state.endTs = this.state.startTs + this.state.durationMs;
      return true;
    }
    return false;
  }

  toObject() {
    return { ...this.state };
  }
}

export default TimerCore;
