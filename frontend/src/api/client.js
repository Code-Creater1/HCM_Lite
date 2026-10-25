import axios from 'axios'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const api = axios.create({ baseURL: API })

api.interceptors.request.use((c) => {
  const t = localStorage.getItem('token')
  if (t) c.headers.Authorization = `Bearer ${t}`
  return c
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      const p = window.location.pathname
      if (p !== '/login' && p !== '/setup') window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api