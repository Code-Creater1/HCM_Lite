import { useEffect, useState } from 'react'
import api from '../api/client'

const STATUS_COLOR = {
  present: '#16a34a', late: '#f59e0b', half_day: '#eab308',
  absent: '#dc2626', on_leave: '#3b82f6', missing_checkout: '#f97316',
  weekend: '#9ca3af', holiday: '#8b5cf6',
}

export default function MyAttendance() {
  const [today, setToday] = useState(null)
  const [cal, setCal] = useState([])
  const [ym, setYm] = useState(() => { const d = new Date(); return { y: d.getFullYear(), m: d.getMonth() + 1 } })
  const [corrs, setCorrs] = useState([])
  const [show, setShow] = useState(false)
  const [f, setF] = useState({ date: '', requested_check_in: '', requested_check_out: '', reason: '' })
  const [msg, setMsg] = useState(''); const [err, setErr] = useState('')

  const reload = async () => {
    const [t, c, cs] = await Promise.all([
      api.get('/attendance/me/today'),
      api.get('/attendance/me/calendar', { params: { year: ym.y, month: ym.m } }),
      api.get('/attendance/corrections/me'),
    ])
    setToday(t.data); setCal(c.data); setCorrs(cs.data)
  }
  useEffect(() => { reload() }, [ym])

  const checkIn = async () => {
    setErr(''); setMsg('')
    try { await api.post('/attendance/check-in'); setMsg('Checked in.'); reload() }
    catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }
  const checkOut = async () => {
    setErr(''); setMsg('')
    try { const { data } = await api.post('/attendance/check-out')
      setMsg(`Checked out. Worked ${data.worked_minutes} min. Status: ${data.status}.`); reload()
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }
  const submitCorr = async (e) => {
    e.preventDefault(); setErr(''); setMsg('')
    try {
      const p = { ...f }
      if (!p.requested_check_in) p.requested_check_in = null
      if (!p.requested_check_out) p.requested_check_out = null
      await api.post('/attendance/corrections', p)
      setMsg('Correction requested.'); setShow(false)
      setF({ date: '', requested_check_in: '', requested_check_out: '', reason: '' }); reload()
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }

  return (
    <div>
      <h1>My Attendance</h1>
      {err && <div className="error">{err}</div>}
      {msg && <div className="success">{msg}</div>}

      <div className="card" style={{ marginBottom: 20 }}>
        <h3>Today</h3>
        {!today?.exists && <p style={{ color: 'var(--text-muted)' }}>No check-in yet today.</p>}
        {today?.exists && (
          <p>
            <b>In:</b> {today.check_in ? new Date(today.check_in).toLocaleTimeString() : '—'} ·
            <b style={{ marginLeft: 12 }}>Out:</b> {today.check_out ? new Date(today.check_out).toLocaleTimeString() : '—'} ·
            <b style={{ marginLeft: 12 }}>Status:</b> {today.status}
          </p>
        )}
        <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
          <button className="btn btn-primary" onClick={checkIn} disabled={!!today?.check_in}>Check In</button>
          <button className="btn btn-primary" onClick={checkOut} disabled={!today?.check_in || !!today?.check_out}>Check Out</button>
          <button className="btn btn-ghost" onClick={() => setShow(!show)}>Request correction</button>
        </div>
        {show && (
          <form onSubmit={submitCorr} style={{ marginTop: 16 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
              <div><label className="label">Date</label>
                <input className="input" type="date" required value={f.date}
                  onChange={e => setF({ ...f, date: e.target.value })} /></div>
              <div><label className="label">Requested In</label>
                <input className="input" type="datetime-local" value={f.requested_check_in}
                  onChange={e => setF({ ...f, requested_check_in: e.target.value })} /></div>
              <div><label className="label">Requested Out</label>
                <input className="input" type="datetime-local" value={f.requested_check_out}
                  onChange={e => setF({ ...f, requested_check_out: e.target.value })} /></div>
            </div>
            <label className="label">Reason</label>
            <input className="input" required value={f.reason}
              onChange={e => setF({ ...f, reason: e.target.value })} />
            <button className="btn btn-primary">Submit</button>
          </form>
        )}
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>Calendar</h3>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-ghost" onClick={() => setYm(ym.m === 1 ? { y: ym.y - 1, m: 12 } : { y: ym.y, m: ym.m - 1 })}>←</button>
            <span style={{ padding: '8px 12px' }}>{ym.y}-{String(ym.m).padStart(2, '0')}</span>
            <button className="btn btn-ghost" onClick={() => setYm(ym.m === 12 ? { y: ym.y + 1, m: 1 } : { y: ym.y, m: ym.m + 1 })}>→</button>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4, marginTop: 12 }}>
          {cal.map(c => (
            <div key={c.date} title={`${c.date} · ${c.status || '—'}${c.worked_minutes ? ' · ' + c.worked_minutes + ' min' : ''}`}
              style={{ padding: 8, borderRadius: 4, fontSize: 12, minHeight: 50,
                background: STATUS_COLOR[c.status] || '#e5e7eb', color: c.status ? 'white' : '#111827' }}>
              <div style={{ fontWeight: 700 }}>{c.date.split('-')[2]}</div>
              <div style={{ fontSize: 10 }}>{c.status || '—'}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h3>My corrections</h3>
        <table className="table">
          <thead><tr><th>Date</th><th>Reason</th><th>Status</th></tr></thead>
          <tbody>
            {corrs.map(c => <tr key={c.id}><td>{c.date}</td><td>{c.reason}</td><td>{c.status}</td></tr>)}
            {corrs.length === 0 && <tr><td colSpan="3" style={{ color: 'var(--text-muted)' }}>None yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}