import { describe, it, expect } from 'vitest'
import { TimerCore } from '../src/timerCore.js'

class FakeClock {
  constructor(start = 0) {
    this.t = start
  }
  nowMs() { return this.t }
  advance(ms) { this.t += ms }
}

describe('TimerCore (JS)', () => {
  it('start and remaining', () => {
    const clock = new FakeClock(1000000)
    const t = new TimerCore()
    const duration = 150000
    t.start(duration, clock.nowMs())
    expect(t.getRemaining(clock.nowMs())).toBe(duration)
    clock.advance(10000)
    expect(t.getRemaining(clock.nowMs())).toBe(duration - 10000)
  })

  it('pause and resume', () => {
    const clock = new FakeClock(0)
    const t = new TimerCore()
    t.start(60000, clock.nowMs())
    clock.advance(30000)
    t.pause(clock.nowMs())
    clock.advance(40000)
    expect(t.getRemaining(clock.nowMs())).toBe(30000)
    t.resume(clock.nowMs())
    clock.advance(20000)
    expect(t.getRemaining(clock.nowMs())).toBe(10000)
  })

  it('multiple pauses and completion', () => {
    const clock = new FakeClock(0)
    const t = new TimerCore()
    t.start(5000, clock.nowMs())
    clock.advance(1000)
    t.pause(clock.nowMs())
    clock.advance(500)
    t.resume(clock.nowMs())
    clock.advance(1000)
    t.pause(clock.nowMs())
    clock.advance(1000)
    expect(t.getRemaining(clock.nowMs())).toBe(3000)
    t.resume(clock.nowMs())
    clock.advance(3000)
    expect(t.getRemaining(clock.nowMs())).toBe(0)
    expect(t.checkComplete(clock.nowMs())).toBe(true)
    expect(t.toObject().status).toBe('completed')
  })

  it('invalid transitions', () => {
    const clock = new FakeClock(0)
    const t = new TimerCore()
    expect(() => t.start(0, clock.nowMs())).toThrow()
    t.start(1000, clock.nowMs())
    expect(() => t.start(1000, clock.nowMs())).toThrow()
    t.pause(clock.nowMs())
    t.resume(clock.nowMs())
    expect(() => t.resume(clock.nowMs())).toThrow()
  })
})
