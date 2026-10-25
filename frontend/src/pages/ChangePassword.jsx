import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../store/auth'

export default function ChangePassword() {
  const nav = useNavigate(); const { setMustChange } = useAuth()
  const [f, setF] = useState({ current_password: '', new_password: '' })
  const [err, setErr] = useState(''); const [busy, setBusy] = useState(false)
  const submit = async (e) => {
    e.preventDefault(); setBusy(true); setErr('')
    try {
      await api.post('/auth/change-password', f)
      setMustChange(false); nav('/')
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
    finally { setBusy(false) }
  }
  return (
    <div className="container" style={{ maxWidth: 400, marginTop: 80 }}>
      <div className="card">
        <h1>Change password</h1>
        <p style={{ color: 'var(--text-muted)' }}>Temporary passwords must be changed before continuing.</p>
        {err && <div className="error">{err}</div>}
        <form onSubmit={submit}>
          <label className="label">Current password</label>
          <input className="input" type="password" required
            onChange={e => setF({ ...f, current_password: e.target.value })} />
          <label className="label">New password (min 8)</label>
          <input className="input" type="password" required minLength={8}
            onChange={e => setF({ ...f, new_password: e.target.value })} />
          <button className="btn btn-primary" disabled={busy} style={{ width: '100%' }}>
            {busy ? 'Updating…' : 'Update password'}
          </button>
        </form>
      </div>
    </div>
  )
}