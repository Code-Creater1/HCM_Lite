import { useEffect, useState } from 'react'
import api from '../api/client'

const BLANK = { name: '', code: '', yearly_quota: 0, is_paid: true }

export default function LeaveTypes() {
  const [rows, setRows] = useState([])
  const [f, setF] = useState(BLANK)
  const [err, setErr] = useState('')
  const [msg, setMsg] = useState('')

  const load = () => api.get('/org/leave-types').then(r => setRows(r.data)).catch(() => {})
  useEffect(() => { load() }, [])

  const submit = async (e) => {
    e.preventDefault()
    setErr(''); setMsg('')
    try {
      await api.post('/org/leave-types', f)
      setMsg('Created.')
      setF(BLANK)
      load()
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }

  const remove = async (id) => {
    if (!confirm('Delete this leave type?')) return
    try { await api.delete(`/org/leave-types/${id}`); load() }
    catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }

  return (
    <div>
      <h1>Leave Types</h1>
      {err && <div className="error">{err}</div>}
      {msg && <div className="success">{msg}</div>}

      <div className="card" style={{ marginBottom: 20 }}>
        <form onSubmit={submit}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
            <div>
              <label className="label">Name</label>
              <input className="input" required value={f.name}
                onChange={e => setF({ ...f, name: e.target.value })} />
            </div>
            <div>
              <label className="label">Code</label>
              <input className="input" required value={f.code}
                onChange={e => setF({ ...f, code: e.target.value })} />
            </div>
            <div>
              <label className="label">Yearly quota (0 = ∞)</label>
              <input className="input" type="number" required value={f.yearly_quota}
                onChange={e => setF({ ...f, yearly_quota: Number(e.target.value) })} />
            </div>
            <div>
              <label className="label">Paid?</label>
              <select className="input" value={String(f.is_paid)}
                onChange={e => setF({ ...f, is_paid: e.target.value === 'true' })}>
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </div>
          </div>
          <div style={{ marginTop: 12 }}>
            <button className="btn btn-primary">Add Leave Type</button>
          </div>
        </form>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Name</th><th>Code</th><th>Quota</th><th>Paid</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.id}>
                <td>{r.name}</td>
                <td>{r.code}</td>
                <td>{r.yearly_quota === 0 ? '∞' : r.yearly_quota}</td>
                <td>{r.is_paid ? 'Yes' : 'No'}</td>
                <td>
                  <button className="btn btn-ghost"
                    style={{ padding: '4px 10px', color: 'var(--danger)' }}
                    onClick={() => remove(r.id)}>Delete</button>
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr><td colSpan="5" style={{ color: 'var(--text-muted)' }}>
                No leave types yet.
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}