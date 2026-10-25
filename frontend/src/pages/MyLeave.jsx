import { useEffect, useState } from 'react'
import api from '../api/client'

export default function MyLeave() {
  const [balance, setBalance] = useState([])
  const [types, setTypes] = useState([])
  const [history, setHistory] = useState([])
  const [f, setF] = useState({ leave_type_id: '', start_date: '', end_date: '', reason: '' })
  const [msg, setMsg] = useState(''); const [err, setErr] = useState('')

  const load = async () => {
    const [b, t, h] = await Promise.all([
      api.get('/leave/balance/me'), api.get('/leave/types'), api.get('/leave/me')])
    setBalance(b.data); setTypes(t.data); setHistory(h.data)
  }
  useEffect(() => { load() }, [])

  const submit = async (e) => {
    e.preventDefault(); setErr(''); setMsg('')
    try {
      const { data } = await api.post('/leave/apply',
        { ...f, leave_type_id: Number(f.leave_type_id) })
      setMsg(`Applied: ${data.days} working days, status ${data.status}.`)
      setF({ leave_type_id: '', start_date: '', end_date: '', reason: '' }); load()
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }
  const cancel = async (id) => {
    if (!confirm('Cancel this leave?')) return
    try { await api.post(`/leave/${id}/cancel`); setMsg('Cancelled.'); load() }
    catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }
  const typeName = (id) => types.find(t => t.id === id)?.name || '—'

  return (
    <div>
      <h1>My Leave</h1>
      {err && <div className="error">{err}</div>}
      {msg && <div className="success">{msg}</div>}

      <div className="card" style={{ marginBottom: 20 }}>
        <h3>Balance</h3>
        <table className="table">
          <thead><tr><th>Type</th><th>Quota</th><th>Used</th><th>Remaining</th><th>Paid</th></tr></thead>
          <tbody>
            {balance.map(b => (
              <tr key={b.leave_type_id}>
                <td>{b.name}</td>
                <td>{b.quota === 0 ? '∞' : b.quota}</td>
                <td>{b.used}</td>
                <td>{b.remaining === null ? '∞' : b.remaining}</td>
                <td>{b.is_paid ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <h3>Apply</h3>
        <form onSubmit={submit}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
            <div><label className="label">Type</label>
              <select className="input" required value={f.leave_type_id}
                onChange={e => setF({ ...f, leave_type_id: e.target.value })}>
                <option value="">-- select --</option>
                {types.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select></div>
            <div><label className="label">Start</label>
              <input className="input" type="date" required value={f.start_date}
                onChange={e => setF({ ...f, start_date: e.target.value })} /></div>
            <div><label className="label">End</label>
              <input className="input" type="date" required value={f.end_date}
                onChange={e => setF({ ...f, end_date: e.target.value })} /></div>
          </div>
          <label className="label">Reason</label>
          <input className="input" required value={f.reason}
            onChange={e => setF({ ...f, reason: e.target.value })} />
          <button className="btn btn-primary">Apply</button>
        </form>
      </div>

      <div className="card">
        <h3>History</h3>
        <table className="table">
          <thead><tr><th>Type</th><th>From</th><th>To</th><th>Days</th><th>Status</th><th>Comment</th><th></th></tr></thead>
          <tbody>
            {history.map(lv => (
              <tr key={lv.id}>
                <td>{typeName(lv.leave_type_id)}</td>
                <td>{lv.start_date}</td><td>{lv.end_date}</td><td>{lv.days}</td>
                <td>{lv.status}</td><td>{lv.review_comment || '—'}</td>
                <td>{(lv.status === 'pending' || lv.status === 'approved') && (
                  <button className="btn btn-ghost" style={{ padding: '4px 10px' }}
                    onClick={() => cancel(lv.id)}>Cancel</button>)}</td>
              </tr>
            ))}
            {history.length === 0 && <tr><td colSpan="7" style={{ color: 'var(--text-muted)' }}>No requests yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}