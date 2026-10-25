import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../api/client'
export default function Employee360() {
  const { id } = useParams()
  const [p, setP] = useState(null)
  const [err, setErr] = useState('')
  useEffect(() => {
    api.get(`/employees/${id}`).then(r => setP(r.data)).catch(() => setErr('Not found'))
  }, [id])
  if (!p) return <div className="card">{err || 'Loading…'}</div>
  const row = (k, v) => <tr><td style={{ width: 200, color: 'var(--text-muted)' }}>{k}</td><td>{v ?? '—'}</td></tr>
  return (
    <div>
      <h1>{p.name}</h1>
      <div className="card">
        <table className="table">
          <tbody>
            {row('Employee code', p.employee_code)}
            {row('Email', p.email)}
            {row('Department', p.department)}
            {row('Designation', p.designation)}
            {row('Date of joining', p.date_of_joining)}
            {row('Days with company', p.joined_days)}
            {row('Basic salary', p.basic_salary)}
            {row('Phone', p.phone)}
            {row('Address', p.address)}
            {row('Status', p.status)}
          </tbody>
        </table>
      </div>
    </div>
  )
}