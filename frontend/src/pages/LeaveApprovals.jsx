import { useEffect, useState } from 'react'
import api from '../api/client'

export default function LeaveApprovals() {
  const [items, setItems] = useState([])
  const [filter, setFilter] = useState('pending')
  const [comment, setComment] = useState({})
  const [msg, setMsg] = useState(''); const [err, setErr] = useState('')

  const load = async () => {
    const { data } = await api.get('/leave/inbox', { params: filter ? { status: filter } : {} })
    setItems(data)
  }
  useEffect(() => { load() }, [filter])

  const review = async (id, action) => {
    setErr(''); setMsg('')
    try {
      await api.post(`/leave/${id}/review`, { action, comment: comment[id] || '' })
      setMsg(`Leave ${action}d.`); load()
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }

  return (
    <div>
      <h1>Leave Approvals</h1>
      {err && <div className="error">{err}</div>}
      {msg && <div className="success">{msg}</div>}
      <div className="card">
        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
          {['pending', 'approved', 'rejected', 'cancelled', ''].map(s => (
            <button key={s || 'all'}
              className={`btn ${filter === s ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setFilter(s)}>{s || 'All'}</button>
          ))}
        </div>
        <table className="table">
          <thead><tr><th>Employee</th><th>Type</th><th>From</th><th>To</th>
            <th>Days</th><th>Reason</th><th>Status</th><th>Action</th></tr></thead>
          <tbody>
            {items.map(lv => (
              <tr key={lv.id}>
                <td>{lv.employee_name || lv.employee_id}</td>
                <td>{lv.leave_type_name || lv.leave_type_id}</td>
                <td>{lv.start_date}</td><td>{lv.end_date}</td><td>{lv.days}</td>
                <td>{lv.reason}</td><td>{lv.status}</td>
                <td>{lv.status === 'pending' && (
                  <>
                    <input className="input" placeholder="comment"
                      value={comment[lv.id] || ''}
                      onChange={e => setComment({ ...comment, [lv.id]: e.target.value })}
                      style={{ marginBottom: 4, fontSize: 12 }} />
                    <button className="btn btn-primary" style={{ padding: '4px 10px', marginRight: 4 }}
                      onClick={() => review(lv.id, 'approve')}>Approve</button>
                    <button className="btn btn-ghost" style={{ padding: '4px 10px' }}
                      onClick={() => review(lv.id, 'reject')}>Reject</button>
                  </>
                )}</td>
              </tr>
            ))}
            {items.length === 0 && <tr><td colSpan="8" style={{ color: 'var(--text-muted)' }}>None.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}