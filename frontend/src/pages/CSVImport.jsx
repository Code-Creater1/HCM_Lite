import { useState } from 'react'
import api from '../api/client'
export default function CSVImport() {
  const [file, setFile] = useState(null)
  const [report, setReport] = useState(null)
  const [err, setErr] = useState(''); const [msg, setMsg] = useState('')
  const [busy, setBusy] = useState(false)

  const dry = async () => {
    if (!file) return
    setBusy(true); setErr(''); setMsg(''); setReport(null)
    try {
      const fd = new FormData(); fd.append('file', file)
      const { data } = await api.post('/employees/import/dry-run', fd)
      setReport(data)
    } catch (e) { setErr(e.response?.data?.detail || 'Failed') }
    finally { setBusy(false) }
  }
  const commit = async () => {
    if (!file) return
    setBusy(true); setErr(''); setMsg('')
    try {
      const fd = new FormData(); fd.append('file', file)
      const { data } = await api.post('/employees/import/commit', fd)
      setMsg(`Imported ${data.created} employees. Each has a temporary password — share securely.`)
      setReport(null)
    } catch (e) {
      const d = e.response?.data?.detail
      if (d && typeof d === 'object') { setReport(d); setErr('') }
      else setErr(e.response?.data?.detail || 'Failed')
    } finally { setBusy(false) }
  }
  const downloadSample = () => {
    const csv = [
      'name,email,employee_code,department,designation,date_of_joining,basic_salary,temporary_password,phone,address',
      'Jane Doe,jane@example.com,EMP001,Engineering,Engineer,2026-01-15,80000,TempPass123,,',
    ].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob); a.download = 'employees_sample.csv'; a.click()
  }

  return (
    <div>
      <h1>Bulk Import Employees</h1>
      {err && <div className="error">{err}</div>}
      {msg && <div className="success">{msg}</div>}
      <div className="card">
        <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
          Upload a CSV, dry-run first to see errors before committing.
        </p>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 12 }}>
          <input type="file" accept=".csv" onChange={e => setFile(e.target.files[0])} />
          <button className="btn btn-ghost" onClick={downloadSample}>Download sample</button>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-ghost" onClick={dry} disabled={!file || busy}>Dry run</button>
          <button className="btn btn-primary" onClick={commit} disabled={!file || busy}>Commit import</button>
        </div>
      </div>

      {report && (
        <div className="card" style={{ marginTop: 16 }}>
          <h3>Dry-run report</h3>
          <p><b>Total:</b> {report.rows_total} · <b>OK:</b> {report.rows_ok} · <b>Errors:</b> {report.rows_error}</p>
          {report.errors?.length > 0 && (
            <table className="table" style={{ marginTop: 12 }}>
              <thead><tr><th>Row</th><th>Field</th><th>Reason</th></tr></thead>
              <tbody>
                {report.errors.map((e, i) => (
                  <tr key={i}><td>{e.row}</td><td>{e.field}</td><td>{e.reason}</td></tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}