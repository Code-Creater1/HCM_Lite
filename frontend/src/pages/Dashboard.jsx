import { useAuth } from '../store/auth'
export default function Dashboard() {
  const { user } = useAuth()
  return (
    <div>
      <h1>Welcome, {user.name}</h1>
      <div className="card">
        <h3>Your role: {user.role}</h3>
        <p style={{ color: 'var(--text-muted)' }}>
          Role-scoped KPIs will populate here as the M4–M9 modules are wired. All figures come from the
          server, aggregated from records created in the app.
        </p>
      </div>
    </div>
  )
}