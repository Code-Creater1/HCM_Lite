import { useEffect, useState } from 'react'
import { Routes, Route, Navigate, useNavigate, NavLink } from 'react-router-dom'
import api from './api/client'
import { useAuth } from './store/auth'
import Setup from './pages/Setup'
import Login from './pages/Login'
import ChangePassword from './pages/ChangePassword'
import Dashboard from './pages/Dashboard'
import AdminHRLogins from './pages/AdminHRLogins'
import HRSEmployees from './pages/HREmployees'
import MyProfile from './pages/MyProfile'
import CompanySettings from './pages/CompanySettings'
import Departments from './pages/Departments'
import Designations from './pages/Designations'
import LeaveTypes from './pages/LeaveTypes'
import Holidays from './pages/Holidays'
import CSVImport from './pages/CSVImport'
import Employee360 from './pages/Employee360'

const MENUS = {
  ADMIN: [
    { label: 'Dashboard', path: '/' },
    { label: 'Company Settings', path: '/admin/settings' },
    { label: 'Departments', path: '/admin/departments' },
    { label: 'Designations', path: '/admin/designations' },
    { label: 'Leave Types', path: '/admin/leave-types' },
    { label: 'Holidays', path: '/admin/holidays' },
    { label: 'HR Logins', path: '/admin/hr-logins' },
    { label: 'All Employees', path: '/admin/employees' },
  ],
  HR: [
    { label: 'Dashboard', path: '/' },
    { label: 'Employees', path: '/hr/employees' },
    { label: 'Bulk Import', path: '/hr/import' },
  ],
  EMPLOYEE: [
    { label: 'Dashboard', path: '/' },
    { label: 'My Profile', path: '/me/profile' },
  ],
}

export default function App() {
  const [checked, setChecked] = useState(false)
  const [setupDone, setSetupDone] = useState(true)
  const { user } = useAuth()

  useEffect(() => {
    api.get('/setup/status')
      .then(r => setSetupDone(r.data.setup_completed))
      .catch(() => setSetupDone(true))
      .finally(() => setChecked(true))
  }, [])

  if (!checked) return <div style={{ padding: 40 }}>Loading…</div>

  return (
    <Routes>
      <Route path="/setup" element={
        setupDone ? <Navigate to="/login" />
          : <Setup onDone={() => setSetupDone(true)} />} />
      <Route path="/login" element={
        !setupDone ? <Navigate to="/setup" />
          : user ? <Navigate to="/" /> : <Login />} />
      <Route path="/change-password" element={
        !user ? <Navigate to="/login" /> : <ChangePassword />} />
      <Route path="/*" element={
        !user ? <Navigate to="/login" />
          : user.must_change_password ? <Navigate to="/change-password" />
            : <Shell />} />
    </Routes>
  )
}

function Shell() {
  const { user, logout } = useAuth()
  const nav = useNavigate()
  const menus = MENUS[user.role] || []

  return (
    <div className="layout">
      <aside className="sidebar">
        <div style={{ padding: '0 20px 16px', fontSize: 16, fontWeight: 800 }}>
          HCM Lite
        </div>
        {menus.map(i => (
          <NavLink key={i.path} to={i.path}
            className={({ isActive }) => isActive ? 'active' : ''}>{i.label}</NavLink>
        ))}
        <div style={{ padding: 20 }}>
          <button className="btn btn-ghost" onClick={() => { logout(); nav('/login') }}>
            Logout
          </button>
        </div>
      </aside>

      <div className="main">
        <div className="topbar">
          <h2>{user.name}<span className="role-badge">{user.role}</span></h2>
        </div>
        <div className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />

            {user.role === 'ADMIN' && (
              <>
                <Route path="/admin/settings" element={<CompanySettings />} />
                <Route path="/admin/departments" element={<Departments />} />
                <Route path="/admin/designations" element={<Designations />} />
                <Route path="/admin/leave-types" element={<LeaveTypes />} />
                <Route path="/admin/holidays" element={<Holidays />} />
                <Route path="/admin/hr-logins" element={<AdminHRLogins />} />
                <Route path="/admin/employees" element={<HRSEmployees />} />
                <Route path="/admin/employees/:id" element={<Employee360 />} />
              </>
            )}

            {user.role === 'HR' && (
              <>
                <Route path="/hr/employees" element={<HRSEmployees />} />
                <Route path="/hr/employees/:id" element={<Employee360 />} />
                <Route path="/hr/import" element={<CSVImport />} />
              </>
            )}

            {user.role === 'EMPLOYEE' && (
              <Route path="/me/profile" element={<MyProfile />} />
            )}

            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </div>
    </div>
  )
}