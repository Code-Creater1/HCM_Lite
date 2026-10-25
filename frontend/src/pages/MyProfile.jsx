import { useEffect, useState } from 'react'
import api from '../api/client'

export default function MyProfile() {
  const [p, setP] = useState(null); const [msg, setMsg] = useState(''); const [err, setErr] = useState('')
  useEffect(() => { api.get('/employees/me').then(r => setP(r.data)).catch(() => setErr('Profile not found')) }, [])
  const save = async (e) => {
    e.preventDefault(); setErr(''); setMsg('')
    try {
      const { data } = await api.patch('/employees/me', { phone: p.phone, address: p.address })
      setP(data); setMsg('Saved.')
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }
  if (!p) return <div className="card">{err || 'Loading…'}</div>
  return (
    <div>
      <h1>My Profile</h1>
      {err && <div className="error">{err}</div>}
      {msg && <div className="success">{msg}</div>}
      <div className="card">
        <p><b>Name:</b> {p.name}</p><p><b>Email:</b> {p.email}</p>
        <p><b>Code:</b> {p.employee_code}</p>
        <p><b>Department:</b> {p.department || '—'}</p>
        <p><b>Designation:</b> {p.designation || '—'}</p>
        <p><b>Date of Joining:</b> {p.date_of_joining}</p>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          Salary, role and attendance are managed by HR/Admin and cannot be edited here.
        </p>
        <form onSubmit={save} style={{ marginTop: 16 }}>
          <label className="label">Phone</label>
          <input className="input" value={p.phone || ''} onChange={e => setP({ ...p, phone: e.target.value })} />
          <label className="label">Address</label>
          <input className="input" value={p.address || ''} onChange={e => setP({ ...p, address: e.target.value })} />
          <button className="btn btn-primary">Save phone & address</button>
        </form>
      </div>
    </div>
  )
}