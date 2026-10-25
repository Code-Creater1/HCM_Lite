import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../store/auth'

export default function Login() {
  const nav = useNavigate(); const { login } = useAuth()
  const [f, setF] = useState({ email: '', password: '' })
  const [err, setErr] = useState(''); const [busy, setBusy] = useState(false)
  const submit = async (e) => {
    e.preventDefault(); setBusy(true); setErr('')
    try {
      const { data } = await api.post('/auth/login', f)
      login(data); nav(data.must_change_password ? '/change-password' : '/')
    } catch (e) { setErr(e.response?.data?.detail || 'Login failed') }
    finally { setBusy(false) }
  }
  return (
    <div className="container" style={{ maxWidth: 400, marginTop: 80 }}>
      <div className="card">
        <h1>Sign in</h1>
        {err && <div className="error">{err}</div>}
        <form onSubmit={submit}>
          <label className="label">Email</label>
          <input className="input" type="email" required
            value={f.email} onChange={e => setF({ ...f, email: e.target.value })} />
          <label className="label">Password</label>
          <input className="input" type="password" required
            value={f.password} onChange={e => setF({ ...f, password: e.target.value })} />
          <button className="btn btn-primary" disabled={busy} style={{ width: '100%' }}>
            {busy ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}