import { useEffect, useState } from 'react'
import api from '../api/client'

export default function SimpleCrud({ title, endpoint, fields, columns }) {
  const [rows, setRows] = useState([])
  const [f, setF] = useState({})
  const [editingId, setEditingId] = useState(null)
  const [err, setErr] = useState('')
  const [msg, setMsg] = useState('')

  const load = () => api.get(endpoint).then(r => setRows(r.data)).catch(() => {})
  useEffect(() => { load() }, [endpoint])

  const submit = async (e) => {
    e.preventDefault(); setErr(''); setMsg('')
    try {
      if (editingId) await api.patch(`${endpoint}/${editingId}`, f)
      else await api.post(endpoint, f)
      setMsg(editingId ? 'Updated.' : 'Created.')
      setF({}); setEditingId(null); load()
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }

  const remove = async (id) => {
    if (!confirm('Delete this row?')) return
    try { await api.delete(`${endpoint}/${id}`); setMsg('Deleted.'); load() }
    catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }

  const edit = (row) => {
    setEditingId(row.id)
    const draft = {}
    fields.forEach(fld => { draft[fld.name] = row[fld.name] ?? '' })
    setF(draft)
  }

  return (
    <div>
      <h1>{title}</h1>
      {err && <div className="error">{err}</div>}
      {msg && <div className="success">{msg}</div>}

      <div className="card" style={{ marginBottom: 20 }}>
        <form onSubmit={submit}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: 12,
          }}>
            {fields.map(fld => (
              <div key={fld.name}>
                <label className="label">{fld.label}</label>
                <input className="input"
                  type={fld.type || 'text'}
                  required={fld.required}
                  value={f[fld.name] ?? ''}
                  onChange={e => setF({
                    ...f,
                    [fld.name]: fld.type === 'number'
                      ? Number(e.target.value)
                      : e.target.value,
                  })} />
              </div>
            ))}
          </div>
          <div style={{ marginTop: 12 }}>
            <button className="btn btn-primary">
              {editingId ? 'Save changes' : `Add ${title.slice(0, -1)}`}
            </button>
            {editingId && (
              <button type="button" className="btn btn-ghost"
                style={{ marginLeft: 8 }}
                onClick={() => { setEditingId(null); setF({}) }}>
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              {columns.map(c => <th key={c.name}>{c.label}</th>)}
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.id}>
                {columns.map(c => <td key={c.name}>{String(r[c.name] ?? '')}</td>)}
                <td>
                  <button className="btn btn-ghost"
                    style={{ padding: '4px 10px', marginRight: 6 }}
                    onClick={() => edit(r)}>Edit</button>
                  <button className="btn btn-ghost"
                    style={{ padding: '4px 10px', color: 'var(--danger)' }}
                    onClick={() => remove(r.id)}>Delete</button>
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr><td colSpan={columns.length + 1}
                style={{ color: 'var(--text-muted)' }}>No rows yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}