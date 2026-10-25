import { useEffect, useState } from 'react'
import api from '../api/client'
export default function AdminHRLogins() {
  const [list, setList] = useState([])
  const [f, setF] = useState({ name: '', email: '', temporary_password: '' })
  const [msg, setMsg] = useState(''); const [err, setErr] = useState('')
  const load = () => api.get('/users/hr').then(r => setList(r.data))
  useEffect(() => { load() }, [])
  const submit = async (e) => {
    e.preventDefault(); setErr(''); setMsg('')
    try {
      await api.post('/users/hr', f)
      setMsg('HR login created. Share the temporary password securely.')
      setF({ name: '', email: '', temporary_password: '' }); load()
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }
  return (
    <div>
      <h1>HR Logins</h1>
      <div className="card" style={{ marginBottom: 20 }}>
        <h3>Create HR login</h3>
        {err && <div className="error">{err}</div>}
        {msg && <div className="success">{msg}</div>}
        <form onSubmit={submit}>
          <label className="label">Name</label>
          <input className="input" required value={f.name} onChange={e => setF({ ...f, name: e.target.value })} />
          <label className="label">Email</label>
          <input className="input" type="email" required value={f.email} onChange={e => setF({ ...f, email: e.target.value })} />
          <label className="label">Temporary password (min 8)</label>
          <input className="input" required minLength={8} value={f.temporary_password} onChange={e => setF({ ...f, temporary_password: e.target.value })} />
          <button className="btn btn-primary">Create HR login</button>
        </form>
      </div>
      <div className="card">
        <h3>Admins & HR</h3>
        <table className="table">
          <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Active</th></tr></thead>
          <tbody>
            {list.map(u => <tr key={u.id}><td>{u.name}</td><td>{u.email}</td>
              <td>{u.role}</td><td>{u.is_active ? 'Yes' : 'No'}</td></tr>)}
          </tbody>
        </table>
      </div>
    </div>
  )
}