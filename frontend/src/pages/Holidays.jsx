import { useEffect, useState } from 'react'
import api from '../api/client'
export default function Holidays() {
  const [rows, setRows] = useState([])
  const [f, setF] = useState({ name: '', date: '' })
  const [err, setErr] = useState(''); const [msg, setMsg] = useState('')
  const load = () => api.get('/org/holidays').then(r => setRows(r.data))
  useEffect(() => { load() }, [])
  const submit = async (e) => {
    e.preventDefault(); setErr(''); setMsg('')
    try {
      await api.post('/org/holidays', f)
      setMsg('Added.'); setF({ name: '', date: '' }); load()
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }
  const remove = async (id) => {
    if (!confirm('Delete this holiday?')) return
    try { await api.delete(`/org/holidays/${id}`); load() }
    catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }
  return (
    <div>
      <h1>Public Holidays</h1>
      {err && <div className="error">{err}</div>}
      {msg && <div className="success">{msg}</div>}
      <div className="card" style={{ marginBottom: 20 }}>
        <form onSubmit={submit} style={{ display: 'flex', gap: 12, alignItems: 'flex-end' }}>
          <div style={{ flex: 2 }}>
            <label className="label">Holiday name</label>
            <input className="input" required value={f.name} onChange={e => setF({ ...f, name: e.target.value })} />
          </div>
          <div style={{ flex: 1 }}>
            <label className="label">Date</label>
            <input className="input" type="date" required value={f.date} onChange={e => setF({ ...f, date: e.target.value })} />
          </div>
          <button className="btn btn-primary" style={{ marginBottom: 12 }}>Add holiday</button>
        </form>
      </div>
      <div className="card">
        <table className="table">
          <thead><tr><th>Name</th><th>Date</th><th>Actions</th></tr></thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.id}>
                <td>{r.name}</td><td>{r.date}</td>
                <td><button className="btn btn-ghost" style={{ padding: '4px 10px', color: 'var(--danger)' }} onClick={() => remove(r.id)}>Delete</button></td>
              </tr>
            ))}
            {rows.length === 0 && <tr><td colSpan="3" style={{ color: 'var(--text-muted)' }}>No holidays yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}