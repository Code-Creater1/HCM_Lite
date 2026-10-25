import { useEffect, useState } from 'react'
import api from '../api/client'
export default function CompanySettings() {
  const [s, setS] = useState(null)
  const [err, setErr] = useState(''); const [msg, setMsg] = useState('')
  useEffect(() => { api.get('/org/settings').then(r => setS(r.data)).catch(() => setErr('Cannot load')) }, [])
  const save = async (e) => {
    e.preventDefault(); setErr(''); setMsg('')
    try {
      await api.patch('/org/settings', s)
      setMsg('Saved. Rules apply to new records only.')
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }
  if (!s) return <div className="card">{err || 'Loading…'}</div>
  const set = (k, v) => setS({ ...s, [k]: v })
  return (
    <div>
      <h1>Company Settings</h1>
      {err && <div className="error">{err}</div>}
      {msg && <div className="success">{msg}</div>}
      <form className="card" onSubmit={save}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 12 }}>
          <div><label className="label">Company name</label>
            <input className="input" value={s.company_name} onChange={e => set('company_name', e.target.value)} /></div>
          <div><label className="label">Office start (HH:MM)</label>
            <input className="input" value={s.office_start} onChange={e => set('office_start', e.target.value)} /></div>
          <div><label className="label">Grace minutes</label>
            <input className="input" type="number" value={s.grace_minutes} onChange={e => set('grace_minutes', Number(e.target.value))} /></div>
          <div><label className="label">Half day (hours)</label>
            <input className="input" type="number" step="0.5" value={s.half_day_hours} onChange={e => set('half_day_hours', Number(e.target.value))} /></div>
          <div><label className="label">Weekend (comma list)</label>
            <input className="input" value={s.weekend} onChange={e => set('weekend', e.target.value)} /></div>
          <div><label className="label">Office lat</label>
            <input className="input" type="number" step="any" value={s.office_lat ?? ''} onChange={e => set('office_lat', e.target.value === '' ? null : Number(e.target.value))} /></div>
          <div><label className="label">Office lng</label>
            <input className="input" type="number" step="any" value={s.office_lng ?? ''} onChange={e => set('office_lng', e.target.value === '' ? null : Number(e.target.value))} /></div>
          <div><label className="label">Radius (m)</label>
            <input className="input" type="number" value={s.office_radius_m} onChange={e => set('office_radius_m', Number(e.target.value))} /></div>
        </div>
        <button className="btn btn-primary" style={{ marginTop: 16 }}>Save settings</button>
      </form>
    </div>
  )
}