import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../store/auth'

const BLANK = {
  name: '', email: '', employee_code: '', department: '', designation: '',
  date_of_joining: '', basic_salary: '', phone: '', address: '', temporary_password: '',
}

export default function HRSEmployees() {
  const { user } = useAuth()
  const [list, setList] = useState([])
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [f, setF] = useState(BLANK)

  const load = () =>
    api.get('/employees', { params: { search, page: 1, size: 50 } })
      .then(r => { setList(r.data.items); setTotal(r.data.total) })
  useEffect(() => { load() }, [])

  const submit = async (e) => {
    e.preventDefault(); setErr(''); setMsg('')
    try {
      await api.post('/employees', { ...f, basic_salary: Number(f.basic_salary) })
      setMsg('Employee registered. Share temp password securely; they must change it on first sign-in.')
      setShowForm(false); setF(BLANK); load()
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
  }

  const exportCsv = async () => {
    try {
      const r = await api.get('/employees/export.csv', { responseType: 'blob' })
      const a = document.createElement('a')
      a.href = URL.createObjectURL(r.data)
      a.download = 'employees.csv'
      a.click()
      URL.revokeObjectURL(a.href)
    } catch (e) { setErr(e.response?.data?.detail || 'Export failed') }
  }

  const viewPath = (id) =>
    user.role === 'ADMIN' ? `/admin/employees/${id}` : `/hr/employees/${id}`

  return (
    <div>
      <h1>{user.role === 'HR' ? 'Employees' : 'All Employees'}</h1>
      {err && <div className="error">{err}</div>}
      {msg && <div className="success">{msg}</div>}

      {user.role === 'HR' && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
              {showForm ? 'Cancel' : '+ Register employee'}
            </button>
            <button className="btn btn-ghost" onClick={exportCsv}>Export CSV</button>
          </div>

          {showForm && (
            <form onSubmit={submit} style={{ marginTop: 16 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div><label className="label">Name</label>
                  <input className="input" required value={f.name}
                    onChange={e => setF({ ...f, name: e.target.value })} /></div>
                <div><label className="label">Email</label>
                  <input className="input" type="email" required value={f.email}
                    onChange={e => setF({ ...f, email: e.target.value })} /></div>
                <div><label className="label">Employee Code</label>
                  <input className="input" required value={f.employee_code}
                    onChange={e => setF({ ...f, employee_code: e.target.value })} /></div>
                <div><label className="label">Department</label>
                  <input className="input" value={f.department}
                    onChange={e => setF({ ...f, department: e.target.value })} /></div>
                <div><label className="label">Designation</label>
                  <input className="input" value={f.designation}
                    onChange={e => setF({ ...f, designation: e.target.value })} /></div>
                <div><label className="label">Joining Date</label>
                  <input className="input" type="date" required value={f.date_of_joining}
                    onChange={e => setF({ ...f, date_of_joining: e.target.value })} /></div>
                <div><label className="label">Basic Salary</label>
                  <input className="input" type="number" step="0.01" required
                    value={f.basic_salary}
                    onChange={e => setF({ ...f, basic_salary: e.target.value })} /></div>
                <div><label className="label">Phone</label>
                  <input className="input" value={f.phone}
                    onChange={e => setF({ ...f, phone: e.target.value })} /></div>
                <div style={{ gridColumn: '1/-1' }}><label className="label">Address</label>
                  <input className="input" value={f.address}
                    onChange={e => setF({ ...f, address: e.target.value })} /></div>
                <div style={{ gridColumn: '1/-1' }}>
                  <label className="label">Temporary Password (min 8)</label>
                  <input className="input" required minLength={8}
                    value={f.temporary_password}
                    onChange={e => setF({ ...f, temporary_password: e.target.value })} /></div>
              </div>
              <button className="btn btn-primary" style={{ marginTop: 8 }}>Register</button>
            </form>
          )}
        </div>
      )}

      <div className="card">
        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
          <input className="input" placeholder="Search name / email / code"
            value={search} onChange={e => setSearch(e.target.value)}
            style={{ marginBottom: 0 }} />
          <button className="btn btn-ghost" onClick={load}>Search</button>
          {user.role === 'ADMIN' && (
            <button className="btn btn-ghost" onClick={exportCsv}>Export CSV</button>
          )}
        </div>
        <div style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 8 }}>
          {total} employees
        </div>
        <table className="table">
          <thead>
            <tr>
              <th>Code</th><th>Name</th><th>Email</th><th>Dept</th>
              <th>Designation</th><th>Joined</th><th>Basic</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {list.map(e => (
              <tr key={e.id}>
                <td>{e.employee_code}</td>
                <td>{e.name}</td>
                <td>{e.email}</td>
                <td>{e.department || '—'}</td>
                <td>{e.designation || '—'}</td>
                <td>{e.date_of_joining}</td>
                <td>{e.basic_salary}</td>
                <td>
                  <Link to={viewPath(e.id)}
                    className="btn btn-ghost"
                    style={{ padding: '4px 10px' }}>View</Link>
                </td>
              </tr>
            ))}
            {list.length === 0 && (
              <tr><td colSpan="8" style={{ color: 'var(--text-muted)' }}>
                No employees yet.
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}