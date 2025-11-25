const startBtn = document.getElementById('startBtn')
const pauseBtn = document.getElementById('pauseBtn')
const resumeBtn = document.getElementById('resumeBtn')
const stopBtn = document.getElementById('stopBtn')
const durationInput = document.getElementById('duration')
const timeDisplay = document.getElementById('timeDisplay')
const lastSession = document.getElementById('lastSession')

let currentSessionId = null
let tickTimer = null

function formatMs(ms) {
  const s = Math.ceil(ms / 1000)
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`
}

async function createSession(durationMinutes) {
  const duration_ms = Number(durationMinutes) * 60 * 1000
  const now_ms = Date.now()
  const res = await fetch('/api/v1/sessions', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ duration_ms, now_ms })
  })
  if (!res.ok) throw new Error('create failed')
  return await res.json()
}

async function patchSession(action) {
  if (!currentSessionId) return
  const now_ms = Date.now()
  const res = await fetch(`/api/v1/sessions/${currentSessionId}`, {
    method: 'PATCH',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ action, now_ms })
  })
  if (!res.ok) throw new Error('action failed')
  return await res.json()
}

async function getSessionInfo() {
  if (!currentSessionId) return null
  const now_ms = Date.now()
  const res = await fetch(`/api/v1/sessions/${currentSessionId}?now_ms=${now_ms}`)
  if (!res.ok) return null
  return await res.json()
}

function updateUIFromSession(data) {
  if (!data) return
  timeDisplay.textContent = formatMs(data.remaining_ms)
  lastSession.textContent = JSON.stringify(data, null, 2)
  currentSessionId = data.id

  const status = data.status
  // update buttons
  startBtn.disabled = status === 'running' || status === 'paused'
  pauseBtn.disabled = status !== 'running'
  resumeBtn.disabled = status !== 'paused'
  stopBtn.disabled = status === 'idle' || status === 'completed' || status === 'canceled'
}

async function autoTick() {
  if (!currentSessionId) return
  const info = await getSessionInfo()
  if (!info) return
  updateUIFromSession(info)
  if (info.status === 'completed') {
    clearInterval(tickTimer)
    tickTimer = null
    startBtn.disabled = false
  }
}

startBtn.addEventListener('click', async () => {
  try {
    const duration = Number(durationInput.value || 25)
    const s = await createSession(duration)
    updateUIFromSession(s)
    if (tickTimer) clearInterval(tickTimer)
    tickTimer = setInterval(autoTick, 1000)
  } catch (err) { alert(err.message) }
})

pauseBtn.addEventListener('click', async () => {
  try {
    const res = await patchSession('pause')
    updateUIFromSession(res)
  } catch (err) { alert(err.message) }
})

resumeBtn.addEventListener('click', async () => {
  try {
    const res = await patchSession('resume')
    updateUIFromSession(res)
  } catch (err) { alert(err.message) }
})

stopBtn.addEventListener('click', async () => {
  try {
    const res = await patchSession('stop')
    updateUIFromSession(res)
    if (tickTimer) { clearInterval(tickTimer); tickTimer = null }
  } catch (err) { alert(err.message) }
})

// show placeholder time
timeDisplay.textContent = '00:00'
