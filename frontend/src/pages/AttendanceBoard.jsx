import { useEffect, useState } from 'react'
import api from '../api/client'

export default function AttendanceBoard() {
  const [board, setBoard] = useState([])
  const [corrs, setCorrs] = useState([])
  const [day, setDay] = useState(() => new Date().toISOString().slice(0, 10))
  const [comment, setComment] = useState({})
  const [msg, setMsg] = useState(''); const [err, setErr] = useState('')

  const load = async () => {
    const [b, c] = await Promise.all([
      api.get('/attendance/board', { params: { date: day } }),
      api.get('/attendance/corrections', { params: { status: 'pending' } }),
    ])
    setBoard(b.data); setCorrs(c.data)
  }
  useEffect(() => { load() }, [day])

  const review = async (id, action) => {
    setErr(''); setMsg('')
    try {
      await api.post(`/attendance/corrections/${id}/review`,
        { action, comment: comment[id] || '' })
      setMsg(`Correction ${action}d.`); load()
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }

  return (
    <div>
      <h1>Attendance Board</h1>
      {err && <div className="error">{err}</div>}
      {msg && <div className="success">{msg}</div>}

      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 12 }}>
          <label className="label" style={{ margin: 0 }}>Date</label>
          <input className="input" type="date" value={day}
            onChange={e => setDay(e.target.value)} style={{ marginBottom: 0 }} />
          <button className="btn btn-ghost" onClick={load}>Refresh</button>
        </div>
        <table className="table">
          <thead><tr><th>Code</th><th>Name</th><th>Dept</th><th>Status</th>
            <th>In</th><th>Out</th><th>Worked</th></tr></thead>
          <tbody>
            {board.map(r => (
              <tr key={r.employee_id}>
                <td>{r.employee_code}</td><td>{r.name}</td>
                <td>{r.department || '—'}</td><td><b>{r.status || '—'}</b></td>
                <td>{r.check_in ? new Date(r.check_in).toLocaleTimeString() : '—'}</td>
                <td>{r.check_out ? new Date(r.check_out).toLocaleTimeString() : '—'}</td>
                <td>{r.worked_minutes ? (Math.round(r.worked_minutes / 6) / 10) + 'h' : '—'}</td>
              </tr>
            ))}
            {board.length === 0 && <tr><td colSpan="7" style={{ color: 'var(--text-muted)' }}>No employees.</td></tr>}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Pending corrections</h3>
        <table className="table">
          <thead><tr><th>Employee</th><th>Date</th><th>In</th><th>Out</th><th>Reason</th><th>Action</th></tr></thead>
          <tbody>
            {corrs.map(c => (
              <tr key={c.id}>
                <td>{c.employee_name || c.employee_id}</td>
                <td>{c.date}</td>
                <td>{c.requested_check_in ? new Date(c.requested_check_in).toLocaleString() : '—'}</td>
                <td>{c.requested_check_out ? new Date(c.requested_check_out).toLocaleString() : '—'}</td>
                <td>{c.reason}</td>
                <td>
                  <input className="input" placeholder="comment" value={comment[c.id] || ''}
                    onChange={e => setComment({ ...comment, [c.id]: e.target.value })}
                    style={{ marginBottom: 4, fontSize: 12 }} />
                  <button className="btn btn-primary" style={{ padding: '4px 10px', marginRight: 4 }}
                    onClick={() => review(c.id, 'approve')}>Approve</button>
                  <button className="btn btn-ghost" style={{ padding: '4px 10px' }}
                    onClick={() => review(c.id, 'reject')}>Reject</button>
                </td>
              </tr>
            ))}
            {corrs.length === 0 && <tr><td colSpan="6" style={{ color: 'var(--text-muted)' }}>None.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}