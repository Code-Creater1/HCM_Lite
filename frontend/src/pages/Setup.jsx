import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../store/auth'

export default function Setup({ onDone }) {
  const nav = useNavigate(); const { login } = useAuth()
  const [f, setF] = useState({ company_name: '', admin_name: '', admin_email: '', admin_password: '' })
  const [err, setErr] = useState(''); const [busy, setBusy] = useState(false)
  const submit = async (e) => {
    e.preventDefault(); setBusy(true); setErr('')
    try {
      const { data } = await api.post('/setup', f)
      login(data); onDone(); nav('/')
    } catch (e) { setErr(e.response?.data?.detail || 'Setup failed') }
    finally { setBusy(false) }
  }
  return (
    <div className="container" style={{ maxWidth: 480, marginTop: 60 }}>
      <div className="card">
        <h1>First-Run Setup</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: 20 }}>
          Create the company and initial Admin. This screen disappears afterwards.
        </p>
        {err && <div className="error">{err}</div>}
        <form onSubmit={submit}>
          <label className="label">Company Name</label>
          <input className="input" required minLength={2}
            value={f.company_name} onChange={e => setF({ ...f, company_name: e.target.value })} />
          <label className="label">Admin Name</label>
          <input className="input" required minLength={2}
            value={f.admin_name} onChange={e => setF({ ...f, admin_name: e.target.value })} />
          <label className="label">Admin Email</label>
          <input className="input" type="email" required
            value={f.admin_email} onChange={e => setF({ ...f, admin_email: e.target.value })} />
          <label className="label">Admin Password (min 8)</label>
          <input className="input" type="password" required minLength={8}
            value={f.admin_password} onChange={e => setF({ ...f, admin_password: e.target.value })} />
          <button className="btn btn-primary" disabled={busy} style={{ width: '100%' }}>
            {busy ? 'Creating…' : 'Create Company & Sign In'}
          </button>
        </form>
      </div>
    </div>
  )
}